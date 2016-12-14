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


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    # db.create_all()
