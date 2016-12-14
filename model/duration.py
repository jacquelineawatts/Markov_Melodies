from model import connect_to_db, db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class Duration(db.Model):
    """Class for duration. """

    __tablename__ = "durations"

    duration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    duration = db.Column(db.Float)

    def __repr__(self):
            return "<Duration: {}>".format(self.duration)

    @classmethod
    def add_duration_to_db(cls, duration):

        duration = Duration(duration=duration)
        db.session.add(duration)
        db.session.commit()
        print "Added new duration object to db."

        return duration

    @staticmethod
    def convert_duration_db_to_abc(duration):
        """Converts duration from db scale to abc notation scale """

        try:
            duration = (float(duration) ** -1) * 4
        except ZeroDivisionError:
            duration = 2.0

        return duration

    @staticmethod
    def convert_duration_abc_to_db(duration):
        """Converts duration from abc notation scale to db scale """

        return (duration / 4) ** -1
