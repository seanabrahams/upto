# Upto
from google.appengine.api import users
from google.appengine.ext import db


class Author(db.Model):
  user = db.UserProperty(required=True)
  
  def status(self):
    return self.status_set.order('-created_at').get()
    
  def actions(self, limit=3):
    return self.action_set.order('-created_at').fetch(limit)
  
  def colleagues(self):
    return Colleague.gql("WHERE user = :1 AND confirmed = true AND denied = false ORDER BY created_at DESC", self)
    
  def colleague_requests(self):
    return Colleague.gql("WHERE colleague = :1 AND confirmed = false AND denied = false", self)
    
  # Since the django templates don't seem to know how to do comparisons, or 
  # because I'm blind...
  def has_colleague_requests(self):
    if Colleague.gql("WHERE colleague = :1 AND confirmed = false AND denied = false", self).count() > 0:
      return True
    return False
  
class Status(db.Model):
  author = db.ReferenceProperty(Author)
  content = db.TextProperty(required=True)
  created_at = db.DateTimeProperty(auto_now_add=True)
  updated_at = db.DateTimeProperty(auto_now=True)
  
  def set_values(self, request):
    self.content = request.get('content')
  
  def __unicode__(self):
    return unicode(self.content)
 
  def __str__(self):
    return str(self.content)
    
  def html(self):
    return str(self)

class Action(db.Model):
  author = db.ReferenceProperty(Author)
  content = db.TextProperty(required=True)
  created_at = db.DateTimeProperty(auto_now_add=True)
  updated_at = db.DateTimeProperty(auto_now=True)
  
  def set_values(self, request):
    self.content = request.get('content')
  
  def __unicode__(self):
    return unicode(self.content)
 
  def __str__(self):
    return str(self.content)
    
  def html(self):
    return str(self)

class Colleague(db.Model):
  user = db.ReferenceProperty(Author, collection_name="user_set")
  colleague = db.ReferenceProperty(Author, collection_name="colleague_set")
  confirmed = db.BooleanProperty()
  denied = db.BooleanProperty()
  created_at = db.DateTimeProperty(auto_now_add=True)
  updated_at = db.DateTimeProperty(auto_now=True)  