from model import connect_to_db, db, User, Connection
from server import app


def load_seed_users_and_connections():
    """Adds sample users to db. """

    jacqui = User(first_name='Jacqui',
                  last_name='Watts',
                  email='jacqui@test.org',
                  password='test',
                  profile_img='https://scontent.fsjc1-3.fna.fbcdn.net/v/t1.0-1/p320x320/12928314_10103831599186320_7570467518951458496_n.jpg?oh=e4b5b293c0d2716a38a2294070bc2e5a&oe=58D1759E'
                  )
    db.session.add(jacqui)

    zoe = User(first_name='Zoe',
               last_name='Watts',
               email='zoe@test.org',
               password='test',
               profile_img='https://scontent.fsjc1-3.fna.fbcdn.net/l/t31.0-8/12715867_974207742672918_8018653577152190566_o.jpg'
               )
    db.session.add(zoe)
    db.session.commit()

    connection = Connection(follower_user_id=jacqui.user_id,
                            following_user_id=zoe.user_id,
                            )
    db.session.add(connection)
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    print "Connected to DB."

    load_seed_users_and_connections()
