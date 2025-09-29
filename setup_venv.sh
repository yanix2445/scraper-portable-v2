#!/bin/bash

# Script pour créer et activer un environnement virtuel pour le scraper
# Utilisation: source setup_venv.sh

echo "🔧 Configuration d'un environnement virtuel pour le scraper..."

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Échec de création de l'environnement virtuel"
        return 1
    fi
fi

# Activer l'environnement virtuel
echo "🚀 Activation de l'environnement virtuel..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    echo "✅ Environnement virtuel activé !"
    echo "💡 Vous pouvez maintenant lancer: python portable_scraper.py"
    echo "🔚 Pour désactiver l'environnement plus tard: deactivate"
else
    echo "❌ Échec d'activation de l'environnement virtuel"
    return 1
fi