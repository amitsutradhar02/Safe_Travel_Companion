from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import pymysql
pymysql.install_as_MySQLdb()

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safe_travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    groups = db.relationship('Group', secondary='user_group', backref='members')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class UserGroup(db.Model):
    __tablename__ = 'user_group'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        if not data['email'].endswith('.edu'):
            return "Only educational email addresses are allowed", 400
            
        if User.query.filter_by(email=data['email']).first():
            return "Email already registered", 400
            
        user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),
            name=data['name']
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password, data['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    groups = Group.query.all()
    return render_template('dashboard.html', groups=groups)

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        data = request.form
        group = Group(
            name=data['name'],
            destination=data['destination'],
            departure_time=data['departure_time'],
            created_by=current_user.id
        )
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_group.html')

@app.route('/join_group/<int:group_id>')
@login_required
def join_group(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user not in group.members:
        user_group = UserGroup(user_id=current_user.id, group_id=group_id)
        db.session.add(user_group)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/group/<int:group_id>')
@login_required
def group_detail(group_id):
    group = Group.query.get_or_404(group_id)
    messages = Message.query.filter_by(group_id=group_id).all()
    return render_template('group_detail.html', group=group, messages=messages)

@app.route('/send_message/<int:group_id>', methods=['POST'])
@login_required
def send_message(group_id):
    content = request.form['content']
    message = Message(
        content=content,
        sender_id=current_user.id,
        group_id=group_id,
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('group_detail', group_id=group_id))

if __name__ == '__main__':
    with app.app_context():
        print("Creating tables...") 
        db.create_all()
    app.run(debug=True)
