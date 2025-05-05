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
    is_admin = db.Column(db.Boolean, default=False)  # Add this line
    groups = db.relationship('Group', secondary='user_group', backref='members')
    routines = db.relationship('Routine', back_populates='user')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_to_university = db.Column(db.Boolean, default=True)  # True = going TO uni, False = coming FROM uni
    meeting_point = db.Column(db.String(200), nullable=False)  # Common meeting location (not uni)
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
            password=generate_password_hash(data['password'], method='pbkdf2:sha256'),
            name=data['name'],
            is_admin=False  # Add this line
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

# @app.route('/create_group', methods=['GET', 'POST'])
# @login_required
# def create_group():
#     if request.method == 'POST':
#         data = request.form
#         # Convert the departure_time string to a datetime object
#         departure_time_str = data['departure_time']
#         departure_time = datetime.strptime(departure_time_str, '%Y-%m-%dT%H:%M')  # Assuming the format is 'YYYY-MM-DDTHH:MM'

#         group = Group(
#             name=data['name'],
#             destination=data['destination'],
#             departure_time=departure_time,
#             created_by=current_user.id
#         )
#         db.session.add(group)
#         db.session.commit()
#         return redirect(url_for('dashboard'))
    
#     return render_template('create_group.html')

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        data = request.form
        departure_time = datetime.strptime(data['departure_time'], '%Y-%m-%dT%H:%M')

        # Get the meeting point from the form
        meeting_point = data['meeting_point']
        
        # Create the group
        group = Group(
            name=data['name'],
            is_to_university=(data.get('journey_type', 'to_university') == 'to_university'),
            meeting_point=meeting_point,
            departure_time=departure_time,
            created_by=current_user.id
        )
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('create_group.html')

@app.route('/group/<int:group_id>/route')
@login_required
def group_route(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Set BRAC University's address
    brac_university = "BRAC University, 66 Mohakhali, Dhaka 1212, Bangladesh"
    
    # Determine start and end based on journey direction
    if group.is_to_university:
        start_location = group.meeting_point
        end_location = brac_university
    else:
        start_location = brac_university
        end_location = group.meeting_point
    
    return render_template('group_route.html', 
                          group=group, 
                          start_location=start_location,
                          end_location=end_location)

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

def create_admin_if_not_exists():
    admin_email = 'iqbal@safetravel.com'
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            password=generate_password_hash('password123', method='pbkdf2:sha256'),
            name='Administrator',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    else:
        # Ensure this user is marked as admin (in case it was created without admin flag)
        if not admin.is_admin:
            admin.is_admin = True
            db.session.commit()
            print("Existing admin account updated with admin privileges.")
        else:
            print("Admin user already exists.")

    # Security check - ensure no other users have admin privileges
    unauthorized_admins = User.query.filter(User.is_admin == True, User.email != admin_email).all()
    if unauthorized_admins:
        for user in unauthorized_admins:
            user.is_admin = False
        db.session.commit()
        print(f"Removed admin privileges from {len(unauthorized_admins)} unauthorized users.")

if __name__ == '__main__':
    with app.app_context():
        print("Creating tables...") 
        db.create_all()
        create_admin_if_not_exists()  # Added this line
    app.run(debug=True)
