from extensions import db
from datetime import datetime

class UserAccount(db.Model):
    __tablename__ = "users"

    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Cycle(db.Model):
    __tablename__ = "cycles"

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_period  = db.Column(db.Date, nullable=False)
    cycle_length = db.Column(db.Integer, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)