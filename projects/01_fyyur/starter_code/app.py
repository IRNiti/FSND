#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import datetime
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

artist_genre = db.Table('Artist_Genre',
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), nullable=False),
  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), nullable=False)
  )

venue_genre = db.Table('Venue_Genre',
  db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), nullable=False),
  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), nullable=False)
  )

class Show(db.Model):
  __tablename__ = 'Show'
  
  #need the id field in order to be able to uniquely identify rows in case the same artist plays the same venue multiple times
  #initially used the artist_id and the venue_id as the primary keys, however those can have duplicates
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  start_time = db.Column(db.DateTime, nullable=False)
  artist = db.relationship('Artist', backref=db.backref('artist_show', lazy=True))
  venue = db.relationship('Venue', backref=db.backref('venue_show', lazy=True))

  def __repr__(self):
    return f'<Show {self.artist_id}, {self.venue_id}, {self.start_time}>'


class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.Integer, db.ForeignKey('City.id'))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.relationship('Genre', secondary=venue_genre, backref=db.backref('venues', lazy=True))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String())
  seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String())
  show = db.relationship('Show', backref=db.backref('venues', lazy=True))

  def __repr__(self):
    return f'<Venue {self.id}, {self.name}>'


class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.Integer, db.ForeignKey('City.id'))
  phone = db.Column(db.String(120))
  genres = db.relationship('Genre', secondary=artist_genre, backref=db.backref('artists', lazy=True))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String())
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String())
  show = db.relationship('Show', backref=db.backref('artists', lazy=True))

  def __repr__(self):
    return f'<Artist {self.id}, {self.name}>'


class Genre(db.Model):
  __tablename__ = 'Genre'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  artist_genres = db.relationship('Artist', secondary=artist_genre, backref=db.backref('artist_genres', lazy=True))
  venue_genres = db.relationship('Venue', secondary=venue_genre, backref=db.backref('venue_genres', lazy=True))

  def __repr__(self):
    return f'<Genre {self.id}, {self.name}>'

class City(db.Model):
  __tablename__ = 'City'

  id = db.Column(db.Integer, primary_key=True)
  #update this to name so it's not city.city
  city = db.Column(db.String)
  state = db.Column(db.String(2))
  artist_city = db.relationship('Artist', backref=db.backref('artist_city', lazy=True))
  venue_city = db.relationship('Venue', backref=db.backref('venue_city', lazy=True))

  def __repr__(self):
    return f'<City {self.id}, {self.city}, {self.state}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.all()
  cities = City.query.all()
  real_data = []
  
  for city in cities:
    entry = {}
    #update this to city.name
    entry["city"] = city.city
    entry["state"] = city.state
    entry["venues"] = []
    for venue in venues:
      if(city.id == venue.city):
        venue_entry = {}
        venue_entry["id"] = venue.id
        venue_entry["name"] = venue.name
        # should find a better way to do this since query in nested for loop
        venue_entry["num_upcoming_shows"] = Show.query.filter_by(venue_id = venue.id).count()
        entry["venues"].append(venue_entry)
    if(len(entry["venues"]) > 0):
      real_data.append(entry)


  return render_template('pages/venues.html', areas=real_data);

