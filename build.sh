#!/usr/bin/env bash
# Script de build pour Render

set -o errexit  # Exit on error

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Appliquer les migrations
python manage.py migrate

# Créer le superuser par défaut si aucun utilisateur n'existe
python manage.py create_default_superuser
