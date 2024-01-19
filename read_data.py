import csv
from sqlalchemy.exc import IntegrityError
from models import *

def check_and_read_data(db):
    if Genre.query.count() == 0:
        genres = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 
          'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 
          'Thriller', 'War', 'Western', 'IMAX', '(no genres listed)']
        for g in genres:
            genre = Genre(name=g)
            db.session.add(genre)
        db.session.commit()


    # check if we have movies in the database
    # read data if database is empty
    if Movie.query.count() == 0:
        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)
                        genres = row[2].split('|')  # genres is a list of genres
                        for genre in genres:  # add each genre to the movie_genre table
                            movie_genre = MovieGenre(movie_id=id, genre_id=Genre.query.filter_by(name=genre).first().id, genre = Genre.query.filter_by(name=genre).first())
                            db.session.add(movie_genre)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")

    if Link.query.count() == 0:
        # read links from csv
        with open('data/links.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        movie_id = row[0]
                        imdb_id = row[1]
                        tmdb_id = row[2]
                        link = Link(movie_id=movie_id, imdb_id=imdb_id, tmdb_id=tmdb_id)
                        db.session.add(link)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate link for movie: " + str(movie_id))
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, "links read")

    if Rating.query.count() == 0:
        # read links from csv
        with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        user_id = row[0]
                        movie_id = row[1]
                        rating_value = row[2]
                        if not User.query.filter_by(id=user_id).first():
                            user = User(id=user_id, active=False, username=f"user{user_id}", password="NoPassword")
                            db.session.add(user)
                            db.session.commit()
                        rating = Rating(user_id=user_id, movie_id=movie_id, rating=rating_value)
                        db.session.add(rating)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print(f"Ignoring duplicate rating for movie {movie_id} and user {user_id}.")
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, "ratings read")
    
    if Tag.query.count() == 0:
        # read links from csv
        with open('data/tags.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        user_id = row[0]
                        movie_id = row[1]
                        tg = row[2]
                        if not User.query.filter_by(id=user_id).first():
                            user = User(id=user_id, active=False, username=f"user{user_id}", password="NoPassword")
                            db.session.add(user)
                            db.session.commit()
                        tag = Tag(user_id=user_id, movie_id=movie_id, tag=tg)
                        db.session.add(tag)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate tag for movie: " + str(movie_id))
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, "tags read")


        

