#!/usr/bin/env python3
"""
Script temporaire pour initialiser la base de données
"""

import sys
import os

# Ajouter le répertoire courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db

def init_database():
    """Initialise la base de données"""
    app = create_app()
    
    with app.app_context():
        db.create_all()
        print("✅ Base de données initialisée avec succès!")

if __name__ == "__main__":
    init_database()