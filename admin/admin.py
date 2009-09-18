import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp import template
import os
import sys
import models

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    data = { 'title': 'Admin' }
    self.response.out.write(template.render('views/index.html', data))

class CreateHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Create' }
    self.response.out.write(template.render('views/create.html', data))

class ImageHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Image' }
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
    
class CreatePostHandler(webapp.RequestHandler):
  def post(self):
    bp = models.BlogPost(title=self.request.get('title'),
                 markup=self.request.get('ta'),
                 image=self.request.get('image'),
                 preview='More testing',
                 author_key='',
                 author_name='Andrew Arrow')
    month = str(bp.created_at.month)
    if len(month) == 1:
      month = '0' + month
    day = str(bp.created_at.day)
    if len(day) == 1:
      day = '0' + day

    bp.permalink = str(bp.created_at.year) + '/' + month + '/' + day + '/this-is-a-test-title/'
    bp.put()
    self.redirect('/admin', permanent=False)
    
def main():
  application = webapp.WSGIApplication([('/admin/create_post', CreatePostHandler),
                                        ('/admin/create', CreateHandler),
                                        ('/admin/image_post', ImagePostHandler),
                                        ('/admin/image', ImageHandler),
                                         ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
