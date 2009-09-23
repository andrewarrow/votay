from google.appengine.ext import db

class BlogPost(db.Model):
  title = db.StringProperty()
  preview = db.TextProperty()
  markup = db.TextProperty()
  permalink = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add=True)
  author_permalink = db.StringProperty()
  author_name = db.StringProperty()
  image = db.StringProperty()
  
  def rfc3339_created_at(self):
    return self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
    
  def to_atom_xml(self):
    import re
    return re.sub('&(?!amp;)', '&amp;', self.markup)    
  
class ImageData(db.Model):
  filename = db.StringProperty()
  data = db.BlobProperty()

class ImageMetaData(db.Model):
  filename = db.StringProperty()
  width = db.IntegerProperty()
  height = db.IntegerProperty()
  created_at = db.DateTimeProperty(auto_now_add=True)
  
class Feature(db.Model):
  title = db.StringProperty()
  preview = db.StringProperty()
  permalink = db.StringProperty()
  position = db.IntegerProperty()
  created_at = db.DateTimeProperty(auto_now_add=True)
  image = db.StringProperty()

class Author(db.Model):
  author_name = db.StringProperty()
  author_permalink = db.StringProperty()
  
class Comment(db.Model):
  blog_post_key = db.StringProperty()
  text = db.TextProperty()
  user_id = db.StringProperty()
  email = db.StringProperty()
  replied_to_key = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add=True)
  is_admin = db.BooleanProperty()
  
class Nickname(db.Model):
  user_id = db.StringProperty()
  nickname = db.StringProperty()
  url = db.StringProperty()
  