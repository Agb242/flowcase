#!/usr/bin/env python3
"""
Script pour créer les templates de workshops par défaut dans Nalabo
Ce script insère des templates prédéfinis pour différents métiers
"""

import sys
import os
import json
from datetime import datetime

# Ajouter le répertoire courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db
from models.user import User, Group
from models.workshop import WorkshopTemplate, Workshop, UserWorkshop
from models.tenant import Tenant
from utils.permissions import *
from models.log import Log

def create_default_templates():
    """Crée les templates de workshops par défaut"""
    
    app = create_app()
    
    with app.app_context():
        # Vérifier s'il y a déjà des templates
        # existing_templates = WorkshopTemplate.query.count()
        # if existing_templates > 0:
        #     print(f"⚠️  {existing_templates} templates existent déjà. Supprimez-les d'abord pour recréer les templates par défaut.")
        #     return
        
        print("🚀 Création des templates de workshops par défaut...")
        
        # Créer un utilisateur admin pour les templates
        admin_user = User.query.filter(User.username == 'admin').first()
        if not admin_user:
            print("👤 Création d'un utilisateur admin...")
            from models.user import Group
            admin_user = User(
                username='admin',
                email='admin@nalabo.com',
                password='admin123',  # Pour démo uniquement
                auth_token='demo_token',
                groups='admin',
                tenant_id=None
            )
            db.session.add(admin_user)
            
            # Créer le groupe admin
            admin_group = Group(
                display_name='admin',
                protected=True,
                perm_admin_panel=True,
                perm_view_users=True,
                perm_edit_users=True,
                perm_view_groups=True,
                perm_edit_groups=True,
                perm_view_droplets=True,
                perm_edit_droplets=True,
                perm_view_instances=True,
                perm_edit_instances=True,
                perm_view_registry=True,
                perm_edit_registry=True,
                # Workshop permissions
                perm_view_workshops=True,
                perm_edit_workshops=True,
                perm_create_workshops=True,
                perm_manage_templates=True,
                perm_view_workshop_instances=True
            )
            db.session.add(admin_group)
            
            db.session.commit()
            print("✅ Utilisateur admin créé avec succès!")
        else:
            print(f"👤 Utilisateur admin trouvé: {admin_user.username}")
        
        # Templates prédéfinis
        templates_data = [
            {
                "name": "Formation Docker Avancée",
                "description": "Atelier pratique pour maîtriser Docker : conteneurisation, orchestration, et bonnes pratiques DevOps.",
                "category": "DevOps",
                "estimated_duration": 120,
                "thumbnail": "/static/img/workshops/docker-workshop.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 2,
                        "memory": "4GB",
                        "storage": "20GB"
                    },
                    "software": [
                        "docker",
                        "docker-compose",
                        "kubectl",
                        "helm"
                    ],
                    "ports": [8080, 3000, 5000],
                    "environment": {
                        "DOCKER_BUILDKIT": "1",
                        "COMPOSE_DOCKER_CLI_BUILD": "1"
                    },
                    "preinstalled_images": [
                        "nginx:alpine",
                        "redis:alpine",
                        "postgres:13"
                    ]
                }
            },
            {
                "name": "Sécurité Web et Pentesting",
                "description": "Découvrez les vulnérabilités web courantes et apprenez les techniques de pentesting éthique.",
                "category": "Sécurité",
                "estimated_duration": 180,
                "thumbnail": "/static/img/workshops/security-workshop.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 2,
                        "memory": "4GB",
                        "storage": "30GB"
                    },
                    "software": [
                        "burpsuite",
                        "sqlmap",
                        "nmap",
                        "metasploit"
                    ],
                    "ports": [80, 443, 8080, 9090],
                    "environment": {
                        "DISPLAY": ":0"
                    },
                    "vulnerable_apps": [
                        "dvwa",
                        "webgoat",
                        "juice-shop"
                    ]
                }
            },
            {
                "name": "Cloud AWS Foundations",
                "description": "Initiation pratique aux services cloud AWS : EC2, S3, VPC, et architecture cloud moderne.",
                "category": "Cloud",
                "estimated_duration": 150,
                "thumbnail": "/static/img/workshops/aws-workshop.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 2,
                        "memory": "4GB",
                        "storage": "25GB"
                    },
                    "software": [
                        "aws-cli",
                        "terraform",
                        "kubectl"
                    ],
                    "ports": [22, 80, 443],
                    "environment": {
                        "AWS_DEFAULT_REGION": "us-west-2"
                    },
                    "services": ["ec2", "s3", "vpc", "rds"]
                }
            },
            {
                "name": "Développement Full-Stack JavaScript",
                "description": "Créez une application web complète avec Node.js, React, et base de données moderne.",
                "category": "Développement",
                "estimated_duration": 200,
                "thumbnail": "/static/img/workshops/js-workshop.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 2,
                        "memory": "4GB",
                        "storage": "20GB"
                    },
                    "software": [
                        "nodejs",
                        "npm",
                        "yarn",
                        "git"
                    ],
                    "ports": [3000, 5000, 27017],
                    "environment": {
                        "NODE_ENV": "development"
                    },
                    "frameworks": [
                        "express",
                        "react",
                        "mongodb"
                    ]
                }
            },
            {
                "name": "Data Science avec Python",
                "description": "Analyse de données et machine learning avec Python, Pandas, NumPy, et Jupyter Notebooks.",
                "category": "Data Science",
                "estimated_duration": 160,
                "thumbnail": "/static/img/workshops/data-science-workshop.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 2,
                        "memory": "4GB",
                        "storage": "25GB"
                    },
                    "software": [
                        "python3",
                        "jupyter",
                        "pip",
                        "git"
                    ],
                    "ports": [8888, 5000],
                    "environment": {
                        "PYTHONPATH": "/opt/workspace"
                    },
                    "libraries": [
                        "pandas",
                        "numpy",
                        "matplotlib",
                        "scikit-learn",
                        "seaborn"
                    ]
                }
            },
            {
                "name": "Formation Cybersécurité Offensive",
                "description": "Techniques d'attaque et de défense en cybersécurité, analyse de malwares et forensics.",
                "category": "Sécurité",
                "estimated_duration": 240,
                "thumbnail": "/static/img/workshops/cyber-offensive.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 4,
                        "memory": "8GB",
                        "storage": "40GB"
                    },
                    "software": [
                        "wireshark",
                        "volatility",
                        "john",
                        "hashcat"
                    ],
                    "ports": [22, 80, 443, 8080],
                    "environment": {
                        "DISPLAY": ":0"
                    },
                    "tools": [
                        "cuckoo",
                        "yara",
                        "malfind"
                    ]
                }
            },
            {
                "name": "Kubernetes et Orchestration",
                "description": "Maîtrisez Kubernetes : déploiement, scaling, monitoring, et gestion de clusters.",
                "category": "DevOps",
                "estimated_duration": 180,
                "thumbnail": "/static/img/workshops/k8s-workshop.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 2,
                        "memory": "4GB",
                        "storage": "20GB"
                    },
                    "software": [
                        "kubectl",
                        "helm",
                        "docker",
                        "k3s"
                    ],
                    "ports": [80, 443, 8080, 3000],
                    "environment": {
                        "KUBECONFIG": "/home/user/.kube/config"
                    },
                    "cluster_config": {
                        "nodes": 3,
                        "master": 1
                    }
                }
            },
            {
                "name": "Machine Learning Avancé",
                "description": "Deep learning, réseaux de neurones, et frameworks ML modernes avec TensorFlow et PyTorch.",
                "category": "Data Science",
                "estimated_duration": 220,
                "thumbnail": "/static/img/workshops/ml-workshop.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 4,
                        "memory": "8GB",
                        "storage": "30GB"
                    },
                    "software": [
                        "python3",
                        "jupyter",
                        "pip",
                        "git"
                    ],
                    "ports": [8888, 6006],
                    "environment": {
                        "CUDA_VISIBLE_DEVICES": "0"
                    },
                    "ml_frameworks": [
                        "tensorflow",
                        "pytorch",
                        "keras"
                    ]
                }
            },
            {
                "name": "Formation Linux Administration",
                "description": "Administration système Linux : gestion des services, sécurité, scripting bash, et monitoring.",
                "category": "Formation",
                "estimated_duration": 140,
                "thumbnail": "/static/img/workshops/linux-admin.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 2,
                        "memory": "2GB",
                        "storage": "15GB"
                    },
                    "software": [
                        "bash",
                        "vim",
                        "git",
                        "systemd"
                    ],
                    "ports": [22, 80, 443],
                    "environment": {
                        "SHELL": "/bin/bash"
                    },
                    "services": ["ssh", "nginx", "postgresql"]
                }
            },
            {
                "name": "Architecture Microservices",
                "description": "Design patterns pour microservices, API Gateway, Service Mesh, et observabilité.",
                "category": "Développement",
                "estimated_duration": 190,
                "thumbnail": "/static/img/workshops/microservices.jpg",
                "config_schema": {
                    "resources": {
                        "cpu": 2,
                        "memory": "4GB",
                        "storage": "20GB"
                    },
                    "software": [
                        "docker",
                        "docker-compose",
                        "kubectl"
                    ],
                    "ports": [8000, 8001, 8002, 9000],
                    "environment": {
                        "ENV": "development"
                    },
                    "services": [
                        "user-service",
                        "order-service",
                        "payment-service",
                        "api-gateway"
                    ]
                }
            }
        ]
        
        # Créer les templates
        created_templates = []
        for template_data in templates_data:
            try:
                template = WorkshopTemplate(
                    name=template_data["name"],
                    description=template_data["description"],
                    category=template_data["category"],
                    estimated_duration=template_data["estimated_duration"],
                    thumbnail=template_data["thumbnail"],
                    created_by=admin_user.id
                )
                
                # Utiliser la méthode setter pour le config_schema
                template.set_config_schema(template_data["config_schema"])
                
                db.session.add(template)
                created_templates.append(template)
                print(f"✅ Template créé: {template_data['name']}")
                
            except Exception as e:
                print(f"❌ Erreur lors de la création du template {template_data['name']}: {str(e)}")
        
        try:
            db.session.commit()
            print(f"\n🎉 {len(created_templates)} templates de workshops créés avec succès!")
            
            # Afficher un résumé
            print("\n📋 Résumé des templates créés:")
            print("=" * 50)
            for template in created_templates:
                print(f"🔹 {template.name} ({template.category}) - {template.estimated_duration} min")
            
            # Statistiques par catégorie
            categories = {}
            for template in created_templates:
                categories[template.category] = categories.get(template.category, 0) + 1
            
            print("\n📊 Répartition par catégorie:")
            for category, count in categories.items():
                print(f"   {category}: {count} template(s)")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la sauvegarde: {str(e)}")

