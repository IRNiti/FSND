from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#add constraints for fields
artist_genre = db.Table('Artist_Genre',
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE")),
  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id', ondelete="CASCADE"))
  )

venue_genre = db.Table('Venue_Genre',
  db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE")),
  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id', ondelete="CASCADE"))
  )

class Show(db.Model):
  __tablename__ = 'Show'
  
  #need the id field in order to be able to uniquely identify rows in case the same artist plays the same venue multiple times
  #initially used the artist_id and the venue_id as the primary keys, however those can have duplicates
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"))
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"))
  start_time = db.Column(db.DateTime, nullable=False)
  artist = db.relationship('Artist', backref=db.backref('artist_show', lazy=True))
  venue = db.relationship('Venue', backref=db.backref('venue_show', lazy=True))

  def __repr__(self):
    return f'<Show {self.artist_id}, {self.venue_id}, {self.start_time}>'


class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  city = db.Column(db.Integer, db.ForeignKey('City.id', ondelete="SET NULL"))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.relationship('Genre', secondary=venue_genre, backref=db.backref('venues', lazy=True))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String())
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  show = db.relationship('Show', backref=db.backref('venues', lazy=True))

  def __repr__(self):
    return f'<Venue {self.id}, {self.name}>'


class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  city = db.Column(db.Integer, db.ForeignKey('City.id', ondelete="SET NULL"))
  phone = db.Column(db.String(120))
  genres = db.relationship('Genre', secondary=artist_genre, backref=db.backref('artists', lazy=True))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String())
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  show = db.relationship('Show', backref=db.backref('artists', lazy=True))

  def __repr__(self):
    return f'<Artist {self.id}, {self.name}>'


class Genre(db.Model):
  __tablename__ = 'Genre'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  artist_genres = db.relationship('Artist', secondary=artist_genre)
  venue_genres = db.relationship('Venue', secondary=venue_genre)

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