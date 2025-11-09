#!/usr/bin/env python3
"""
Create test workshops for Flowcase/Nalabo
"""

from __init__ import db, create_app
from models.workshop import Workshop

def create_test_workshops():
    """Create sample workshops for testing"""
    
    workshops = [
        {
            "id": "docker-basics",
            "display_name": "Docker Basics",
            "description": "Learn the fundamentals of Docker containers and images",
            "difficulty": "beginner",
            "duration": 60,
            "droplet_id": "ubuntu-ssh",
            "instructions": "# Docker Basics Workshop\n\n## Objectives\n- Understand Docker concepts\n- Learn basic Docker commands\n- Create your first container\n\n## Steps\n1. Introduction to containers\n2. Docker CLI basics\n3. Working with images\n4. Running containers\n5. Managing containers",
            "is_active": True
        },
        {
            "id": "python-web-dev",
            "display_name": "Python Web Development",
            "description": "Build a simple web application with Flask",
            "difficulty": "intermediate",
            "duration": 120,
            "droplet_id": "vscode-server",
            "instructions": "# Python Web Development Workshop\n\n## Objectives\n- Set up Flask environment\n- Create routes and views\n- Work with templates\n- Deploy application\n\n## Steps\n1. Environment setup\n2. Hello World app\n3. Adding routes\n4. Template rendering\n5. Database integration",
            "is_active": True
        },
        {
            "id": "data-science-intro",
            "display_name": "Introduction to Data Science",
            "description": "Get started with data analysis using Jupyter notebooks",
            "difficulty": "beginner",
            "duration": 90,
            "droplet_id": "jupyter-notebook",
            "instructions": "# Data Science Introduction\n\n## Objectives\n- Learn Jupyter basics\n- Work with pandas\n- Create visualizations\n- Basic statistics\n\n## Steps\n1. Jupyter interface\n2. Loading data\n3. Data exploration\n4. Creating plots\n5. Statistical analysis",
            "is_active": True
        },
        {
            "id": "linux-admin",
            "display_name": "Linux Administration",
            "description": "Master essential Linux system administration tasks",
            "difficulty": "advanced",
            "duration": 180,
            "droplet_id": "ubuntu-ssh",
            "instructions": "# Linux Administration Workshop\n\n## Objectives\n- User management\n- File permissions\n- System monitoring\n- Network configuration\n- Security basics\n\n## Steps\n1. User and group management\n2. File system permissions\n3. Process management\n4. Network configuration\n5. Security hardening",
            "is_active": True
        },
        {
            "id": "web-hosting",
            "display_name": "Web Hosting with Nginx",
            "description": "Deploy and configure a web server with Nginx",
            "difficulty": "intermediate",
            "duration": 75,
            "droplet_id": "nginx-webserver",
            "instructions": "# Web Hosting Workshop\n\n## Objectives\n- Configure Nginx\n- Set up virtual hosts\n- SSL certificates\n- Reverse proxy\n\n## Steps\n1. Nginx installation\n2. Basic configuration\n3. Virtual hosts setup\n4. SSL configuration\n5. Performance tuning",
            "is_active": True
        },
        {
            "id": "database-fundamentals",
            "display_name": "Database Fundamentals",
            "description": "Learn SQL and database design with PostgreSQL",
            "difficulty": "beginner",
            "duration": 90,
            "droplet_id": "postgresql-db",
            "instructions": "# Database Fundamentals\n\n## Objectives\n- SQL basics\n- Database design\n- Queries and joins\n- Indexes and optimization\n\n## Steps\n1. Introduction to databases\n2. Creating tables\n3. CRUD operations\n4. Joins and relationships\n5. Performance optimization",
            "is_active": True
        },
        {
            "id": "nodejs-api",
            "display_name": "Building REST APIs with Node.js",
            "description": "Create a RESTful API using Node.js and Express",
            "difficulty": "intermediate",
            "duration": 120,
            "droplet_id": "node-dev",
            "instructions": "# Node.js API Workshop\n\n## Objectives\n- Express framework\n- REST principles\n- Authentication\n- Database integration\n\n## Steps\n1. Express setup\n2. Creating routes\n3. Middleware\n4. Authentication\n5. Database connection",
            "is_active": True
        },
        {
            "id": "desktop-customization",
            "display_name": "Linux Desktop Customization",
            "description": "Customize your Ubuntu desktop environment",
            "difficulty": "beginner",
            "duration": 45,
            "droplet_id": "ubuntu-desktop-vnc",
            "instructions": "# Desktop Customization Workshop\n\n## Objectives\n- Desktop environments\n- Themes and icons\n- Productivity tools\n- Shortcuts\n\n## Steps\n1. Desktop overview\n2. Installing themes\n3. Customizing panels\n4. Adding widgets\n5. Keyboard shortcuts",
            "is_active": True
        }
    ]
    
    # Create each workshop
    for workshop_data in workshops:
        # Check if workshop already exists
        existing = Workshop.query.filter_by(id=workshop_data['id']).first()
        if not existing:
            workshop = Workshop(**workshop_data)
            db.session.add(workshop)
            print(f"✅ Created workshop: {workshop_data['display_name']}")
        else:
            print(f"⚠️  Workshop already exists: {workshop_data['display_name']}")
    
    # Commit changes
    db.session.commit()
    print("\n✅ Test workshops created successfully!")
    print("📝 Available workshops:")
    print("   - Beginner: Docker Basics, Data Science, Desktop Customization, Database")
    print("   - Intermediate: Python Web Dev, Web Hosting, Node.js API")
    print("   - Advanced: Linux Administration")

if __name__ == "__main__":
    # Create app context
    app = create_app()
    
    with app.app_context():
        print("🚀 Creating test workshops for Flowcase/Nalabo...")
        create_test_workshops()
