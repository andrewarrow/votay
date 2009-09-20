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
    
class SetNameHandler(webapp.RequestHandler):
  def post(self):
    self.redirect(self.request.uri, permanent=False)
    
  def get(self):
    if util.missingTrailingSlash(self):
      return
    user = users.get_current_user() 
      
    data = { 'title': 'Set Name' }
    self.response.out.write(template.render('views/set_name.html', data))
    
def main():
  application = webapp.WSGIApplication([('/set-name/*', SetNameHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
