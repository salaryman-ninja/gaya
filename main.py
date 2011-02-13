import os
import sys

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import models


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.redirect('/oogiri.html')


def main():
    application = webapp.WSGIApplication([('/', MainHandler)], debug = True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
