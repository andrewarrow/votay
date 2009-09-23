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
    
class AtomHandler(webapp.RequestHandler):
  def get(self):

    data = util.getRecentBlogPosts(1)
    
    posts = data['posts']
    data.update({'most_recent': ''})
    if len(posts) > 0:
      data.update({'most_recent': posts[0].rfc3339_created_at()})

    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write(template.render('views/atom.xml', data))
    
def main():
  application = webapp.WSGIApplication([('/atom.xml', AtomHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
