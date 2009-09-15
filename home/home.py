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
    data = { 'title': 'Home' }
    
    query = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created_at")
    list = query.fetch(20)
    
    data.update({'list': list})
    self.response.out.write(template.render('views/index.html', data))
    
def main():
  application = webapp.WSGIApplication([('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
