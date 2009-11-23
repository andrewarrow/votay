import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp import template
import util
import os
import sys
import models
import re

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    util.send404(self)
    return    

class ImageHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Image' }
    
    page = 1
    query = db.GqlQuery('SELECT * FROM ImageMetaData ORDER BY created_at desc')
    per_page = 5
    images = query.fetch(per_page, per_page*(page-1))
    next_page_count = len(query.fetch(per_page, per_page*page))
    
    for image in images:
      image.thumb_width = image.width
      image.thumb_height = image.height
      
      while image.thumb_width > 75:
        image.thumb_width = image.thumb_width / 2
        image.thumb_height = image.thumb_height / 2

      while image.thumb_height > 75:     
        image.thumb_height = image.thumb_height / 2
        image.thumb_width = image.thumb_width / 2

    data.update({'images': images})
    self.response.out.write(template.render('views/image.html', data))

class ImagePostHandler(webapp.RequestHandler):
  def post(self):
    lines = str(self.request).split("\n")
    for line in lines:
      if line.startswith('Content-Disposition'):
        filename = line.split(';')[2][11:-2]
        
        
    filename = re.sub('[^a-z0-9\.]', '_', filename.lower())
    
    query = db.GqlQuery('SELECT * FROM ImageData WHERE filename = :1', filename)
    list = query.fetch(1)

    if len(list) == 0:    
      image = images.Image(self.request.get("img"))
      image_data = models.ImageData(data=self.request.get("img"),
                                    filename=filename)
      image_meta_data = models.ImageMetaData(filename=filename,
                                    width=image.width,
                                    height=image.height)
      image_data.put()
      image_meta_data.put()
      
    self.redirect('/admin', permanent=False)
    
def main():
  application = webapp.WSGIApplication([('/admin/image_post', ImagePostHandler),
                                        ('/admin/images', ImageHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
