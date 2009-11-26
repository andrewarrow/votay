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

class ExportHandler(webapp.RequestHandler):
  def get(self):

    page = int(self.request.get('p'))
    query = db.GqlQuery('SELECT * FROM BlogPost ORDER BY created_at desc')
    posts = query.fetch(1, page-1)
    
    if len(posts) == 0:
      util.send404(self)
      return    
    
    post = posts[0]
    self.response.headers['Content-Type'] = 'text/plain'    
    self.response.out.write(post.image + '\n')
    self.response.out.write(post.title + '\n')
    self.response.out.write(post.permalink + '\n')
    self.response.out.write(str(post.created_at)[0:10] + '\n')
    self.response.out.write(post.author_permalink + '\n')
    self.response.out.write(post.author_name + '\n')
    self.response.out.write('<markup>\n')
    self.response.out.write(post.markup + '\n')  
    self.response.out.write('</markup>\n')
    
def main():
  application = webapp.WSGIApplication([('/sitemap.xml', SiteMapHandler),
                                        ('/export', ExportHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
