import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
import models
import util
import urllib

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
    
    self.response.headers['Cache-Control'] = 'public, max-age=900000'
    self.response.headers.add_header("Expires", "Thu, 01 Dec 2014 16:00:00 GMT")
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
    
    title = 'Andrew Arrow'
    if permalink[0:-1] == 'guest-author':
      title = 'Guest Author'
    data = { 'title': title }

    query = db.GqlQuery('SELECT * FROM BlogPost WHERE author_permalink = :1 ORDER BY created_at', permalink[0:-1])
    posts = query.fetch(5)        
    data.update({'posts': posts})    
    self.response.out.write(template.render('views/author.html', data))    

class MainHandler(webapp.RequestHandler):
  def template_data(self, page):
    data = { 'title': 'Open Source Blogging Software for Google App Engine',
             'next_page': page+1}    
        
    features = memcache.get('features')
    if features is None:
      query = db.GqlQuery('SELECT * FROM Feature ORDER BY created_at')
      features = query.fetch(3)
      memcache.add('features', features)
 
    data.update(util.getRecentBlogPosts(page))        
    data.update({'features': features})
    return data

  def get(self,path):
    if len(path) > 0:
      util.send404(self)
      return
      
    self.response.out.write(template.render('views/index.html', self.template_data(1)))

class MainHandlerWithPageNumber(MainHandler):
  def get(self,page):
    if util.missingTrailingSlash(self):
      return 
    int_page = int(page);
    if int_page < 2:
      util.send404(self)
      return    
    data = self.template_data(int_page)
    
    if len(data['posts']) == 0:
      util.send404(self)
      return    
    
    self.response.out.write(template.render('views/index.html', data))

class BlogPostHandler(webapp.RequestHandler):
  def post(self,year,month,day,title):
    user = users.get_current_user()
    comment = models.Comment(text=self.request.get('ta'),
                             blog_post_key=self.request.get('key'),
                             user_id=user.user_id(),
                             email=user.email(),
                             replied_to_key=self.request.get('replied_to_key'),
                             is_admin=False)    
    comment.put()
                             
    self.redirect(self.request.uri, permanent=False)
    
  def get(self,year,month,day,title):
    if util.missingTrailingSlash(self):
      return
    user = users.get_current_user() 
      
    permalink = ''.join(['/', year, '/', month, '/', day, '/', title])
    
    post = util.loadBlogPost(permalink)
    
    if post is None:    
      util.send404(self)
      return
 
    query = db.GqlQuery("SELECT * FROM Comment WHERE blog_post_key = :1 and replied_to_key = '' ORDER BY created_at", str(post.key()))
    comments = query.fetch(20)
    for comment in comments:
      query = db.GqlQuery("SELECT * FROM Nickname WHERE user_id = :1", comment.user_id)
      nickname = query.fetch(1)
      
      if len(nickname) == 0:
        comment.nickname = 'Anonymous'
        if user and comment.user_id == user.user_id():
          comment.set_name_link = '<a style="color: blue" rel="nofollow" href="/set-name?'+urllib.urlencode({'return_url':self.request.uri})+'">(set your name)</a>'
      else:
        nickname = nickname[0]
        comment.nickname = nickname.nickname
        comment.url = nickname.url

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
                                        ('/page/(\d*)/*', MainHandlerWithPageNumber),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
