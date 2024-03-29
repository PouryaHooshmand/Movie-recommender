from flask import Flask, render_template, request, redirect, url_for
from flask_user import login_required, UserManager, current_user

from models import db, User, Movie, MovieGenre, FavoriteGenres, Genre, Rating
from read_data import check_and_read_data
from get_recommendations import *


class CustomUserManager(UserManager):
    @login_required
    def edit_user_profile_view(self):
            # Initialize form
            form = self.EditUserProfileFormClass(request.form, obj=current_user)

            # Process valid POST
            if request.method == 'POST' and form.validate():
                # Update fields
                form.populate_obj(current_user)

                # Save object
                self.db_manager.save_object(current_user)
                self.db_manager.commit()

                return redirect(self._endpoint_url(self.USER_AFTER_EDIT_USER_PROFILE_ENDPOINT))

            # Render form
            self.prepare_domain_translations()

            genres = {}
            fav_genres = [g.genre for g in FavoriteGenres.query.filter(FavoriteGenres.user_id==current_user.id).all()]
            for g in Genre.query.all():
                genres[g] = g in fav_genres
            
            return render_template(self.USER_EDIT_USER_PROFILE_TEMPLATE, form=form, genres=genres)

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Movie Recommender"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

    USER_AFTER_REGISTER_ENDPOINT = 'welcome_page'
    USER_AFTER_CONFIRM_ENDPOINT = 'welcome_page'
    USER_AFTER_LOGIN_ENDPOINT = 'welcome_page'
    USER_AFTER_LOGOUT_ENDPOINT = 'home_page'

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = CustomUserManager(app, db, User)  # initialize Flask-User management

@app.cli.command('initdb')
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')

@app.route('/')
def home_page():
    is_logged_in = isinstance(current_user, User)
    top_movies = {}
    movies = Movie.query.order_by(Movie.rating_sum.desc()).limit(5).all()
    for m in movies:
        rating = [r.rating for r in m.ratings]
        if rating:
            top_movies[m] = (len(rating), round(sum(rating)/len(rating),1))
    top_cat_movies = {}
    rated_movies = {}
    if is_logged_in:
        
        fav_genres = [g.genre_id for g in FavoriteGenres.query.filter(FavoriteGenres.user_id==current_user.id).all()]
        
        
        if fav_genres:
            movies = Movie.query.join(MovieGenre).filter(MovieGenre.genre_id.in_(fav_genres)).distinct().order_by(Movie.rating_sum.desc()).limit(5).all()
            for m in movies:
                rating = [r.rating for r in m.ratings]
                if rating:
                    top_cat_movies[m] = (len(rating), round(sum(rating)/len(rating),1))
        
        movies = list(reversed([Movie.query.get(mid) for mid in [r.movie_id for r in current_user.ratings]]))
        for m in movies[:5]:
            rating = [r.rating for r in m.ratings]
            rated_movies[m] = (len(rating), round(sum(rating)/len(rating),1))
    return render_template("home.html", top_movies = top_movies, top_cat_movies = top_cat_movies, rated_movies = rated_movies)

@app.route("/welcome")
@login_required
def welcome_page():
    if current_user.first_name or current_user.last_name or FavoriteGenres.query.filter(FavoriteGenres.user_id==current_user.id).all():
        return redirect(url_for('home_page'))
    
    genres = Genre.query.all()
    return render_template("welcome.html", user=current_user, genres = genres[:-1])

@app.route("/search")
@login_required
def results_page():
    movie_name = request.args.get('q')
    movies = Movie.query.filter(Movie.title.icontains(movie_name)).all()
    ratings = {}
    for m in movies:
        rating = [r.rating for r in m.ratings]
        user_rating = [r.rating for r in m.ratings if r.user_id==current_user.id]
        if user_rating:
            user_rating = user_rating[0]
        else:
            user_rating = 0
        if rating:
            ratings[m] = (len(rating), round(sum(rating)/len(rating),1), user_rating)
        else:
            ratings[m] = (0,0,0)
    return render_template("movies.html", movies=ratings)


