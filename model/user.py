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


class Connection(db.Model):
    """Class for Connections; like an association table for Users to Users relationships?"""

    __tablename__ = "connections"

    connection_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    following_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    # follower = db.relationship("User", foreign_keys=[follower_user_id])
    # following = db.relationship("User", foreign_keys=[following_user_id])

    def __repr__(self):
        return "<Connection ID: {}, Follower: {}, Following: {}>".format(self.connection_id,
                                                                         self.follower_user_id,
                                                                         self.following_user_id,
                                                                         )

    @classmethod
    def add_connection_to_db(cls, follower_user_id, following_user_id):
        """Given the follower and following user ids, adds connection to db."""

        try:
            connection = Connection.query.filter_by(follower_user_id=follower_user_id,
                                                    following_user_id=following_user_id,
                                                    ).one()
            flash("You're already following that user!")

        except NoResultFound:
            connection = Connection(follower_user_id=follower_user_id,
                                    following_user_id=following_user_id,
                                    )
            db.session.add(connection)
            db.session.commit()
            print "Added new connection object to the db."
            following = User.query.get(following_user_id)
            # flash("You're now following {} {}".format(following.first_name, following.last_name))

    @classmethod
    def delete_connection(cls, follower_user_id, following_user_id):
        """Delete a connection between users."""

        try:
            connection = Connection.query.filter_by(follower_user_id=follower_user_id,
                                                    following_user_id=following_user_id,
                                                    ).one()
            db.session.delete(connection)
            db.session.commit()

        except NoResultFound:
            print "That connection was not in the db."


class Like(db.Model):
    """Class for Likes """

    __tablename__ = "likes"

    like_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    melody_id = db.Column(db.Integer, db.ForeignKey('melodies.melody_id'))

    user = db.relationship('User', backref='likes')
    melody = db.relationship('Melody', backref='likes')

    def __repr__(self):
        return "<Like ID: {}, User: {}, Melody: {}>".format(self.like_id,
                                                            self.user,
                                                            self.melody,
                                                            )

    # Could create the add_delete toggle within here... what's best practices?
    @classmethod
    def add_like(cls, user_id, melody_id):
        """Given user and melody ids, adds a new like object to db."""

        try:
            like = Like.query.filter_by(user_id=user_id,
                                        melody_id=melody_id,
                                        ).one()

        except NoResultFound:
            like = Like(user_id=user_id,
                        melody_id=melody_id,
                        )

            db.session.add(like)
            db.session.commit()
            print "Added new like object to the db."

    @classmethod
    def delete_like(cls, user_id, melody_id):
        """Deletes a like object from the db. """

        try:
            like = Like.query.filter_by(user_id=user_id,
                                        melody_id=melody_id,
                                        ).one()
            db.session.delete(like)
            db.session.commit()

        except NoResultFound:
            print "That like object was not in the db."

    @classmethod
    def check_for_likes(cls, melodies, user_id):
        """Checks for existence of likes in list of melodies.

        Returns a list of melodies where like_exists is true."""

        likes_exist = []
        for melody in melodies:
            try:
                Like.query.filter_by(melody_id=melody.melody_id, user_id=user_id).one()
                likes_exist.append(melody)
            except NoResultFound:
                print "This user has not liked this melody."

        return likes_exist


# if __name__ == "__main__":

#     from server import app
#     connect_to_db(app)
#     print "Connected to DB."

    # db.create_all()
