# 🕷️ Scraper Portable - Ton Assistant d'Extraction de Contacts

> **En gros :** Un script Python qui visite des sites web et récupère automatiquement tous les emails, noms et numéros de téléphone. Zero config compliquée, il s'installe tout seul ! 🚀

---

## 🎯 C'est quoi exactement ?

Imagine : tu veux récupérer tous les contacts d'un site (équipe, direction, staff...). Au lieu de copier-coller pendant des heures comme un robot, tu lances ce petit script, tu lui files l'URL du site, et **boom** 💥 il te sort un joli fichier JSON avec tous les contacts bien organisés.

**Le meilleur dans tout ça ?** Pas besoin d'installer 50 trucs avant, le script gère tout automatiquement. Tu lances, ça roule !

---

## 📦 Ce qu'il y a dans le pack

```
📁 ton-dossier/
├── 🐍 portable_scraper.py      # Le boss (c'est lui qui fait tout ⭐)
├── 🗄️ recreate_table.sql       # Pour créer ta base de données
├── ⚙️ .env.example              # Config exemple (super pratique)
├── 🔧 setup_venv.sh            # Script magique pour Mac
└── 📖 README.md                 # Le guide que tu lis là 👋
```

---

## 🚀 Installation Ultra Rapide (5 min chrono)

### Étape 1️⃣ : Check si t'as Python

Ouvre ton terminal et tape :
```bash
python --version
# ou si ça marche pas :
python3 --version
```

