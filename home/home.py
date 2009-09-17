import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import models
import util

class ImageHandler(webapp.RequestHandler): 
  def get(self,filename):
    query = db.GqlQuery('SELECT * FROM ImageData WHERE filename = :1', filename)
    list = query.fetch(1)

    if len(list) == 0:
      util.send404(self)
      return
      
    self.response.headers['Content-Type'] = 'image/png' 
    self.response.out.write(list[0].data)

class PageHandler(webapp.RequestHandler):
  def get(self,path):      
    if util.missingTrailingSlash(self):
      return
    data = { 'title': path.capitalize() + ' - Open Source Blogging Software for Google App Engine' }    
    self.response.out.write(template.render('views/'+path+'.html', data))
    
class ArchivesHandler(webapp.RequestHandler):
  def get(self):      
    if util.missingTrailingSlash(self):
      return
    data = { 'title':'Archives - Open Source Blogging Software for Google App Engine' }    
    self.response.out.write(template.render('views/archives.html', data))    

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    if len(path) > 0:
      util.send404(self)
      return
      
    data = { 'title': 'Open Source Blogging Software for Google App Engine' }
    
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
                                        ('/(about|advertise|contact)/*', PageHandler),
                                        ('/archives/*', ArchivesHandler),
                                        ('/blog-image/(.*)', ImageHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
