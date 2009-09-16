from google.appengine.ext.webapp import template
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