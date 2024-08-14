import pkg_resources
from app import *
from modal import *

with app.app_context():
    db.create_all()
    
    # Create roles
    if not Role.query.filter_by(name="admin").first():
        admin_role = datastore.create_role(name="admin", description="I am the admin of the website. I look at stats of the website and manage everything.")
    if not Role.query.filter_by(name="influencer").first():
        datastore.create_role(name="influencer", description="I am a user of this website. I like to use this website.")
    
    db.session.commit()
    
    # Create admin user
    if not Influencer.query.filter_by(email="arinvashisth@gmail.com").first():
        admin = Influencer(
            name="Arin",
            email="arinvashisth@gmail.com",
            password=generate_password_hash("arin2004"),
            niche="Admin",
            category="Admin",

            gender='Male' # Assign the correct role_id
        )
        datastore.add_role_to_user(admin,admin_role)
        db.session.add(admin)
        db.session.commit()
