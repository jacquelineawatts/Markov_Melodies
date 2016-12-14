from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask import flash


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