@app.route('/movies')
@login_required  # User must be authenticated
def movies_page():
    fav_genres = [g.genre_id for g in FavoriteGenres.query.filter(FavoriteGenres.user_id==current_user.id).all()]
    if not fav_genres:
        fav_genres = [g.id for g in Genre.query.all()]
    ratings = {}
    
    if Rating.query.filter(Rating.user_id==current_user.id).first():
        all_ratings = Rating.query.with_entities(Rating.user_id, Rating.movie_id, Rating.rating).all()

        df = pd.DataFrame.from_records(all_ratings, columns=['user_id', 'movie_id', 'rating'])

        init_movie_list = [int(_) for _ in get_recommendations_user(df, current_user.id)]
        init_movie_list = init_movie_list[:int(len(init_movie_list)/5)]
        all_ratings = Rating.query.filter(Rating.movie_id.in_(init_movie_list)).with_entities(Rating.user_id, Rating.movie_id, Rating.rating).all()
        df = pd.DataFrame.from_records(all_ratings, columns=['user_id', 'movie_id', 'rating'])

        movie_ranking = [int(_) for _ in get_recommendations_item(df, current_user.id)]
        i = 0
        for m_id in movie_ranking:
            m = Movie.query.get(m_id)
            if (set(fav_genres) & set([g.genre_id for g in m.genres])) and \
                (Rating.query.filter(Rating.movie_id==m_id).filter(Rating.user_id==current_user.id).first() is None):
                
                rating = [r.rating for r in m.ratings]
                if rating:
                    ratings[m] = (len(rating), round(sum(rating)/len(rating),1))
                else:
                    ratings[m] = (0,0)
                i+=1
                if i>=50:
                    break
    else:
        movies = Movie.query.join(MovieGenre).filter(MovieGenre.genre_id.in_(fav_genres)).distinct().limit(10).all()
        common_genres = [len([g.genre_id for g in m.genres if g.genre_id in fav_genres]) for m in movies]
        for m in movies:
            rating = [r.rating for r in m.ratings]
            user_rating = [r.rating for r in m.ratings if r.user_id==current_user.id]
            if user_rating:
                user_rating = user_rating[0]
            else:
                user_rating = 0
            if rating:
                ratings[m] = (len(rating), round(sum(rating)/len(rating),1), user_rating)
            else:
                ratings[m] = (0,0,0)

        common_genres, ratings = zip(*sorted(zip(common_genres,ratings.items()), key= lambda i:i[1][1][1], reverse=True))
        ratings = dict([x for _, x in sorted(zip(common_genres,ratings), key= lambda i:i[0], reverse=True)])

    return render_template("movies.html", movies=ratings)


@app.route('/rated_movies')
@login_required
def rated_movies_page():
    ratings = {}
    
    movies = reversed([Movie.query.get(mid) for mid in [r.movie_id for r in current_user.ratings]])
    for m in movies:
        rating = [r.rating for r in m.ratings]
        user_rating = [r.rating for r in m.ratings if r.user_id==current_user.id][0]
        ratings[m] = (len(rating), round(sum(rating)/len(rating),1), user_rating)
    
    return render_template("rated_movies.html", movies=ratings)



    
@app.route('/user/update_favs', methods=['POST'])
@login_required
def update_favs():
    data = request.get_json()
    for g in data:
        fav_genre_entry = FavoriteGenres.query.filter(FavoriteGenres.genre.has(Genre.name==g))\
                .filter(FavoriteGenres.user_id==current_user.id).first()
        if data[g]:
            if fav_genre_entry is None:
                genre = Genre.query.filter(Genre.name==g).first()
                new_fav = FavoriteGenres(user_id=current_user.id, genre_id = genre.id, genre = genre)
                db.session.add(new_fav)
        else:
            if fav_genre_entry:
                db.session.delete(fav_genre_entry)
    db.session.commit()
    return {'message':'Favorites updated successfully'}, 200

@app.route('/set_user_profile', methods=['POST'])
@login_required
def set_user_profile():
    data = request.get_json()
    current_user.first_name = data["first_name"]
    current_user.last_name = data["last_name"]
    data.pop('first_name', None)
    data.pop('last_name', None)
    for g in data:
        if data[g]:
            genre = Genre.query.filter(Genre.name==g).first()
            new_fav = FavoriteGenres(user_id=current_user.id, genre_id = genre.id, genre = genre)
            db.session.add(new_fav)
    db.session.commit()
    return {'message':'profile updated successfully'}, 200


@app.route('/rate', methods=['POST'])
@login_required
def rate_movie():
    data = request.get_json()
    movie_id = int(data['movie_id'])
    movie = Movie.query.get(movie_id)
    rating = int(data['rating'])
    movie_prev_rating = Rating.query.filter(Rating.user_id==current_user.id).filter(Rating.movie_id==movie_id).first()

    if movie_prev_rating:
        movie.rating_sum -= movie_prev_rating.rating
        db.session.delete(movie_prev_rating)

    new_rating = Rating(user_id=current_user.id, movie_id=movie_id, rating=rating)
    movie.rating_sum += new_rating.rating
    db.session.add(new_rating)
    db.session.commit()

    return {'message':'rating updated successfully'}, 200

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
