# 🕷️ Scraper Portable - Guide d'Installation et d'Utilisation

## 📦 Contenu du Package

- `portable_scraper.py` - Script principal auto-installable
- `recreate_table.sql` - Script de création de la base de données
- `README.md` - Ce guide d'installation

## 🚀 Installation Rapide

### 1. Prérequis

- **Python 3.7+** (vérifiez avec `python --version`)
- **Connexion Internet** pour l'installation automatique des dépendances
- **Compte Supabase** (gratuit sur [supabase.com](https://supabase.com))

### 2. Configuration de la Base de Données

#### Étape 2.1 : Créer un projet Supabase

1. Allez sur [supabase.com](https://supabase.com)
2. Créez un compte ou connectez-vous
3. Cliquez sur **"New Project"**
4. Choisissez votre organisation
5. Donnez un nom à votre projet (ex: `scraper-portable`)
6. Choisissez un mot de passe sécurisé
7. Sélectionnez une région proche
8. Cliquez sur **"Create new project"**

#### Étape 2.2 : Créer la table

1. Une fois le projet créé, allez dans **"SQL Editor"**
2. Ouvrez le fichier `recreate_table.sql`
3. Copiez tout le contenu
4. Collez-le dans l'éditeur SQL de Supabase
5. Cliquez sur **"Run"** pour exécuter

✅ Votre table `personnes` est maintenant créée !

#### Étape 2.3 : Récupérer les clés d'accès

1. Allez dans **Settings** > **API**
2. Notez ces informations :
   - **URL** : `https://votre-projet.supabase.co`
   - **Clé anon** : `eyJhbGciOiJIUz...` (clé publique)

## 🎯 Utilisation

### Lancement du Script

```bash
python portable_scraper.py
```

### Configuration Interactive

Le script vous demandera :

1. **🔗 URL du site à scraper**
   ```
   Exemple : https://example.com
   ```

2. **📄 Nombre max de pages [50]**
   ```
   Appuyez sur Entrée pour 50, ou tapez un nombre
   ```

3. **🗄️ Configuration Supabase**
   ```
   URL Supabase : https://votre-projet.supabase.co
   Clé Supabase : eyJhbGciOiJIUz...
   ```

4. **📁 Dossier de sauvegarde**
   ```
   1) Répertoire courant
   2) Bureau
   3) Téléchargements
   4) Dossier personnalisé
   ```

### Exemple d'Exécution

```
🚀 Scraper Portable Auto-Installable
========================================
✅ Python 3.9 détecté
🔧 Vérification des dépendances...
  ✅ requests
  ✅ beautifulsoup4
  ✅ lxml
  ✅ supabase
  ✅ spacy
  ✅ python-dotenv
  ✅ Modèle spaCy français
✅ Toutes les dépendances sont prêtes!

🚀 Scraper Portable - Configuration
========================================
🔗 URL du site à scraper: https://example.com
📄 Nombre max de pages [50]: 20
🗄️ Configuration Supabase:
URL Supabase: https://votre-projet.supabase.co
Clé Supabase: eyJhbGciOiJIUz...
✅ Connexion Supabase réussie

🕷️ Début du crawling de https://example.com
📄 Page 1/20: https://example.com
   👥 2 personne(s) trouvée(s)
📄 Page 2/20: https://example.com/about
   👥 1 personne(s) trouvée(s)
...

📊 Résultats: 15 personne(s) trouvée(s)
💾 15 personne(s) sauvegardée(s) en base
📁 Résultats sauvés dans: scraping_example_com_29-09-2025_14h30.json

👥 Exemples trouvés:
  1. John Doe - john.doe@example.com - 01 23 45 67 89
  2. Jane Smith - jane.smith@example.com - 06 78 90 12 34
  3. Bob Wilson - bob.wilson@example.com -

✅ Scraping terminé!
```

## 📊 Résultats

### Base de Données Supabase

Les données sont automatiquement sauvées dans votre table `personnes` avec :
- **nom** : Nom de famille
- **prenom** : Prénom
- **email** : Adresse email
- **telephone** : Numéro de téléphone formaté
- **poste** : Fonction/poste
- **source_url** : URL de la page source
- **confidence** : Score de confiance (0.0 à 1.0)
- **created_at** : Date de création automatique

### Fichier JSON Local

Un fichier JSON est également créé avec un nom logique :
```
scraping_[nom-du-site]_[date]_[heure].json
```

## ⚙️ Fonctionnalités

### 🔧 Installation Automatique
- Vérifie la version Python
- Installe automatiquement toutes les dépendances
- Configure spaCy pour l'extraction de noms

### 🕷️ Scraping Intelligent
- Crawling respectueux (pause de 1s entre pages)
- Extraction d'emails, téléphones et noms
- Évite les doublons automatiquement
- Reste sur le même domaine

### 💾 Sauvegarde Double
- **Supabase** : Base de données cloud
- **JSON local** : Fichier de sauvegarde

### 📱 Formats de Téléphone Supportés
- Français : `06 12 34 56 78`, `+33 6 12 34 56 78`
- Internationaux : `+1 234 567 8900`
- Détection contextuelle : `Tel: 01.23.45.67.89`

## 🛠️ Dépannage

### Problème : "Python 3.7+ requis"
```bash
# Vérifiez votre version
python --version
# ou
python3 --version
```

### Problème : "Échec installation dépendances"
```bash
# Installez pip manuellement
python -m ensurepip --upgrade
# ou
pip install --upgrade pip
```

### Problème : "Connexion Supabase échouée"
- Vérifiez votre URL (doit commencer par `https://`)
- Vérifiez votre clé (doit commencer par `eyJ`)
- Vérifiez votre connexion Internet

### Problème : "Table 'personnes' n'existe pas"
- Réexécutez le script `recreate_table.sql` dans Supabase
- Vérifiez dans Table Editor que la table existe

## 🔒 Sécurité

- ✅ **Respect des robots.txt** (pause entre requêtes)
- ✅ **User-Agent standard** (pas de bot détectable)
- ✅ **Pas de stockage de mots de passe**
- ✅ **Clés Supabase en lecture/écriture seulement**

## 📝 Support

En cas de problème :
1. Vérifiez que tous les fichiers sont présents
2. Vérifiez votre connexion Supabase dans le dashboard
3. Testez avec un site simple (votre propre site)

## 🚀 Conseils d'Utilisation

### Sites Recommandés
- Sites d'entreprises avec pages équipe
- Annuaires professionnels
- Sites institutionnels

### Sites à Éviter
- Sites avec captcha
- Sites nécessitant une connexion
- Sites avec beaucoup de JavaScript dynamique

---

**💡 Astuce** : Commencez toujours par tester sur 5-10 pages maximum pour vérifier que le site est compatible avant de lancer un scraping complet !