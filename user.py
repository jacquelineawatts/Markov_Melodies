from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


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


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    db.create_all()
