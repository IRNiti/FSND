#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import datetime
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from models import db
from sqlalchemy import func
from flask_moment import Moment
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
db.init_app(app)
migrate = Migrate(app, db)

from models import *


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
  cities = City.query.order_by(City.state)
  venues = db.session.query(Venue, func.count(Show.id)).join(Show, isouter=True).group_by(Venue.id).order_by(Venue.name)
  real_data = []

  
  for city in cities:
    entry = {}
    entry["city"] = city.city
    entry["state"] = city.state
    entry["venues"] = []
    for venue in venues:
      if(city.id == venue[0].city):
        venue_entry = {}
        venue_entry["id"] = venue[0].id
        venue_entry["name"] = venue[0].name
        venue_entry["num_upcoming_shows"] = venue[1]
        entry["venues"].append(venue_entry)
    if(len(entry["venues"]) > 0):
      real_data.append(entry)


  return render_template('pages/venues.html', areas=real_data);


@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_query = '%'+request.form.get('search_term', '')+'%'
  search_venues = Venue.query.filter(Venue.name.ilike(search_query))
  real_data = {}
  real_data["data"] = []

  for search_venue in search_venues:
    entry = {}
    entry["id"] = search_venue.id
    entry["name"] = search_venue.name
    entry["num_upcoming_shows"] = len(search_venue.show)
    real_data["data"].append(entry)

  real_data["count"] = len(real_data["data"])

  return render_template('pages/search_venues.html', results=real_data, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  genres = Genre.query.join(venue_genre).filter((venue_genre.c.genre_id == Genre.id) & (venue_genre.c.venue_id == venue_id)).all()
  shows = db.session.query(Show, Artist).filter((Show.venue_id == venue_id) & (Show.artist_id == Artist.id)).all()
  venue = db.session.query(Venue, City).join(City).filter(Venue.id == venue_id).first()

  data = vars(venue[0])
  data["state"] = venue[1].state
  data["city"] = venue[1].city
  data["genres"] = []
  data["past_shows"] = []
  data["upcoming_shows"] =[]

  for genre in genres:
    data["genres"].append(genre.name)

  for show in shows:
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
  
  form = VenueForm(request.form)
  error = False
  errorMessage = ''

  try:
    if(form.validate()):
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

      venue_city = City.query.filter_by(city=request.form['city'], state=request.form['state']).first()

      if venue_city is None:
        new_city = City(city=request.form['city'], state=request.form['state'])
        db.session.add(new_city)
        db.session.commit()
        new_venue.city = new_city.id
      else:
        new_venue.city = venue_city.id

      venue_genres_input = form.genres.data
      genre_list = []

      for genre_input in venue_genres_input:
        db_value = Genre.query.filter_by(name=genre_input).first()
        if db_value is None:
          new_genre = Genre(name=genre_input)
          db.session.add(new_genre)
          db.session.commit()
          genre_list.append(new_genre)
        else:
          genre_list.append(db_value)

      new_venue.genres = genre_list
      db.session.add(new_venue)
      db.session.commit()
    else:
      error=True
  except:
    db.session.rollback()
    error = True
    errorMessage = sys.exc_info()
  finally:
    db.session.close()
  if error:
    if(form.errors):
      flash('We could not post venue '+ request.form['name'] +' because: ')
      for field, error in form.errors.items():
        flash(field+': '+error[0])
    else:
      if('violates unique constraint' in str(errorMessage[1])):
        flash('A venue with the same name already exists. Please enter another name')
      else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  error = False

  try:
    to_delete = db.session.query(Venue).filter(Venue.id==venue_id).first()
    db.session.delete(to_delete)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return jsonify({ 'success': False })
  else:
    return jsonify({ 'success': True })


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  return render_template('pages/artists.html', artists=Artist.query.order_by(Artist.name))


@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_query = '%'+request.form.get('search_term', '')+'%'
  search_artists = Artist.query.filter(Artist.name.ilike(search_query))
  real_data = {}
  real_data["data"] = []

  for search_artist in search_artists:
    entry = {}
    entry["id"] = search_artist.id
    entry["name"] = search_artist.name
    entry["num_upcoming_shows"] = len(search_artist.show)
    real_data["data"].append(entry)

  real_data["count"] = len(real_data["data"])

  
  return render_template('pages/search_artists.html', results=real_data, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = db.session.query(Artist, City).join(City).filter(Artist.id == artist_id).first()
  genres = Genre.query.join(artist_genre).filter((artist_genre.c.genre_id == Genre.id) & (artist_genre.c.artist_id == artist_id)).all()
  shows = db.session.query(Show, Venue).filter((Show.artist_id == artist_id) & (Show.venue_id == Venue.id)).all()

  data = vars(artist[0])
  data["state"] = artist[1].state
  data["city"] = artist[1].city
  data["genres"] = []
  data["past_shows"] = []
  data["upcoming_shows"] =[]

  for genre in genres:
    data["genres"].append(genre.name)

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

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  real_artist = Artist.query.get(artist_id)
  artist_city = City.query.get(real_artist.city)
  artist_genres = []

  for genre in real_artist.genres:
    artist_genres.append(genre.name)

  form = ArtistForm(
    name=real_artist.name,
    city=artist_city.city,
    state=artist_city.state,
    genres=artist_genres,
    phone=real_artist.phone,
    facebook_link=real_artist.facebook_link,
    image_link=real_artist.image_link,
    website=real_artist.website,
    seeking_description=real_artist.seeking_description,
    seeking_venue=real_artist.seeking_venue
    )

  return render_template('forms/edit_artist.html', form=form, artist=real_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form)
  to_update = Artist.query.get(artist_id)
  error = False

  try:
    
    #if the user leaves the checkbox unchecked, then nothing is getting sent in the request for seeking_talent
    #so setting up False as default if nothing is found in the request
    #if the checkbox is checked, the form sends a value of 'y' which is not a boolean so converting that to True
    want_venue = request.form.get('seeking_venue', False)
    if(want_venue == 'y'):
      want_venue = True

    to_update.name = request.form['name']
    to_update.phone=request.form['phone']
    to_update.image_link=request.form['image_link']
    to_update.facebook_link=request.form['facebook_link']
    to_update.website=request.form['website']
    to_update.seeking_venue=want_venue
    to_update.seeking_description=request.form['seeking_description']

    artist_city = City.query.filter_by(city=request.form['city'], state=request.form['state']).all()


    if(len(artist_city) == 0):
      new_city = City(city=request.form['city'], state=request.form['state'])
      db.session.add(new_city)
      db.session.commit()
      to_update.city = new_city.id
    else:
      to_update.city = artist_city[0].id

    artist_genres_input = form.genres.data
    genre_list = []

    for genre_input in artist_genres_input:
      db_value = Genre.query.filter_by(name=genre_input).all()
      if(len(db_value) == 0):
        new_genre = Genre(name=genre_input)
        db.session.add(new_genre)
        db.session.commit()
        genre_list.append(new_genre)
      else:
        genre_list.append(db_value[0])

    to_update.genres = genre_list

    db.session.add(to_update)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  real_venue = Venue.query.get(venue_id)
  venue_city = City.query.get(real_venue.city)
  venue_genres = []

  for genre in real_venue.genres:
    venue_genres.append(genre.name)

  form = VenueForm(
    name=real_venue.name,
    city=venue_city.city,
    state=venue_city.state,
    address=real_venue.address,
    genres=venue_genres,
    phone=real_venue.phone,
    facebook_link=real_venue.facebook_link,
    image_link=real_venue.image_link,
    website=real_venue.website,
    seeking_description=real_venue.seeking_description,
    seeking_talent=real_venue.seeking_talent
    )

  return render_template('forms/edit_venue.html', form=form, venue=real_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm(request.form)
  to_update = Venue.query.get(venue_id)
  error = False

  try:
    
    #if the user leaves the checkbox unchecked, then nothing is getting sent in the request for seeking_talent
    #so setting up False as default if nothing is found in the request
    #if the checkbox is checked, the form sends a value of 'y' which is not a boolean so converting that to True
    want_talent = request.form.get('seeking_talent', False)
    if(want_talent == 'y'):
      want_talent = True

    to_update.name = request.form['name']
    to_update.address=request.form['address']
    to_update.phone=request.form['phone']
    to_update.image_link=request.form['image_link']
    to_update.facebook_link=request.form['facebook_link']
    to_update.website=request.form['website']
    to_update.seeking_talent=want_talent
    to_update.seeking_description=request.form['seeking_description']

    venue_city = City.query.filter_by(city=request.form['city'], state=request.form['state']).all()


    if(len(venue_city) == 0):
      new_city = City(city=request.form['city'], state=request.form['state'])
      db.session.add(new_city)
      db.session.commit()
      to_update.city = new_city.id
    else:
      to_update.city = venue_city[0].id

    venue_genres_input = form.genres.data
    genre_list = []

    for genre_input in venue_genres_input:
      db_value = Genre.query.filter_by(name=genre_input).all()
      if(len(db_value) == 0):
        new_genre = Genre(name=genre_input)
        db.session.add(new_genre)
        db.session.commit()
        genre_list.append(new_genre)
      else:
        genre_list.append(db_value[0])

    to_update.genres = genre_list

    db.session.add(to_update)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  
  form = ArtistForm(request.form)
  error = False
  errorMessage = ''

  try:
    if(form.validate()):
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

      artist_city = City.query.filter_by(city=request.form['city'], state=request.form['state']).first()

      if artist_city is None:
        new_city = City(city=request.form['city'], state=request.form['state'])
        db.session.add(new_city)
        db.session.commit()
        new_artist.city = new_city.id
      else:
        new_artist.city = artist_city.id

      artist_genres_input = form.genres.data
      genre_list = []

      for genre_input in artist_genres_input:
        db_value = Genre.query.filter_by(name=genre_input).first()
        if db_value is None:
          new_genre = Genre(name=genre_input)
          db.session.add(new_genre)
          db.session.commit()
          genre_list.append(new_genre)
        else:
          genre_list.append(db_value)

      new_artist.genres = genre_list
      db.session.add(new_artist)
      db.session.commit()
    else:
      error=True
  except:
    db.session.rollback()
    error = True
    errorMessage = sys.exc_info()
    print(errorMessage)
  finally:
    db.session.close()
  if error:
    if(form.errors):
      flash('We could not post artist '+ request.form['name'] +' because: ')
      for field, error in form.errors.items():
        flash(field+': '+error[0])
    else:
      if('violates unique constraint' in str(errorMessage[1])):
        flash('An artist with the same name already exists. Please enter another name')
      else:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  real_data = []
  db_shows = db.session.query(Venue, Show, Artist).filter((Show.venue_id == Venue.id) & (Show.artist_id == Artist.id)).order_by(Show.start_time)

  for show in db_shows:
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


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  error = False

  try:
    if(form.validate()):
      new_show = Show(
        artist_id=request.form['artist_id'],
        venue_id=request.form['venue_id'],
        start_time=request.form['start_time']
        )
      db.session.add(new_show)
      db.session.commit()
    else:
      error=True

  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    if(form.errors):
      flash('We could not post your show because: ')
      for field, error in form.errors.items():
        flash(field+': '+error[0])
    else:
      flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

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
