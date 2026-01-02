# 💰 MonNkap

Application collaborative de suivi des dépenses et d'objectifs financiers.

## 🚀 Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Appliquer les migrations :
```bash
python manage.py migrate
```

4. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

5. Lancer le serveur :
```bash
python manage.py runserver
```

## 📁 Structure du projet

- `accounts/` - Gestion des utilisateurs & authentification
- `expenses/` - Gestion des dépenses & catégories
- `goals/` - Objectifs financiers personnels
- `groups/` - Objectifs financiers collaboratifs
- `dashboard/` - Tableaux de bord et statistiques

## 🛠 Stack technique

- **Backend:** Django (Python)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de données:** SQLite (dev) / PostgreSQL (prod)
