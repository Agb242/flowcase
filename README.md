# 🌊 Flowcase - Container Management Platform

## 📋 Vue d'ensemble

Flowcase est une plateforme de gestion de conteneurs Docker avec accès distant via Guacamole (VNC/RDP/SSH) ou HTTP direct. Interface moderne avec architecture Single Page Application.

## 🚀 Démarrage rapide

### 1. Prérequis
- Python 3.8+
- Docker Desktop
- 4GB RAM minimum

### 2. Installation

```bash
# Cloner le repo
git clone https://github.com/yourusername/flowcase.git
cd flowcase

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur
python3 start_dev.py
```

### 3. Accès

- **URL**: http://localhost:5000
- **Admin**: Voir `IDENTIFIANTS.txt` après le premier démarrage

## 🏗️ Architecture

```
flowcase/
├── models/          # Modèles SQLAlchemy
├── routes/          # Blueprints Flask
├── templates/       # Templates HTML
├── static/          # CSS, JS, images
├── utils/           # Utilitaires
└── data/           # Base de données SQLite
```

### Templates principaux

- `login_modern.html` - Page de connexion
- `dashboard_integrated.html` - Dashboard avec tout intégré
- `droplet_modern.html` - Viewer pour instances
- `register.html` - Inscription
- `404.html` - Page d'erreur

### Routes principales

- `/` - Login
- `/dashboard` - Dashboard principal (tout intégré)
- `/droplet/{id}` - Viewer instance
- `/api/droplets` - API liste droplets
- `/api/instance/request` - API créer instance

## 💻 Fonctionnalités

### Dashboard intégré
- **Stats** - Vue d'ensemble système
- **Droplets** - Images Docker disponibles
- **Instances** - Conteneurs actifs
- **Actions** - Start/Stop/Delete sans rechargement

### Types de connexion
- **VNC** - Desktop Linux
- **RDP** - Desktop Windows  
- **SSH** - Terminal
- **HTTP** - Applications web

### Gestion des instances
- Lancement via modal (pas de navigation)
- Actions AJAX en temps réel
- Auto-refresh toutes les 30s
- Monitoring ressources

## 🔧 Configuration

### Base de données
```python
# SQLite par défaut
DATABASE_URL = 'sqlite:///data/flowcase.db'
```

### Docker
```python
# Connexion Docker locale
DOCKER_HOST = 'unix://var/run/docker.sock'
```

### Guacamole
```python
# Serveur Guacamole
GUACAMOLE_URL = 'http://localhost:8080/guacamole'
```

## 📝 Données de test

### Créer des droplets
```bash
python3 create_test_droplets.py
```

### Créer des workshops
```bash
python3 create_test_workshops.py
```

### Créer des tenants
```bash
python3 create_test_tenants.py
```

## 🐳 Docker Compose

### Développement
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up
```

## 🔐 Sécurité

- Mots de passe hashés (Werkzeug)
- Sessions Flask-Login
- Tokens AES pour Guacamole
- CSRF protection
- Permissions par groupes

## 📊 API Endpoints

### Droplets
```
GET  /api/droplets              # Liste droplets
GET  /api/droplets/stats        # Statistiques
```

### Instances
```
POST /api/instance/request      # Créer instance
GET  /api/instances             # Liste instances
POST /api/instances/{id}/start  # Démarrer
POST /api/instances/{id}/stop   # Arrêter
GET  /api/instance/{id}/destroy # Supprimer
```

## 🛠️ Développement

### Structure du code

```python
# models/droplet.py
class Droplet(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    display_name = db.Column(db.String(80))
    droplet_type = db.Column(db.String(80))
    # ...

# routes/droplet.py
@droplet_bp.route('/api/instance/request', methods=['POST'])
@login_required
def request_instance():
    # Créer une instance
    pass
```

### JavaScript principal

```javascript
// static/js/dashboard_integrated.js
loadDroplets()    // Charge les droplets
loadInstances()   // Charge les instances
launchInstance()  // Lance via modal
```

## 🔄 Workflow utilisateur

```
1. LOGIN → Authentification
2. DASHBOARD → Vue complète
   ├── Droplets disponibles
   └── Instances actives
3. LAUNCH → Click droplet → Modal → Create
4. CONNECT → Click instance → Viewer
5. MANAGE → Start/Stop/Delete (AJAX)
```

## 📈 Monitoring

- CPU usage en temps réel
- Memory usage
- Container status
- Activity logs

## 🌐 Environnements

### Local
```bash
python3 start_dev.py
```

### Docker
```bash
docker-compose up
```

### Production
- PostgreSQL au lieu de SQLite
- Redis pour le cache
- Nginx reverse proxy
- SSL/TLS certificates

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

MIT License - voir `LICENSE`

## 📞 Support

- Issues: GitHub Issues
- Email: support@flowcase.io

---

**Version**: 3.0  
**Date**: 2025-11-08  
**Status**: Production Ready
