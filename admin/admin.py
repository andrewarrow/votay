import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
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

class CreatePostHandler(webapp.RequestHandler):
  def post(self):
    bp = models.BlogPost(title='This is a test title',
                 markup='More testing',
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
                                         ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
