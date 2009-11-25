from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache
import os

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

def missingTrailingSlash(handler):
  if handler.request.uri.endswith('/'):
    return False
  else:
    handler.redirect(''.join([handler.request.uri, '/']), permanent=True)
    return True
   
def send404(handler):
  handler.error(404)
  handler.response.out.write(template.render(APP_ROOT_DIR + '/home/views/404.html', {}))
  
def getRecentBlogPosts(page):
  data = memcache.get('page_'+str(page))
  if data is None:
    query = db.GqlQuery('SELECT * FROM BlogPost ORDER BY created_at desc')
    per_page = 5
    posts = query.fetch(per_page, per_page*(page-1))
    next_page_count = len(query.fetch(per_page, per_page*page))
  
    for post in posts:
      query = db.GqlQuery('SELECT * FROM ImageMetaData WHERE filename = :1', post.image)
      list = query.fetch(1)
      if len(list) == 1:
        post.imageMeta = list[0]
    data = {'posts': posts, 'next_page_count': next_page_count}
    memcache.add('page_'+str(page), data)

  return data
