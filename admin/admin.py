import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from datetime import datetime
import util
import os
import sys
import models
import re

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    user = users.get_current_user() 

    data = { 'title': 'Admin',
             'email': user.email() }
        
    query = db.GqlQuery('SELECT * FROM BlogPost ORDER BY created_at desc')
    posts = query.fetch(20)    
    data.update({'posts': posts})

    query = db.GqlQuery('SELECT * FROM Feature ORDER BY created_at desc')
    features = query.fetch(20)    
    data.update({'features': features})
    
    if users.is_current_user_admin():
      self.response.out.write(template.render('views/super_user.html', data))
    else:
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

    if post.published:
      data.update({'published_yes': 'selected="true"'})
    else:
      data.update({'published_no': 'selected="true"'})
    
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
    query = db.GqlQuery('SELECT * FROM ImageMetaData WHERE filename = :1', self.request.get('image'))
    list = query.fetch(1)
    if len(list) == 0:
      self.redirect('/admin', permanent=False)
      return
    imageMeta = list[0]
  
    author_info = self.request.get('author').split('|')
        
    if self.request.get('key'):
      post = db.get(db.Key(self.request.get('key'))) 
      post.title=self.request.get('title')
      post.image=self.request.get('image')
      post.width = imageMeta.width
      post.height = imageMeta.height
      post.markup=self.request.get('ta')
      post.preview = self.extract_preview(post.markup)
      post.author_permalink=author_info[0]
      post.author_name=author_info[1]
      post.published = self.request.get('published') == '1'
    else:
      created_at = datetime.now()
      datestr = self.request.get('created_at')
      if datestr:
        created_at = datetime(int(datestr[0:4]), int(datestr[5:7]), int(datestr[8:10]))
        
      year = str(created_at.year)
      month = str(created_at.month)
      if len(month) == 1:
        month = '0' + month
      day = str(created_at.day)
      if len(day) == 1:
        day = '0' + day
      
      permalink = '/' + year + '/' + month + '/' + day + '/' + re.sub('[^a-z0-9]', '-', self.request.get('title').lower()) + '/'
      
      if util.loadBlogPost(permalink) is not None:
        self.redirect('/admin', permanent=False)
        return
      
      post = models.BlogPost(title=self.request.get('title'),
                 markup=self.request.get('ta'),
                 preview=self.extract_preview(self.request.get('ta')),
                 image=self.request.get('image'),
                 width=imageMeta.width,
                 height=imageMeta.height,
                 created_at=created_at,
                 permalink=permalink,
                 published=False,
                 author_permalink=author_info[0],
                 author_name=author_info[1])

    post.put()
    memcache.delete(post.permalink)
    memcache.delete('p1')
    self.redirect(post.permalink, permanent=False)
    
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
    memcache.delete('features')
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
