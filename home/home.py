import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import models
import util

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    data = { 'title': 'Home' }
    
    query = db.GqlQuery('SELECT * FROM BlogPost ORDER BY created_at')
    list = query.fetch(20)
    
    data.update({'list': list})
    self.response.out.write(template.render('views/index.html', data))

class BlogPostHandler(webapp.RequestHandler):
  def get(self,year,month,day,title):
    if util.missingTrailingSlash(self):
      return
      
    permalink = ''.join([year, '/', month, '/', day, '/', title])
    query = db.GqlQuery('SELECT * FROM BlogPost WHERE permalink = :1', permalink)
    list = query.fetch(1)

    if len(list) == 0:
      util.send404(self)
      return
     
    data = { 'title': list[0].title }     
    data.update({'post': list[0]})
    self.response.out.write(template.render('views/blog_post.html', data))
    
def main():
  application = webapp.WSGIApplication([('/(\d\d\d\d)/(\d\d)/(\d\d)/(.*)', BlogPostHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
