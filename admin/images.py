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
    per_page = 20
    images = query.fetch(per_page, per_page*(page-1))
    next_page_count = len(query.fetch(per_page, per_page*page))
    
    for image in images:
      image.thumb_width = image.width / 8
      image.thumb_height = image.height / 8

    data.update({'images': images})
    self.response.out.write(template.render('views/image.html', data))

class ImagePostHandler(webapp.RequestHandler):
  def post(self):
    lines = str(self.request).split("\n")
    for line in lines:
      if line.startswith('Content-Disposition'):
        filename = line.split(';')[2][11:-2]
        
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
