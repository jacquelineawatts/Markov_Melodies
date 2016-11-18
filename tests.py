import unittest
from server import app
from model.model import connect_to_db, db
from flask import session
from logistic_regression import ItemSelector, predict


# class FlaskTests(unittest.TestCase):
#     """Integration tests for app."""

#     def setUp(self):

#         self.client = app.test_client()
#         app.config['TESTING'] = True
#         # What is this 'key' actually supposed to be? os.urandom(24)?
#         app.config['SECRET_KEY'] = 'key'
#         app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#         # with self.client as c:
#         #     with c.session_transaction() as sess:
#         #         sess['user_id'] = True



class FlaskTestsDatabase(unittest.TestCase):
    """Integration tests for pages requiring db and login."""

    def setUp(self):

        self.client = app.test_client()
        app.config['TESTING'] = True
        # What is this 'key' actually supposed to be? os.urandom(24)?
        app.config['SECRET_KEY'] = 'key'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 3
                sess['current_melody'] = {'wav_filepath': 'static/temp.wav',
                                          'genres': ['Classical'],
                                          'notes': (('e4', 32.0), ('f#4', 0.6666666666666666)),
                                          'is_major': True}

        connect_to_db(app, "postgresql:///testdb")
        # db.create_all()
        # load_seed_users_and_connections()

    def login(self, email, password):

        return self.client.post('/login', data=dict(
            email=email,
            password=password),
            follow_redirects=True)

    def logout(self):

        return self.client.get('logout', follow_redirects=True)

    def test_homepage(self):

        result = self.client.get('/')
        self.assertIn('Welcome', result.data)

    def test_results(self):

        print self.client
        result = self.client.post('/results', data=dict(
            note1='E4',
            note2='G4',
            length=5,
            mode='minor',
            genres='Celtic',
            ), follow_redirects=True)
        assert 'Resulting Melody' in result.data

    def test_login_logout(self):

        result = self.login('jacqui@test.org', 'test')
        print 'successful login', result
        assert "successfully logged in!" in result.data

        result = self.logout()
        print 'successful logout', result
        assert "successfully logged out!" in result.data

        result = self.login('asdfasdf@test.org', 'test')
        print 'bad login email', result
        assert "that email is not in our system." in result.data

        result = self.login('jacqui@test.org', 'asdfasdf')
        print 'bad login pw', result
        assert "that password is incorrect. Please try again." in result.data

    def test_profile(self):

        result = self.login('jacqui@test.org', 'test')
        self.assertIn('Jacqui', result.data)

    def test_users(self):

        result = self.login('jacqui@test.org', 'test')
        self.assertIn('All Users', result.data)

    def test_add_melody(self):

        result = self.client.post('/add_melody', data=dict(
            title='My Test Melody'), follow_redirects=True)

        self.assertIn('successfully added a melody to your account', result.data)

    def test_follow_user(self):

        result = self.client.get('/follow_user/1', follow_redirects=True)
        self.assertIn('following', result.data)

    def test_unfollow_user(self):

        result = self.client.get('unfollow/1', follow_redirects=True)
        self.assertIn('All Users', result.data)

    def test_add_like(self):

        result = self.client.get('/add_like/3', follow_redirects=True)
        self.assertIn('Unlike this melody', result.data)

    def test_delete_like(self):

        result = self.client.get('/unlike/3', follow_redirects=True)
        self.assertIn('Like this melody', result.data)

    def tearDown(self):
        """ Do at the end of each test."""

        db.session.close()
        # db.drop_all()


if __name__ == '__main__':

    unittest.main()
