import unittest
from server import app
from model import connect_to_db, db


class FlaskTests(unittest.TestCase):
    """Integration tests for app."""

    def setUp(self):

        self.client = app.test_client()
        app.config['TESTING'] = True
        # What is this 'key' actually supposed to be? os.urandom(24)?
        app.config['SECRET_KEY'] = 'key'

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = True

    def test_homepage(self):

        result = self.client.get('/')
        self.assertIn('Welcome', result.data)

    def test_results(self):

        result = self.client.get('/results')
        self.assertIn('Resulting Melody', result.data)


class FlaskTestsDatabase(unittest.TestCase):
    """Integration tests for pages requiring db and login."""

    def setUp(self):

        self.client = app.test_client()
        app.config['TESTING'] = True
        # What is this 'key' actually supposed to be? os.urandom(24)?
        app.config['SECRET_KEY'] = 'key'

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = True

        connect_to_db(app, "postgresql:///testdb")
        db.create_all()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password),
            follow_redirects=True)

    def logout(self):
        return self.client.get('logout', follow_redirects=True)

    def test_login_logout(self):

        rv = self.login('jacqui@test.org', 'test')
        print 'successful login', rv
        assert "You've successfully logged in!" in rv.data
        rv = self.logout()
        print 'successful logout', rv
        assert "You've successfully logged out!" in rv.data
        rv = self.login('asdfasdf@test.org', 'test')
        print 'bad login email', rv
        assert "I'm sorry that email is not in our system." in rv.data
        rv = self.login('jacqui@test.org', 'asdfasdf')
        print 'bad login pw', rv
        assert "I'm sorry that password is incorrect. Please try again." in rv.data

    def test_profile(self):

        # rv = self.login('jacqui@test.org', 'test')

        # Is this how I'd test for whether or not a users profile is routing correctly?
        result = self.client.get('/profile/1')
        self.assertIn('Jacqui', result.data)

    def tearDown(self):
        """ Do at the end of each test."""

        db.session.close()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()
