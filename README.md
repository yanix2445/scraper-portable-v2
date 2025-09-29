# 🕷️ Scraper Portable - Guide d'Installation et d'Utilisation

⚠️ **Important pour utilisateurs macOS** : Vous devez utiliser `source setup_venv.sh` avant de lancer le script sur macOS avec Python 3.13+ (Homebrew).

## 📦 Contenu du Package

- `portable_scraper.py` - Script principal auto-installable
- `recreate_table.sql` - Script de création de la base de données
- `.env.example` - Fichier de configuration exemple
- `setup_venv.sh` - Script d'installation d'environnement virtuel
- `README.md` - Ce guide d'installation

## 🚀 Installation Rapide

### 1. Prérequis

- **Python 3.7+** (vérifiez avec `python --version` ou `python3 --version`)
- **Connexion Internet** pour l'installation automatique des dépendances
- **Compte Supabase** (gratuit sur [supabase.com](https://supabase.com))

### 1.1. Configuration Automatique (.env)

Pour éviter de retaper vos informations à chaque fois :

```bash
# Copiez le fichier exemple
cp .env.example .env

# Éditez le fichier .env avec vos vraies valeurs
nano .env
```

**Le fichier .env.example contient déjà un exemple complet :**
```env
SUPABASE_URL=https://eeqxziwpykocnrbtmxiy.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DEFAULT_MAX_PAGES=50
DEFAULT_SAVE_DIR=.
# DEFAULT_URL=https://example.com
```

⚠️ **Important** : Remplacez les valeurs dans votre fichier `.env` par vos vraies informations Supabase.

### 1.2. Environnement Virtuel (REQUIS pour macOS)

⚠️ **Important pour macOS** : Si vous avez Python 3.13+ installé via Homebrew, l'environnement virtuel est **obligatoire** pour que le script fonctionne correctement.

```bash
# REQUIS sur macOS - Script automatique
source setup_venv.sh

# Puis lancez le script
python portable_scraper.py
```

**Alternative manuelle :**
```bash
python3 -m venv venv
source venv/bin/activate
python portable_scraper.py
```

💡 **Pourquoi ?** Python 3.13+ sur Homebrew utilise PEP 668 qui empêche l'installation de packages système. L'environnement virtuel contourne cette limitation.

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

💡 **Conseil** : Copiez ces valeurs directement dans votre fichier `.env` pour gagner du temps !

## 🎯 Utilisation

### Lancement du Script

**Sur macOS (obligatoire) :**
```bash
# 1. Activez l'environnement virtuel
source setup_venv.sh

# 2. Lancez le script
python portable_scraper.py
```

**Sur Linux/Windows :**
```bash
# Tentative directe (peut fonctionner)
python3 portable_scraper.py

# Si échec, utilisez un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
python portable_scraper.py
```

### Configuration Interactive

#### Avec fichier .env (Recommandé)

Si vous avez configuré un fichier `.env`, le script vous proposera :

1. **🔗 URL du site à scraper [URL par défaut si configurée]**
   ```
   🔗 URL du site à scraper [https://example.com]:
   Appuyez sur Entrée pour utiliser la valeur par défaut
   ```

2. **🗄️ Configuration Supabase (depuis .env)**
   ```
   🗄️ Configuration Supabase (depuis .env):
   URL: https://eeqxziwpykocnrbtmxiy.supabase.co
   Clé: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   Utiliser cette configuration ? [O/n]:
   ```

#### Sans fichier .env

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
   URL Supabase : https://eeqxziwpykocnrbtmxiy.supabase.co
   Clé Supabase : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
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
🗄️ Configuration Supabase (depuis .env):
URL: https://eeqxziwpykocnrbtmxiy.supabase.co
Clé: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Utiliser cette configuration ? [O/n]:
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
- **nom** : Nom complet de la personne (ex: "Marie Dupont", "Jean-Pierre Martin")
- **email** : Adresse email
- **telephone** : Numéro de téléphone formaté
- **poste** : Fonction/poste
- **source_url** : URL de la page source
- **confidence** : Score de confiance (0.0 à 1.0)
- **created_at** : Date de création automatique

### Fichier JSON Local

Les fichiers JSON sont organisés dans une structure de dossiers logique par date :

```
saves/
├── 2025/
│   ├── 09-Septembre/
│   │   ├── 29/
│   │   │   ├── 14h30_example_com_scraping.json
│   │   │   ├── 15h45_zyteck_fr_scraping.json
│   │   │   └── ...
│   │   └── 30/
│   │       └── ...
│   └── 10-Octobre/
│       └── ...
└── ...
```

**Format des fichiers** : `[heure]_[nom-du-site]_scraping.json`

Cette organisation permet de :
- ✅ Retrouver facilement les sauvegardes par date
- ✅ Éviter l'encombrement du répertoire principal
- ✅ Conserver un historique organisé chronologiquement

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

**Sur macOS :**
```bash
# Solution recommandée : utilisez l'environnement virtuel
source setup_venv.sh
python portable_scraper.py
```

**Sur autres systèmes :**
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