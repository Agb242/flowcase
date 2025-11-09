#!/usr/bin/env python3
"""
Create test tenants for Flowcase/Nalabo
"""

from __init__ import db, create_app
from models.tenant import Tenant

def create_test_tenants():
    """Create sample tenants for testing"""
    
    tenants = [
        {
            "id": "default",
            "display_name": "Default Organization",
            "description": "Default tenant for individual users",
            "max_users": 10,
            "max_instances": 20,
            "max_storage_gb": 100,
            "is_active": True
        },
        {
            "id": "acme-corp",
            "display_name": "ACME Corporation",
            "description": "Enterprise tenant for ACME Corp employees",
            "max_users": 50,
            "max_instances": 100,
            "max_storage_gb": 500,
            "is_active": True
        },
        {
            "id": "university",
            "display_name": "Tech University",
            "description": "Academic tenant for university students and staff",
            "max_users": 200,
            "max_instances": 300,
            "max_storage_gb": 1000,
            "is_active": True
        },
        {
            "id": "startup-hub",
            "display_name": "Startup Hub",
            "description": "Shared workspace for startup teams",
            "max_users": 30,
            "max_instances": 50,
            "max_storage_gb": 200,
            "is_active": True
        },
        {
            "id": "research-lab",
            "display_name": "Research Laboratory",
            "description": "Scientific computing and research environment",
            "max_users": 25,
            "max_instances": 75,
            "max_storage_gb": 1000,
            "is_active": True
        },
        {
            "id": "dev-team",
            "display_name": "Development Team",
            "description": "Software development team workspace",
            "max_users": 15,
            "max_instances": 40,
            "max_storage_gb": 150,
            "is_active": True
        },
        {
            "id": "training-center",
            "display_name": "Training Center",
            "description": "Professional training and certification programs",
            "max_users": 100,
            "max_instances": 150,
            "max_storage_gb": 300,
            "is_active": True
        }
    ]
    
    # Create each tenant
    for tenant_data in tenants:
        # Check if tenant already exists
        existing = Tenant.query.filter_by(id=tenant_data['id']).first()
        if not existing:
            tenant = Tenant(**tenant_data)
            db.session.add(tenant)
            print(f"✅ Created tenant: {tenant_data['display_name']}")
        else:
            print(f"⚠️  Tenant already exists: {tenant_data['display_name']}")
    
    # Commit changes
    db.session.commit()
    print("\n✅ Test tenants created successfully!")
    print("📝 Available tenants:")
    for t in tenants:
        print(f"   - {t['display_name']}: {t['max_users']} users, {t['max_instances']} instances")

if __name__ == "__main__":
    # Create app context
    app = create_app()
    
    with app.app_context():
        print("🚀 Creating test tenants for Flowcase/Nalabo...")
        create_test_tenants()