Il te faut **Python 3.7 minimum**. Si c'est OK, passe direct à l'étape 2. Sinon, va sur [python.org](https://python.org) pour l'installer (c'est gratuit et rapide).

---

### Étape 2️⃣ : Prépare ton environnement

#### Sur macOS 🍎 (avec Homebrew)
```bash
# Un seul coup et c'est réglé !
source setup_venv.sh
```
> 💡 **Pourquoi ?** Depuis Python 3.13+, Apple a mis des restrictions. Cet environnement virtuel contourne ça proprement.

#### Sur Linux/Windows 🐧🪟
```bash
# Essaie direct d'abord
python3 portable_scraper.py

# Si ça bloque, crée un environnement virtuel
python3 -m venv venv
source venv/bin/activate      # Linux/Mac
# OU
venv\Scripts\activate         # Windows
```

> 💡 **C'est quoi un venv ?** C'est comme une bulle isolée pour tes scripts Python. Ça évite les conflits avec d'autres projets.

---

### Étape 3️⃣ : Configure Supabase (ta base de données gratuite)

#### 3.1 - Crée ton compte (2 min)

1. Va sur [supabase.com](https://supabase.com)
2. Clique **"Start your project"** (100% gratuit)
3. Connecte-toi avec GitHub ou email
4. Crée un nouveau projet :
   - **Nom** : `scraper-contacts` (ou ce que tu veux)
   - **Password** : choisis un mot de passe solide
   - **Région** : prends le plus proche géographiquement
5. Attends 30 sec que ça se crée ☕

#### 3.2 - Crée ta table (30 sec)

1. Dans ton projet Supabase → **"SQL Editor"** (menu gauche)
2. Ouvre le fichier `recreate_table.sql` sur ton PC
3. Copie tout le contenu (Ctrl+A, Ctrl+C)
4. Colle dans l'éditeur Supabase (Ctrl+V)
5. Clique **"RUN"** en bas à droite
6. Message de succès = GG ! ✅

#### 3.3 - Récupère tes clés (1 min)

1. Menu **Settings** → **API** (l'icône engrenage)
2. Note bien ces 2 trucs :
   - **URL** : ressemble à `https://xxxxx.supabase.co`
   - **anon public key** : un long texte qui commence par `eyJ...`

> 💡 **Astuce** : Garde ça dans un fichier texte, tu vas en avoir besoin juste après !

---

### Étape 4️⃣ : Config automatique (optionnel mais top)

Pour pas retaper tes infos à chaque fois :

```bash
# Copie le template
cp .env.example .env

# Édite avec ton éditeur préféré
nano .env
# ou code .env
# ou vim .env
```

Remplis comme ça :
```env
SUPABASE_URL=https://ton-projet.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUz...ta-grosse-clé-ici
DEFAULT_MAX_PAGES=50
```

Sauvegarde et c'est dans la poche ! Le script chargera tout automatiquement.

---

## 🎮 Mode d'emploi (super simple)

### Lancer le script

**Sur Mac** :
```bash
source setup_venv.sh          # Active l'environnement
python portable_scraper.py    # C'est parti !
```

**Sur Linux/Windows** :
```bash
python3 portable_scraper.py   # Go !
```

---

### Le script va te poser des questions

**1. URL du site ?**
```
🔗 URL du site à scraper: https://example.com
```
Entre l'URL du site que tu veux scraper.

**2. Combien de pages max ?**
```
📄 Nombre max de pages [50]:
```
Laisse vide pour 50 pages, ou tape un chiffre (ex: 10 pour tester).

**3. Config Supabase ?**
```
🗄️ Utiliser la config .env ? [O/n]:
```
Si t'as fait l'étape 4, tape juste "O" (ou Entrée). Sinon, entre tes clés manuellement.

**4. Où sauvegarder ?**
```
📁 Dossier de sauvegarde:
1) Ici (répertoire actuel)
2) Bureau
3) Téléchargements
4) Autre...
```
Choisis où tu veux le fichier JSON final.

---

### Exemple concret

```
🚀 Scraper Portable Auto-Installable
========================================
✅ Python 3.11 détecté
🔧 Vérification des dépendances...
  ✅ requests
  ✅ beautifulsoup4
  ✅ spacy
✅ Toutes les dépendances OK !

🕷️ Début du crawling de https://example.com
📄 Page 1/50: https://example.com
   👥 2 personne(s) trouvée(s)
      • Jean Dupont - jean.dupont@example.com - 06 12 34 56 78 (1.0)
      • Marie Martin - marie@example.com - 01 23 45 67 89 (0.9)

📄 Page 2/50: https://example.com/team
   👥 3 personne(s) trouvée(s)
   ...

✅ Crawling terminé - 15 profils trouvés
💾 15 personnes sauvegardées en base Supabase
📁 Fichier : saves/2025/09-Septembre/30/14h30_example_com_scraping.json

Enjoy! 🎉
```

---

## 📊 Où sont mes résultats ?

### Dans Supabase 🗄️

Va sur ton dashboard Supabase → **Table Editor** → table `personnes`

Tu verras tout bien rangé :
- **nom** : ex: "Jean Dupont", "Marie Martin"
- **email** : l'adresse email
- **telephone** : le tel formaté nickel (+33 6...)
- **poste** : le job si trouvé ("Directeur", "CEO"...)
- **source_url** : l'URL d'où ça vient
- **confidence** : score de fiabilité (0.0 = pas sûr, 1.0 = très sûr)
- **created_at** : timestamp automatique

### Dans un fichier JSON 📁

Structure hyper organisée par date :

```
saves/
└── 2025/
    └── 09-Septembre/
        └── 30/
            ├── 14h30_example_com_scraping.json
            ├── 15h45_autre_site_scraping.json
            └── ...
```

Le JSON ressemble à ça :
```json
[
  {
    "nom": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "telephone": "+33 6 12 34 56 78",
    "poste": "CEO",
    "source_url": "https://example.com/team",
    "confidence": 0.95,
    "created_at": "2025-09-30T14:30:00"
  }
]
```

---

## 🎨 Les trucs stylés du script

### 🧠 IA intégrée
- Utilise **spaCy** pour reconnaître les vrais noms
- Filtre les faux positifs ("Contact", "Team", "About Us"...)
- Score de confiance pour chaque extraction

### 🌍 Français + Anglais
- Détecte automatiquement la langue du site
- Gère les formats français ET anglais
- Téléphones français, US, UK, internationaux...

### 🎯 Extraction intelligente
- Trouve les zones "équipe", "team", "staff" automatiquement
- Regroupe les infos éparpillées (email en haut, nom en bas = OK !)
- Évite les doublons tout seul
- Priorise les noms proches des emails

### 📞 Tous les formats de tel
- France : `06 12 34 56 78`, `+33 6 12 34 56 78`, `01.23.45.67.89`
- USA : `+1 234 567 8900`
- UK : `+44 20 1234 5678`
- Contexte : `Tel: 01 23 45 67 89` → détecté !

### 🤝 Respectueux
- Pause de 1 sec entre chaque page (pas de spam)
- User-Agent standard (pas repéré comme bot)
- Reste sur le domaine demandé
- Timeout de 10 sec par page

---

## 🛠️ Problèmes courants

### "Python 3.7+ requis"
```bash
# Check ta version
python --version

# Trop vieux ? Installe une version récente sur python.org
```

### "Échec installation dépendances"
```bash
# Sur Mac
source setup_venv.sh
python portable_scraper.py

# Sur autres systèmes
python -m ensurepip --upgrade
pip install --upgrade pip
```

### "Connexion Supabase failed"
- ✅ URL commence par `https://` ?
- ✅ Clé commence par `eyJ` ?
- ✅ Internet fonctionne ?
- ✅ Projet Supabase créé ?

### "Table 'personnes' existe pas"
Refais l'étape 3.2 (copie le SQL dans Supabase)

### "Aucun contact trouvé"
- ✅ Le site a des contacts visibles (pas que des images) ?
- ✅ Langue française ou anglaise ?
- ✅ Pas de login requis ?
- ✅ Pas de Cloudflare/captcha ?

---

## 💡 Tips de pro

### Sites qui marchent bien 👍
- Pages "Notre équipe" / "Our team"
- Pages contact avec infos
- Annuaires pros
- Sites d'entreprise classiques
- Portfolios personnels

### Sites compliqués 👎
- Sites avec captcha (Cloudflare, reCAPTCHA)
- Sites avec login obligatoire
- Sites 100% JavaScript (React/Vue sans SSR)
- Réseaux sociaux (LinkedIn, Facebook...)

### Astuce 🎓
**Teste toujours avec 5-10 pages d'abord !**
```
📄 Nombre max de pages [50]: 5   # ← Tape 5 pour tester
```
Une fois que tu vois que ça marche, relance avec 50 ou plus.

---

## 🔐 Éthique & Légalité

### Ce que fait le script ✅
- Pause respectueuse entre pages
- User-Agent standard
- Reste sur le domaine
- Utilise que des clés publiques

### Tes responsabilités 🙏
- **Respecte la vie privée** : utilise les données éthiquement
- **Check le robots.txt** du site
- **Pas de spam** : 1 scraping suffit généralement
- **RGPD** : respecte les lois sur les données
- **Demande permission** si possible au proprio du site

> ⚠️ **Important** : Tu es responsable de comment tu utilises ce script. Utilise-le légalement et éthiquement !

---

## 🎉 C'est tout !

Si t'as suivi ce guide, t'as maintenant :
- ✅ Un scraper qui tourne
- ✅ Une base Supabase configurée
- ✅ Des contacts extraits proprement

### Besoin d'aide ?
1. Relis calmement ce README
2. Check les logs d'erreur
3. Google ton message d'erreur
4. Teste avec un site simple d'abord

---

**Fait avec ❤️ - Happy Scraping ! 🕷️**

*PS : Utilise ce pouvoir avec sagesse 😎*