def add_sample_workshops():
    """Ajoute des exemples de workshops pour demonstration"""
    
    app = create_app()
    
    with app.app_context():
        print("\n🚀 Ajout d'exemples de workshops...")
        
        # Trouver un utilisateur admin pour les exemples
        admin_user = User.query.filter(User.username == 'admin').first()
        if not admin_user:
            print("⚠️  Utilisateur admin non trouvé, création d'exemples avec utilisateur demo...")
            admin_user = User.query.first()
        
        if not admin_user:
            print("❌ Aucun utilisateur trouvé pour créer des exemples")
            return
        
        # Template Docker
        docker_template = WorkshopTemplate.query.filter_by(name="Formation Docker Avancée").first()
        if docker_template:
            sample_workshop = Workshop(
                name="Mon Atelier Docker",
                description="Exemple d'atelier Docker pour démonstration",
                template=docker_template,
                created_by=admin_user.id,
                status="ready"
            )
            
            db.session.add(sample_workshop)
            print("✅ Exemple d'atelier Docker créé")
        
        # Template Sécurité
        security_template = WorkshopTemplate.query.filter_by(name="Sécurité Web et Pentesting").first()
        if security_template:
            sample_workshop2 = Workshop(
                name="Formation Pentesting Demo",
                description="Exemple d'atelier de sécurité",
                template=security_template,
                created_by=admin_user.id,
                status="ready"
            )
            
            db.session.add(sample_workshop2)
            print("✅ Exemple d'atelier Sécurité créé")
        
        try:
            db.session.commit()
            print("\n🎉 Exemples de workshops créés!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la création des exemples: {str(e)}")

if __name__ == "__main__":
    print("=== Création des Templates de Workshops Nalabo ===")
    print("Ce script va créer des templates prédéfinis pour différents métiers")
    print()
    
    create_default_templates()
    add_sample_workshops()
    
    print("\n✨ Processus terminé!")
    print("Les templates sont maintenant disponibles dans l'interface admin.")