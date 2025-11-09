#!/usr/bin/env python3
"""Create or reset admin password"""
import sys
sys.path.insert(0, '.')

from __init__ import create_app, db, bcrypt
from models.user import User, Group

app = create_app()
with app.app_context():
    # Create admin if doesn't exist
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("🔧 Creating admin user...")
        
        # Get or create Admin group
        admin_group = Group.query.filter_by(display_name='Admin').first()
        if not admin_group:
            admin_group = Group(
                display_name="Admin",
                protected=True,
                perm_admin_panel=True,
                perm_view_instances=True,
                perm_edit_instances=True,
                perm_view_users=True,
                perm_edit_users=True,
                perm_view_droplets=True,
                perm_edit_droplets=True,
                perm_view_registry=True,
                perm_edit_registry=True,
                perm_view_groups=True,
                perm_edit_groups=True
            )
            db.session.add(admin_group)
            db.session.commit()
        
        # Create admin user
        admin = User(
            username='admin',
            password=bcrypt.generate_password_hash('Admin123!').decode('utf-8'),
            groups=admin_group.id,
            auth_token=''.join(__import__('random').choice(__import__('string').ascii_letters + __import__('string').digits) for i in range(80))
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created!")
    else:
        print("🔧 Resetting admin password...")
        admin.password = bcrypt.generate_password_hash('Admin123!').decode('utf-8')
        db.session.commit()
        print("✅ Password reset!")
    
    print("""
╔════════════════════════════════════════╗
║   🔐 CREDENTIALS SUPER ADMIN           ║
╠════════════════════════════════════════╣
║                                        ║
║   Username: admin                      ║
║   Password: Admin123!                  ║
║                                        ║
║   URL: http://localhost:5000           ║
║                                        ║
╚════════════════════════════════════════╝
""")
