import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import models
import util

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    util.send404(self)
    return
    
class SiteMapHandler(webapp.RequestHandler):
  def get(self):

    data = util.getRecentBlogPosts(1)
    
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write(template.render('views/sitemap.xml', data))
    
def main():
  application = webapp.WSGIApplication([('/sitemap.xml', SiteMapHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
