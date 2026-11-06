from werkzeug.security import check_password_hash, generate_password_hash
from website import db
from sqlalchemy.sql import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TTData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_code = db.Column(db.Integer)
    dept_p = db.Column(db.String(30))
    dept_a = db.Column(db.String(30))
    odd_even = db.Column(db.String(30))
    semester = db.Column(db.String(30))
    ltpr = db.Column(db.String(30))
    subject = db.Column(db.String(30))
    weekday = db.Column(db.String(30))
    slot = db.Column(db.String(30))
    count = db.Column(db.String(30))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
