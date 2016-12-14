from model import connect_to_db, db
from genre import Genre
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class MelodyGenre(db.Model):
    """Association table connecting melodies and genres."""

    __tablename__ = "melodies_genres"

    melodygenre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    melody_id = db.Column(db.Integer, db.ForeignKey('melodies.melody_id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'))

    def __repr__(self):
        return "<MelodyGenre ID: {}, Melody: {}, Genre: {}".format(self.melodygenre_id,
                                                                   self.melody_id,
                                                                   self.genre_id,
                                                                   )

    @classmethod
    def add_melody_genre_to_db(cls, melody_id, genres):
        """Adds melody_genre instance to the db."""

        for genre in genres:
            try:
                genre_id = Genre.query.filter_by(genre=genre).one().genre_id

            except NoResultFound:
                print "No genre was found with that name."

            try:
                MelodyGenre.query.filter_by(melody_id=melody_id, genre_id=genre_id).one()

            except NoResultFound:
                melody_genre = MelodyGenre(melody_id=melody_id,
                                           genre_id=genre_id,
                                           )

                db.session.add(melody_genre)
                db.session.commit()
                print "Successfully added new new melody_genre association."
