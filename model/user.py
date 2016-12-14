from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask import flash


class User(db.Model):
    """Class for App Users. """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    profile_img = db.Column(db.String(256))

    following = db.relationship('User',
                                secondary='connections',
                                primaryjoin='Connection.follower_user_id == User.user_id',
                                secondaryjoin='Connection.following_user_id == User.user_id',
                                backref=db.backref('followers'),
                                )

    def __repr__(self):
        return "<User ID: {}; User: {} {}; Email: {}>".format(self.user_id,
                                                              self.first_name,
                                                              self.last_name,
                                                              self.email,
                                                              )

    @classmethod
    def add_user_to_db(cls, email, password, first_name, last_name, profile_img=None):
        """Adds new user instance to the db."""

        user = User(email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    profile_img=profile_img,
                    )

        db.session.add(user)
        db.session.commit()

        return user

    def find_last_melody(self):
        """For a given user, finds their most recently added melody."""

        melody_ids = [melody.melody_id for melody in self.melodies]
        if melody_ids:
            return max(melody_ids)
        else:
            return None


# if __name__ == "__main__":

#     from server import app
#     connect_to_db(app)
#     print "Connected to DB."

    # db.create_all()
