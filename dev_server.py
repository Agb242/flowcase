#!/usr/bin/env python3
"""
Script de développement pour lancer l'application Flask
"""

import sys
import os

# Ajouter le répertoire courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app

def run_dev_server():
    """Lance le serveur de développement"""
    app = create_app({'DEBUG': True})
    
    print("🚀 Lancement du serveur de développement...")
    print("🌐 Accès: http://localhost:5000")
    print("👤 Connexion avec: admin / admin123")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")

if __name__ == "__main__":
    run_dev_server()