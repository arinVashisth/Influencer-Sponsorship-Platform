from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user,login_required, logout_user,current_user
from flask_security import UserMixin,RoleMixin
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
roles_users = db.Table('roles_users',
    db.Column('influencer_id', db.Integer, db.ForeignKey('influencer.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.role_id'))
)

class Role(db.Model, RoleMixin):
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    def _repr_(self):
        return f"Role('{self.name}')"

class Influencer(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    reach = db.Column(db.Integer, nullable=False, default=0)
    gender = db.Column(db.String(10), nullable=False)
    profile = db.Column(db.Text, nullable=True)
    posts = db.relationship('Post', backref='influencer', lazy=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, default=str(uuid.uuid4()))
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)
    followers = db.relationship('Follower', foreign_keys='Follower.following_id', backref='following_influencer', lazy='dynamic')
    following = db.relationship('Follower', foreign_keys='Follower.follower_id', backref='follower_influencer', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    approval = db.Column(db.Integer, nullable=False, default=0)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.Integer, nullable=False, default=0)
    goals = db.Column(db.Text, nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    inappropriate = db.Column(db.Boolean, default=False)

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="Pending")
    conversation = db.Column(db.Text, nullable=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    comments = db.Column(db.Text, nullable=True)
    media_type = db.Column(db.String(10), nullable=False)
    media_url = db.Column(db.String(255), nullable=False)
    inappropriate = db.Column(db.Boolean, default=False)


class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)