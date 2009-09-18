import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp import template
import os
import sys
import models
import re

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    data = { 'title': 'Admin' }
    
    query = db.GqlQuery('SELECT * FROM BlogPost ORDER BY created_at desc')
    posts = query.fetch(20)    
    data.update({'posts': posts})
    
    self.response.out.write(template.render('views/index.html', data))

class EditHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Edit' }

    post = db.get(db.Key(self.request.get('key')))
    data.update({'post': post})
    self.response.out.write(template.render('views/create.html', data))

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
  def extract_preview(self,markup):
    lines = markup.split("\n")
    buff = []
    for line in lines:
      if line.strip() == '<!-- break -->':
        break
      buff.append(line)
    return ''.join(buff)
    
  def post(self):
    if self.request.get('key'):
      post = db.get(db.Key(self.request.get('key'))) 
      post.title=self.request.get('title')
      post.image=self.request.get('image')
      post.markup=self.request.get('ta')
      post.preview = self.extract_preview(post.markup)
    else:  
      post = models.BlogPost(title=self.request.get('title'),
                 markup=self.request.get('ta'),
                 image=self.request.get('image'),
                 preview='More testing',
                 author_key='',
                 author_name='Andrew Arrow')
      month = str(post.created_at.month)
      if len(month) == 1:
        month = '0' + month
      day = str(post.created_at.day)
      if len(day) == 1:
        day = '0' + day
  
      permalink = re.sub(r'def\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*\(\s*\):', '-', post.title.lower())
      sys.stderr.write(permalink)
      post.permalink = str(post.created_at.year) + '/' + month + '/' + day + '/' + permalink + '/'
      post.preview = self.extract_preview(post.markup)
    post.put()
    self.redirect('/admin', permanent=False)
    
def main():
  application = webapp.WSGIApplication([('/admin/create_post', CreatePostHandler),
                                        ('/admin/create', CreateHandler),
                                        ('/admin/image_post', ImagePostHandler),
                                        ('/admin/image', ImageHandler),
                                        ('/admin/edit.*', EditHandler),
                                         ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
