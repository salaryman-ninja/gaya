from google.appengine.ext import db


class Room(db.Model):
  title = db.StringProperty()
  description = db.StringProperty(multiline = True)
  oogiri_name = db.StringProperty()
  oogiri_hash = db.StringProperty()
  question = db.ReferenceProperty() # later to be ReferenceProperty(Question)
  create_user = db.UserProperty()
  create_datetime = db.DateTimeProperty(auto_now_add = True)

class Question(db.Model):
  room = db.ReferenceProperty(Room, required = True)
  content = db.StringProperty(multiline = True)
  oogiri_name = db.StringProperty()
  oogiri_hash = db.StringProperty()
  end_datetime = db.DateTimeProperty()
  create_user = db.UserProperty()
  create_datetime = db.DateTimeProperty(auto_now_add = True)

# Fix Forward Reference
Room.question.reference_class = Question

class Answer(db.Model):
  question = db.ReferenceProperty(Question, required = True)
  content = db.StringProperty(multiline = True)
  oogiri_name = db.StringProperty()
  oogiri_hash = db.StringProperty()
  create_user = db.UserProperty()
  create_datetime = db.DateTimeProperty(auto_now_add = True)
  update_datetime = db.DateTimeProperty(auto_now = True)

class Vote(db.Model):
  answer = db.ReferenceProperty(Answer, required = True)
  rating = db.RatingProperty()
  content = db.StringProperty(multiline = True)
  oogiri_name = db.StringProperty()
  oogiri_hash = db.StringProperty()
  create_user = db.UserProperty()
  create_datetime = db.DateTimeProperty(auto_now_add = True)
