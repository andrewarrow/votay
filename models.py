from google.appengine.ext import db

class BlogPost(db.Model):
  title = db.StringProperty()
  preview = db.StringProperty()
  markup = db.StringProperty()
  permalink = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add=True)
  author_key = db.StringProperty()
  author_name = db.StringProperty()
  
class ImageData(db.Model):
  filename = db.StringProperty()
  width = db.IntegerProperty()
  height = db.IntegerProperty()
  data = db.BlobProperty()
  