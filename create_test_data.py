from app import app, db, User, Group, Routine, UserGroup, Message
from werkzeug.security import generate_password_hash
from datetime import datetime, time

# Run this script while in the Flask application context
with app.app_context():
    # Clear existing data (optional - comment out if you want to keep existing data)
    Message.query.delete()
    UserGroup.query.delete()
    Routine.query.delete()
    Group.query.delete()
    User.query.delete()
    
    print("Creating test data...")
    
    # Create test users
    users = [
        User(
            email="student1@g.bracu.ac.bd",
            password=generate_password_hash("password123", method='pbkdf2:sha256'),
            name="Alex Johnson"
        ),
        User(
            email="student2@g.bracu.ac.bd",
            password=generate_password_hash("password123", method='pbkdf2:sha256'),
            name="Maya Rahman"
        ),
        User(
            email="student3@g.bracu.ac.bd",
            password=generate_password_hash("password123", method='pbkdf2:sha256'),
            name="Omar Faruk"
        ),
        User(
            email="student4@g.bracu.ac.bd",
            password=generate_password_hash("password123", method='pbkdf2:sha256'),
            name="Priya Ahmed"
        ),
        User(
            email="student5@g.bracu.ac.bd",
            password=generate_password_hash("password123", method='pbkdf2:sha256'),
            name="David Wilson"
        ),
    ]
    
    for user in users:
        db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(users)} users")
    
    # Create travel groups
    groups = [
        Group(
            name="CSE370 Study Group",
            destination="BRACU Main Campus",
            departure_time=datetime(2025, 5, 3, 15, 30),
            created_by=users[0].id
        ),
        Group(
            name="Weekend Meetup",
            destination="Gulshan City Center",
            departure_time=datetime(2025, 5, 5, 10, 0),
            created_by=users[1].id
        ),
        Group(
            name="Library Session",
            destination="Ayesha Abed Library",
            departure_time=datetime(2025, 5, 4, 14, 0),
            created_by=users[2].id
        ),
    ]
    
    for group in groups:
        db.session.add(group)
    
    db.session.commit()
    print(f"Created {len(groups)} groups")
    
    # Add users to groups (UserGroup relationships)
    user_groups = [
        UserGroup(user_id=users[0].id, group_id=groups[0].id),  # Alex in CSE370 Study Group
        UserGroup(user_id=users[1].id, group_id=groups[0].id),  # Maya in CSE370 Study Group
        UserGroup(user_id=users[2].id, group_id=groups[0].id),  # Omar in CSE370 Study Group
        UserGroup(user_id=users[1].id, group_id=groups[1].id),  # Maya in Weekend Meetup
        UserGroup(user_id=users[3].id, group_id=groups[1].id),  # Priya in Weekend Meetup
        UserGroup(user_id=users[0].id, group_id=groups[2].id),  # Alex in Library Session
        UserGroup(user_id=users[2].id, group_id=groups[2].id),  # Omar in Library Session
        UserGroup(user_id=users[4].id, group_id=groups[2].id),  # David in Library Session
    ]
    
    for user_group in user_groups:
        db.session.add(user_group)
    
    db.session.commit()
    print(f"Created {len(user_groups)} user-group relationships")
    
    # Create routines for users
    routines = [
        Routine(
            day="Monday",
            course_name="CSE370 - Database Systems",
            start_time=time(10, 0),
            end_time=time(11, 30),
            room_no="UB30401",
            user_id=users[0].id
        ),
        Routine(
            day="Monday",
            course_name="CSE471 - System Analysis",
            start_time=time(13, 0),
            end_time=time(14, 30),
            room_no="UB40901",
            user_id=users[0].id
        ),
        Routine(
            day="Tuesday",
            course_name="CSE370 - Database Systems",
            start_time=time(14, 0),
            end_time=time(15, 30),
            room_no="UB30401",
            user_id=users[1].id
        ),
        Routine(
            day="Wednesday",
            course_name="CSE423 - Computer Graphics",
            start_time=time(10, 0),
            end_time=time(11, 30),
            room_no="UB21301",
            user_id=users[2].id
        ),
        Routine(
            day="Thursday",
            course_name="CSE471 - System Analysis",
            start_time=time(13, 0),
            end_time=time(14, 30),
            room_no="UB40901",
            user_id=users[3].id
        ),
    ]
    
    for routine in routines:
        db.session.add(routine)
    
    db.session.commit()
    print(f"Created {len(routines)} routines")
    
    # Create messages in groups
    messages = [
        Message(
            content="Hey everyone, are we still meeting tomorrow?",
            timestamp=datetime(2025, 5, 1, 15, 30),
            sender_id=users[0].id,
            group_id=groups[0].id
        ),
        Message(
            content="Yes, I'll be there at the usual time.",
            timestamp=datetime(2025, 5, 1, 15, 35),
            sender_id=users[1].id,
            group_id=groups[0].id
        ),
        Message(
            content="I might be 10 minutes late, but I'll definitely come.",
            timestamp=datetime(2025, 5, 1, 15, 40),
            sender_id=users[2].id,
            group_id=groups[0].id
        ),
        Message(
            content="Let's meet at the main entrance.",
            timestamp=datetime(2025, 5, 1, 16, 0),
            sender_id=users[1].id,
            group_id=groups[1].id
        ),
        Message(
            content="Sounds good to me!",
            timestamp=datetime(2025, 5, 1, 16, 5),
            sender_id=users[3].id,
            group_id=groups[1].id
        ),
        Message(
            content="I've reserved a study room for us.",
            timestamp=datetime(2025, 5, 1, 14, 0),
            sender_id=users[0].id,
            group_id=groups[2].id
        ),
        Message(
            content="Great! Which floor?",
            timestamp=datetime(2025, 5, 1, 14, 10),
            sender_id=users[2].id,
            group_id=groups[2].id
        ),
        Message(
            content="3rd floor, room 305.",
            timestamp=datetime(2025, 5, 1, 14, 15),
            sender_id=users[0].id,
            group_id=groups[2].id
        ),
    ]
    
    for message in messages:
        db.session.add(message)
    
    db.session.commit()
    print(f"Created {len(messages)} messages")
    
    print("Test data creation complete!")