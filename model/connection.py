from model import connect_to_db, db
from user import User
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask import flash


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
