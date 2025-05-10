from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///safe_travel.db')
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
    address = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(20))
    groups = db.relationship('Group', secondary='user_group', backref='members')
    routines = db.relationship('Routine', back_populates='user')
    is_admin = db.Column(db.Boolean, default=False)
    # In User model
    #given_reviews = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy='dynamic')
    #received_reviews = db.relationship('Review', foreign_keys='Review.reviewed_id', backref='reviewed', lazy='dynamic')
# In User model

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room_no = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='routines')

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

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


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
        if not data['email'].endswith('g.bracu.ac.bd'):
            return "Only BRACU GSuite email addresses are allowed", 400
            
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
    routines = current_user.routines  # Access routines from the logged-in user directly
    return render_template('dashboard.html', groups=groups, routines=routines)


@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    user = current_user  # Get the current logged-in user
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.address = request.form['address']
        user.emergency_contact = request.form['emergency_contact']
        db.session.commit()  # Save the changes to the database

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to the dashboard or another page

    # For GET request, show the profile form with existing data
    return render_template('update_profile.html', user=user)


@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        data = request.form
        # Convert the departure_time string to a datetime object
        departure_time_str = data['departure_time']
        departure_time = datetime.strptime(departure_time_str, '%Y-%m-%dT%H:%M')  # Assuming the format is 'YYYY-MM-DDTHH:MM'

        group = Group(
            name=data['name'],
            destination=data['destination'],
            departure_time=departure_time,
            created_by=current_user.id
        )
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('create_group.html')

@app.route('/delete_group/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)

    # ✅ Only the creator can delete
    if group.created_by != current_user.id:
        flash("You are not authorized to delete this group.", "danger")
        return redirect(url_for('dashboard'))  # Replace 'home' with your actual redirect

    # If your group has a members relationship, clear it first (optional)
    # group.members.clear()

    db.session.delete(group)
    db.session.commit()
    flash("Group deleted successfully.", "success")
    return redirect(url_for('dashboard'))  # Replace with appropriate page

@app.route('/create-routine', methods=['GET', 'POST'])
@login_required
def create_routine():
    if request.method == 'POST':
        day = request.form['day']
        course_name = request.form['course_name']
        start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        location = request.form['location']

        new_routine = Routine(
            day=day,
            course_name=course_name,
            start_time=start_time,
            end_time=end_time,
            location=location,
            user_id=current_user.id
        )

        db.session.add(new_routine)
        db.session.commit()
        flash('Routine created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_routine.html')

@app.route('/delete-routine/<int:routine_id>', methods=['POST'])
@login_required
def delete_routine(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    if routine.user_id != current_user.id:
        flash('You are not authorized to delete this routine.', 'danger')
        return redirect(url_for('dashboard'))

    print(f"Deleting routine: {routine.id}")  # Add for debugging
    db.session.delete(routine)
    db.session.commit()
    flash('Routine deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

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

@app.route('/leave_group/<int:group_id>', methods=['POST'])
@login_required
def leave_group(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user in group.members:
        group.members.remove(current_user)
        db.session.commit()
        flash('You left the group.', 'info')
    else:
        flash('You are not a member of this group.', 'warning')
    return redirect(url_for('dashboard'))

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

@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    review = Review(
        reviewer_id=current_user.id,
        reviewed_id=request.form['reviewed_id'],
        group_id=request.form['group_id'],
        rating=int(request.form['rating']),
        comment=request.form['comment']
    )
    db.session.add(review)
    db.session.commit()
    flash("Review submitted successfully!", "success")
    return redirect(url_for('group_detail', group_id=request.form['group_id']))

@app.route('/my_reviews')
@login_required
def my_reviews():
    reviews = Review.query.filter_by(reviewed_id=current_user.id).order_by(Review.timestamp.desc()).all()

    local_tz = timezone('Asia/Dhaka')  # Use your local timezone

#Convert UTC timestamp to local time for display
    for review in reviews:
        if review.timestamp:
            review.local_time = review.timestamp.replace(tzinfo=timezone('UTC')).astimezone(local_tz)

    return render_template('my_reviews.html', reviews=reviews)

if __name__ == '__main__':
    with app.app_context():
        print("Creating tables...") 
        db.create_all()
    app.run(debug=True)
