import cgi
import logging
import os
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from upto import *

class MainPage(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()      
    # Users must be logged in
    if current_user:
      # Setup the author object for this user
      author = Author.gql("WHERE user = :1", current_user).get()
      if not author:
        author = Author(user=current_user)
        author.put()
      
      # Doing this because you can't call author.actions(20) from the template  
      author_actions = author.actions(limit=20)
      
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
      
      template_values = {
        'author': author,
        'author_actions': author_actions, 
        'url': url,
        'url_linktext': url_linktext
        }

      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))
    else:
      self.redirect(users.create_login_url(self.request.uri))
          
class ActionPage(webapp.RequestHandler):
  def post(self):
    current_user = users.get_current_user()
    author = Author.gql("WHERE user = :1", current_user).get()
    
    action = Action(author=author, content=cgi.escape(self.request.get('content')))
    #action.set_values(self.request)
    action.put()
	  
    self.redirect('/')

class StatusPage(webapp.RequestHandler):
  def post(self):
    current_user = users.get_current_user()
    author = Author.gql("WHERE user = :1", current_user).get()
    
    status = Status(author=author, content=cgi.escape(self.request.get('content')))
    # status.set_values(self.request)
    status.put()
	  
    self.redirect('/')

class ColleaguePage(webapp.RequestHandler):
  def post(self):
    current_user = users.get_current_user()
    author = Author.gql("WHERE user = :1", current_user).get()
    
    address = cgi.escape(self.request.get('email'))
    
    # Ensure it is a valid account...
    # Right now Google Apps has no way to verify if it is a valid account
    if not mail.is_email_valid(address) or not address.endswith("@gmail.com"):
      self.redirect('/?invalid_email=true')
      return
    else:
      requester = author
      requested_user = Author.gql("WHERE user = :1", users.User(address)).get()
      if not requested_user:
        requested_user = Author(user=users.User(address))
        requested_user.put()
      colleague = Colleague(user=requester, colleague=requested_user)
      colleague.confirmed = False
      colleague.denied = False
      colleague.put()

      # Send email to colleague notifying them of the request
      upto_url = "http://upto.appspot.com"
      sender_address = "upto@fastlightbeautiful.com"
      subject = "Upto Colleague Request from %s" % requester.user.nickname()
      body = """
      %s has requested to be your colleague on Upto.
      
      Upto is an application that enables you track what your colleagues are up to right now and in the recent past.
      
      Login and confirm you know %s
      
      %s
      """ % (requester.user.nickname(), requester.user.nickname(), upto_url)

      mail.send_mail(sender_address, address, subject, body)
    

    self.redirect('/?colleague_request_sent=true')
	  
class ColleagueConfirmPage(webapp.RequestHandler):
  def get(self):
    colleague = Colleague.get(self.request.get('id'))
    colleague.confirmed = True
    colleague.put()
    
    # Must create a colleague where the user is the colleague so that
    # queries for a user's colleagues works.
    colleague_reverse = Colleague(user=colleague.colleague, colleague=colleague.user)
    colleague_reverse.confirmed = True
    colleague_reverse.denied = False
    colleague_reverse.put()

    self.redirect('/?colleague_confirmed=true')
    
class ColleagueDenyPage(webapp.RequestHandler):
  def get(self):
    colleague = Colleague.get(self.request.get('id'))
    colleague.denied = True
    colleague.put()
    
    self.redirect('/?colleague_denied=true')
    
def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage),
                                        ('/action', ActionPage),
                                        ('/status', StatusPage),
                                        ('/colleague', ColleaguePage),
                                        ('/colleague_confirm/', ColleagueConfirmPage),
                                        ('/colleague_deny/', ColleagueDenyPage),
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()