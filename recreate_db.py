#!/usr/bin/env python3
"""
Script pour recréer la base de données avec les nouveaux modèles
"""

import sys
import os

# Ajouter le répertoire courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db

def recreate_database():
    """Recrée la base de données avec les nouveaux modèles"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️  Suppression des tables existantes...")
            db.drop_all()
            print("✅ Tables supprimées")
            
            print("🏗️  Création des nouvelles tables...")
            db.create_all()
            print("✅ Tables créées avec succès!")
            
            print("\n🎉 Base de données recréée avec les nouveaux modèles workshop")
            
        except Exception as e:
            print(f"❌ Erreur lors de la recréation: {str(e)}")

if __name__ == "__main__":
    recreate_database()