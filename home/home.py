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
      
    image = list[0]    
    parts = image.filename.split('.')
    extension = parts[len(parts)-1]
    
    if extension == 'png':
      self.response.headers['Content-Type'] = 'image/png'
    if extension == 'jpeg' or extension == 'jpg':
      self.response.headers['Content-Type'] = 'image/jpeg'
    if extension == 'gif':
      self.response.headers['Content-Type'] = 'image/gif'
    
    self.response.out.write(image.data)

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

class AuthorHandler(webapp.RequestHandler):
  def get(self,permalink):      
    if util.missingTrailingSlash(self):
      return
    data = { 'title':'Andrew Arrow' }    
        
    query = db.GqlQuery('SELECT * FROM BlogPost WHERE author_permalink = :1 ORDER BY created_at', permalink[0:-1])
    posts = query.fetch(20)
    
    for post in posts:
      query = db.GqlQuery('SELECT * FROM ImageMetaData WHERE filename = :1', post.image)
      list = query.fetch(1)
      if len(list) == 1:
        post.imageMeta = list[0]
    
    data.update({'posts': posts})    
    self.response.out.write(template.render('views/author.html', data))    

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    if len(path) > 0:
      util.send404(self)
      return
      
    data = { 'title': 'Open Source Blogging Software for Google App Engine' }    
    
    query = db.GqlQuery('SELECT * FROM Feature ORDER BY created_at')
    features = query.fetch(3)
    
    query = db.GqlQuery('SELECT * FROM BlogPost ORDER BY created_at desc')
    posts = query.fetch(20)
    
    for post in posts:
      query = db.GqlQuery('SELECT * FROM ImageMetaData WHERE filename = :1', post.image)
      list = query.fetch(1)
      if len(list) == 1:
        post.imageMeta = list[0]
    
    data.update({'features': features})
    data.update({'posts': posts})
    self.response.out.write(template.render('views/index.html', data))

class BlogPostHandler(webapp.RequestHandler):
  def post(self,year,month,day,title):
    user = users.get_current_user()
    nickname = user.nickname()
    if (nickname == user.email()):
      nickname = 'Anonymous'
    comment = models.Comment(text=self.request.get('ta'),
                             blog_post_key=self.request.get('key'),
                             user_id=user.user_id(),
                             nickname=nickname,
                             email=user.email(),
                             replied_to_key=self.request.get('replied_to_key'),
                             is_admin=False)    
    comment.put()
                             
    self.redirect(self.request.uri, permanent=False)
    
  def get(self,year,month,day,title):
    if util.missingTrailingSlash(self):
      return
      
    permalink = ''.join(['/', year, '/', month, '/', day, '/', title])
    query = db.GqlQuery('SELECT * FROM BlogPost WHERE permalink = :1', permalink)
    list = query.fetch(1)

    if len(list) == 0:
      util.send404(self)
      return
      
    post = list[0]
     
    query = db.GqlQuery('SELECT * FROM ImageMetaData WHERE filename = :1', post.image)
    list = query.fetch(1)
    if len(list) == 1:
      post.imageMeta = list[0]

    query = db.GqlQuery("SELECT * FROM Comment WHERE blog_post_key = :1 and replied_to_key = '' ORDER BY created_at", str(post.key()))
    comments = query.fetch(20)


    user = users.get_current_user() 
    data = { 'title': post.title, 'user': user, 'comments': comments }
    if not user:
      data.update({'login_url': users.create_login_url(self.request.uri)})
    
    data.update({'post': post})
    self.response.out.write(template.render('views/blog_post.html', data))
    
def main():
  application = webapp.WSGIApplication([('/(\d\d\d\d)/(\d\d)/(\d\d)/(.*)', BlogPostHandler),
                                        ('/(about|advertise|contact)/*', PageHandler),
                                        ('/archives/*', ArchivesHandler),
                                        ('/author/(.*)', AuthorHandler),
                                        ('/blog-image/(.*)', ImageHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
