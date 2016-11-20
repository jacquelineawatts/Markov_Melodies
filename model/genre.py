from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class Genre(db.Model):
    """Class for musical genres."""

    __tablename__ = "genres"

    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre = db.Column(db.String(20))

    def __repr__(self):
        return "<Genre ID: {}, Genre: {}".format(self.genre_id,
                                                 self.genre,
                                                 )

    @classmethod
    def add_genre_to_db(cls, genre):
        """Adds a new genre object to the db."""

        try:
            Genre.query.filter_by(genre=genre).one()
        except NoResultFound:
            genre = Genre(genre=genre)
            db.session.add(genre)
            db.session.commit()
            print "Successfully added new genre."

    @classmethod
    def get_genre(cls, genre_name):
        """Given a genre name, returns a genre object.

        SEE WHERE THIS IS USED, AND POTENTIALLY CALL ADD TO DB IN EXCEPT."""

        try:
            genre = Genre.query.filter_by(genre=genre_name).one()
        except NoResultFound:
            print "No genre instance was found with that name."

        return genre


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


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    # db.create_all()
