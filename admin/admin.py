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

    query = db.GqlQuery('SELECT * FROM Feature ORDER BY created_at desc')
    features = query.fetch(20)    
    data.update({'features': features})
    
    self.response.out.write(template.render('views/index.html', data))

class EditHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Edit' }

    post = db.get(db.Key(self.request.get('key')))
    data.update({'post': post})
    
    query = db.GqlQuery('SELECT * FROM Author ORDER BY author_name')
    authors = query.fetch(20)
    for author in authors:
      if author.author_permalink == post.author_permalink:
        author.selected = 'selected="true"'
    data.update({'authors': authors})
    
    self.response.out.write(template.render('views/create.html', data))

class EditFeatureHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Edit Feature' }

    feature = db.get(db.Key(self.request.get('key')))
    data.update({'feature': feature})
    self.response.out.write(template.render('views/create_feature.html', data))

class CreateHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Create' }
    
    query = db.GqlQuery('SELECT * FROM Author ORDER BY author_name')
    authors = query.fetch(20)
    data.update({'authors': authors})
    
    self.response.out.write(template.render('views/create.html', data))

class CreateFeatureHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Create Feature' }
    self.response.out.write(template.render('views/create_feature.html', data))

class CreateAuthorHandler(webapp.RequestHandler):
  def get(self):
    data = { 'title': 'Admin Create Author' }
    self.response.out.write(template.render('views/create_author.html', data))

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
    author_info = self.request.get('author').split('|')
        
    if self.request.get('key'):
      post = db.get(db.Key(self.request.get('key'))) 
      post.title=self.request.get('title')
      post.image=self.request.get('image')
      post.markup=self.request.get('ta')
      post.preview = self.extract_preview(post.markup)
      post.author_permalink=author_info[0]
      post.author_name=author_info[1]
    else:  
      post = models.BlogPost(title=self.request.get('title'),
                 markup=self.request.get('ta'),
                 image=self.request.get('image'),
                 author_permalink=author_info[0],
                 author_name=author_info[1])
      month = str(post.created_at.month)
      if len(month) == 1:
        month = '0' + month
      day = str(post.created_at.day)
      if len(day) == 1:
        day = '0' + day
        
      post.permalink = '/' + str(post.created_at.year) + '/' + month + '/' + day + '/' + re.sub('[^a-z0-9]', '-', post.title.lower()) + '/'
      post.preview = self.extract_preview(post.markup)
    post.put()
    self.redirect('/admin', permanent=False)
    
class CreateFeaturePostHandler(webapp.RequestHandler):
  def post(self):
    if self.request.get('key'):
      feature           = db.get(db.Key(self.request.get('key'))) 
      feature.title     = self.request.get('title')
      feature.image     = self.request.get('image')
      feature.preview   = self.request.get('ta')
      feature.permalink = self.request.get('permalink')
    else:  
      feature = models.Feature(title=self.request.get('title'),
                 preview=self.request.get('ta'),
                 image=self.request.get('image'),
                 permalink=self.request.get('permalink'))
    feature.put()
    self.redirect('/admin', permanent=False)
    
class CreateAuthorPostHandler(webapp.RequestHandler):
  def post(self):
    author = models.Author(author_name=self.request.get('name'),
                 author_permalink=self.request.get('permalink'))
    author.put()
    self.redirect('/admin', permanent=False)    
    
def main():
  application = webapp.WSGIApplication([('/admin/create_post', CreatePostHandler),
                                        ('/admin/create', CreateHandler),
                                        ('/admin/create_feature', CreateFeatureHandler),
                                        ('/admin/create_feature_post', CreateFeaturePostHandler),
                                        ('/admin/image_post', ImagePostHandler),
                                        ('/admin/image', ImageHandler),
                                        ('/admin/edit_feature.*', EditFeatureHandler),
                                        ('/admin/edit.*', EditHandler),
                                        ('/admin/create_author', CreateAuthorHandler),
                                        ('/admin/create_author_post', CreateAuthorPostHandler),
                                         ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