#TODO*******************************
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  genres = Genre.query.join(venue_genre).filter((venue_genre.c.genre_id == Genre.id) & (venue_genre.c.venue_id == venue_id)).all()
  shows = db.session.query(Show, Artist).filter((Show.venue_id == venue_id) & (Show.artist_id == Artist.id)).all()

  data = vars(venue)
  data["state"] = City.query.get(venue.city).state
  data["city"] = City.query.get(venue.city).city
  data["genres"] = []
  data["past_shows"] = []
  data["upcoming_shows"] =[]

  for genre in genres:
    data["genres"].append(genre.name)

  # account for venue timezone when checking whether show is past or upcoming
  # datetime.now returns local date and time
  # to do after implementing show creation
  for show in shows:
    print(str(show[0].start_time))
    entry = {}
    entry["artist_id"] = show[0].artist_id
    entry["artist_name"] = show[1].name
    entry["artist_image_link"] = show[1].image_link
    entry["start_time"] = str(show[0].start_time)
    if(show[0].start_time < datetime.now()):
      data["past_shows"].append(entry)
    else:
      data["upcoming_shows"].append(entry)

  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  error = False

  # print(request.form)
  # print(request.form.get('seeking_talent', False))
  # print(request.form['genres'])
  # print(form.genres.data)
  # print(form.genres.data[0])
  #print(request.form['seeking_talent'])

  try:
    #print(request.form['seeking_talent'])
    want_talent = request.form.get('seeking_talent', False)
    if(want_talent == 'y'):
      want_talent = True
    
    new_venue = Venue(
      name = request.form['name'],
      address=request.form['address'],
      phone=request.form['phone'],
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      website=request.form['website'],
      seeking_talent=want_talent,
      seeking_description=request.form['seeking_description'])

    venue_city = City.query.filter_by(city=request.form['city'], state=request.form['state']).all()

    if(len(venue_city) == 0):
      new_city = City(city=request.form['city'], state=request.form['state'])
      db.session.add(new_city)
      db.session.commit()
      new_venue.city = new_city.id
    else:
      new_venue.city = venue_city[0].id

    venue_genres_input = form.genres.data
    genre_list = []

    #find a better way to do this since it's horrible
    for genre_input in venue_genres_input:
      db_value = Genre.query.filter_by(name=genre_input).all()
      if(len(db_value) == 0):
        new_genre = Genre(name=genre_input)
        db.session.add(new_genre)
        db.session.commit()
        genre_list.append(new_genre)
        # new_venue_genre = venue_genre(venue_id=new_venue.id, genre_id=new_genre.id)
        # db.session.add(new_venue_genre)
        # db.session.commit()
      else:
        genre_list.append(db_value[0])
        # new_venue_genre = venue_genre(venue_id=new_venue.id, genre_id=db_value[0].id)
        # db.session.add(new_venue_genre)
        # db.session.commit()

    new_venue.genres = genre_list
    db.session.add(new_venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

#TODO*******************************
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  return render_template('pages/artists.html', artists=Artist.query.all())

#TODO*******************************
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  genres = Genre.query.join(artist_genre).filter((artist_genre.c.genre_id == Genre.id) & (artist_genre.c.artist_id == artist_id)).all()
  shows = db.session.query(Show, Venue).filter((Show.artist_id == artist_id) & (Show.venue_id == Venue.id)).all()

  data = vars(artist)
  print(data["name"])
  print(data["city"])
  print(artist.city)
  data["state"] = City.query.get(artist.city).state
  print(data["state"])
  print(data["city"])
  print(artist.city)
  data["city"] = City.query.get(artist.city).city
  data["genres"] = []
  data["past_shows"] = []
  data["upcoming_shows"] =[]

  for genre in genres:
    data["genres"].append(genre.name)

# account for venue timezone when checking whether show is past or upcoming
  # datetime.now returns local date and time
  # to do after implementing show creation
  for show in shows:
    entry = {}
    entry["venue_id"] = show[0].venue_id
    entry["venue_name"] = show[1].name
    entry["venue_image_link"] = show[1].image_link
    entry["start_time"] = str(show[0].start_time)
    if(show[0].start_time < datetime.now()):
      data["past_shows"].append(entry)
    else:
      data["upcoming_shows"].append(entry)

  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

#TODO*******************************
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

#TODO*******************************
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

#TODO*******************************
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

#TODO*******************************
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

#TODO*******************************
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm()
  error = False

  # print(request.form)
  # print(request.form.get('seeking_talent', False))
  # print(request.form['genres'])
  # print(form.genres.data)
  # print(form.genres.data[0])
  #print(request.form['seeking_talent'])

  try:
    #print(request.form['seeking_venue'])
    want_venue = request.form.get('seeking_venue', False)
    if(want_venue == 'y'):
      want_venue = True
    
    new_artist = Artist(
      name = request.form['name'],
      phone=request.form['phone'],
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      website=request.form['website'],
      seeking_venue=want_venue,
      seeking_description=request.form['seeking_description'])

    #test whether this works for cities with same name but different states
    artist_city = City.query.filter_by(city=request.form['city'], state=request.form['state']).all()

    #check if query returns more than one result
    if(len(artist_city) == 0):
      new_city = City(city=request.form['city'], state=request.form['state'])
      db.session.add(new_city)
      db.session.commit()
      new_artist.city = new_city.id
    else:
      new_artist.city = artist_city[0].id

    artist_genres_input = form.genres.data
    genre_list = []

    #find a better way to do this since it's horrible
    for genre_input in artist_genres_input:
      db_value = Genre.query.filter_by(name=genre_input).all()
      if(len(db_value) == 0):
        new_genre = Genre(name=genre_input)
        db.session.add(new_genre)
        db.session.commit()
        genre_list.append(new_genre)
      else:
        #check if there is more than one result??
        genre_list.append(db_value[0])

    new_artist.genres = genre_list
    db.session.add(new_artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  real_data = []
  q = db.session.query(Venue, Show, Artist).filter((Show.venue_id == Venue.id) & (Show.artist_id == Artist.id)).all()

  #should we still display shows that have passed?
  for show in q:
    entry = {}
    entry["venue_id"] = show[0].id
    entry["artist_id"] = show[2].id
    entry["venue_name"] = show[0].name
    entry["artist_name"] = show[2].name
    entry["artist_image_link"] = show[2].image_link
    entry["start_time"] = str(show[1].start_time)
    real_data.append(entry)
  
  return render_template('pages/shows.html', shows=real_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

#TODO*******************************
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
