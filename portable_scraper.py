#!/usr/bin/env python3
"""
Scraper Portable - Version auto-installable
Fonctionne sur n'importe quelle machine avec Python 3.7+

Usage: python portable_scraper.py
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import json
import time
from datetime import datetime

# Version minime requise de Python
MIN_PYTHON = (3, 7)

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < MIN_PYTHON:
        print(f"❌ Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ requis. Version actuelle: {sys.version_info[0]}.{sys.version_info[1]}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info[0]}.{sys.version_info[1]} détecté")

def install_package(package):
    """Installe un package Python"""
    try:
        # Essayer d'abord installation normale
        subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        # Essayer avec --break-system-packages --user pour Python 3.13+ sur macOS/Homebrew
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package,
                                "--break-system-packages", "--user"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            # Essayer juste --user
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except subprocess.CalledProcessError:
                return False

def ensure_dependencies():
    """S'assure que toutes les dépendances sont installées"""
    print("🔧 Vérification des dépendances...")

    dependencies = {
        'requests': 'requests>=2.25.0',
        'beautifulsoup4': 'beautifulsoup4>=4.11.0',
        'lxml': 'lxml>=4.9.0',
        'supabase': 'supabase>=1.0.0',
        'spacy': 'spacy>=3.5.0',
        'python-dotenv': 'python-dotenv>=1.0.0'
    }

    missing = []

    for module, package in dependencies.items():
        try:
            if module == 'beautifulsoup4':
                import bs4
            elif module == 'python-dotenv':
                import dotenv
            else:
                __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {module} manquant")

    if missing:
        print(f"\n📦 Installation de {len(missing)} dépendances...")
        for package in missing:
            print(f"  Installant {package}...")
            if install_package(package):
                print(f"  ✅ {package} installé")
            else:
                print(f"  ❌ Échec installation {package}")
                return False

        # Après installation, forcer le rechargement des modules
        print("\n🔄 Vérification post-installation...")
        for module, package in dependencies.items():
            try:
                # Forcer le rechargement si le module était déjà importé
                if module in sys.modules:
                    del sys.modules[module]

                if module == 'beautifulsoup4':
                    import bs4
                elif module == 'python-dotenv':
                    import dotenv
                else:
                    __import__(module)
                print(f"  ✅ {module} vérifié")
            except ImportError:
                print(f"  ❌ {module} toujours manquant après installation")
                print(f"  ℹ️  Essayez d'activer un environnement virtuel ou utilisez 'python3 -m venv venv && source venv/bin/activate' avant de relancer")
                return False

    # Vérifier et installer spaCy model
    try:
        # Forcer le rechargement de spacy si déjà importé
        if 'spacy' in sys.modules:
            del sys.modules['spacy']
        import spacy
        try:
            nlp = spacy.load("fr_core_news_sm")
            print("  ✅ Modèle spaCy français")
        except OSError:
            try:
                nlp = spacy.load("en_core_web_sm")
                print("  ✅ Modèle spaCy anglais")
            except OSError:
                print("  📥 Installation modèle spaCy français...")
                # Essayer plusieurs méthodes d'installation pour spaCy
                success = False
                for args in [
                    [sys.executable, "-m", "spacy", "download", "fr_core_news_sm"],
                    [sys.executable, "-m", "pip", "install", "https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.7.0/fr_core_news_sm-3.7.0-py3-none-any.whl", "--break-system-packages", "--user"],
                    [sys.executable, "-m", "pip", "install", "https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.7.0/fr_core_news_sm-3.7.0-py3-none-any.whl", "--user"]
                ]:
                    if subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                        success = True
                        break

                if success:
                    print("  ✅ Modèle spaCy français installé")
                else:
                    print("  ⚠️  Échec modèle français, tentative anglais...")
                    success = False
                    for args in [
                        [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                        [sys.executable, "-m", "pip", "install", "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl", "--break-system-packages", "--user"],
                        [sys.executable, "-m", "pip", "install", "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl", "--user"]
                    ]:
                        if subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                            success = True
                            break

                    if success:
                        print("  ✅ Modèle spaCy anglais installé")
                    else:
                        print("  ❌ Impossible d'installer un modèle spaCy")
                        return False
    except ImportError:
        print("  ❌ spaCy non installé correctement")
        return False

    print("✅ Toutes les dépendances sont prêtes!")
    return True

# === CODE DU SCRAPER INTÉGRÉ ===

import re
import asyncio
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, urldefrag

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PersonInfo:
    """Structure pour les informations d'une personne"""
    nom: str = ""
    prenom: str = ""
    email: str = ""
    telephone: str = ""
    poste: str = ""
    source_url: str = ""
    confidence: float = 0.0
    created_at: str = ""

class SimpleSupabaseManager:
    """Gestionnaire Supabase simplifié"""

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client = None

    def connect(self):
        """Connexion à Supabase"""
        try:
            from supabase import create_client
            self.client = create_client(self.url, self.key)
            return True
        except Exception as e:
            logger.error(f"Connexion Supabase échouée: {e}")
            return False

    def save_person(self, person: PersonInfo) -> bool:
        """Sauvegarde une personne"""
        if not self.client:
            return False

        try:
            person.created_at = datetime.now().isoformat()
            data = asdict(person)

            # Insertion simple
            result = self.client.table('personnes').insert(data).execute()
            return True
        except Exception as e:
            logger.debug(f"Erreur sauvegarde: {e}")
            return False

class SimpleTextExtractor:
    """Extracteur de texte simplifié"""

    def __init__(self):
        self.setup_patterns()
        self.nlp = self.load_spacy()

    def setup_patterns(self):
        """Configure les patterns regex"""
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        )

        # Phone patterns améliorés
        self.phone_patterns = [
            re.compile(r'(?:\+33\s?|0)([1-9])(?:[\s.-]?\d{2}){4}'),
            re.compile(r'(?:\+33\s?|0)([1-9])\s?\d{8}'),
            re.compile(r'\+\d{1,3}[\s.-]?\d{6,14}'),
            re.compile(r'0\d(?:\s?\d{2}){4}'),
            re.compile(r'(?:tel|tél|phone|mobile)[\s:]+([+\d\s.-]{8,20})', re.I),
        ]

    def load_spacy(self):
        """Charge spaCy avec fallback"""
        try:
            import spacy
            for model in ["fr_core_news_sm", "en_core_web_sm"]:
                try:
                    return spacy.load(model)
                except OSError:
                    continue
            logger.warning("Aucun modèle spaCy trouvé, NER désactivé")
            return None
        except ImportError:
            logger.warning("spaCy non disponible, NER désactivé")
            return None

    def extract_emails(self, text: str) -> Set[str]:
        """Extrait les emails"""
        emails = set(self.email_pattern.findall(text))
        return {e for e in emails if not any(x in e.lower() for x in ['noreply', 'example'])}

    def extract_phones(self, text: str) -> Set[str]:
        """Extrait les téléphones"""
        phones = set()
        for pattern in self.phone_patterns:
            for match in pattern.finditer(text):
                phone = match.group().strip()
                normalized = self.normalize_phone(phone)
                if normalized:
                    phones.add(normalized)
        return phones

    def normalize_phone(self, phone: str) -> str:
        """Normalise un téléphone"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 8 or len(digits) > 15:
            return ""

        # Format français
        if digits.startswith('33') and len(digits) == 11:
            d = digits[2:]
            return f"+33 {d[0]} {d[1:3]} {d[3:5]} {d[5:7]} {d[7:9]}"
        elif digits.startswith('0') and len(digits) == 10:
            return f"{digits[0:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:10]}"

        return phone.strip()

    def extract_names(self, text: str) -> Set[str]:
        """Extrait les noms avec spaCy si disponible"""
        names = set()
        if self.nlp:
            try:
                doc = self.nlp(text[:10000])  # Limite pour performance
                for ent in doc.ents:
                    if ent.label_ in ("PER", "PERSON") and len(ent.text.strip()) > 2:
                        names.add(ent.text.strip())
            except Exception:
                pass
        return names

class SimpleScraper:
    """Scraper simplifié et portable"""

    def __init__(self, start_url: str, max_pages: int = 50):
        self.start_url = start_url
        self.max_pages = max_pages
        self.domain = urlparse(start_url).netloc
        self.visited = set()
        self.extractor = SimpleTextExtractor()
        self.results = []

    def is_valid_url(self, url: str) -> bool:
        """Vérifie si l'URL est valide pour ce scraping"""
        parsed = urlparse(url)
        return (parsed.netloc == self.domain and
                parsed.scheme in ('http', 'https') and
                not any(skip in url.lower() for skip in ['.pdf', '.jpg', '.png', '.gif']))

    def get_page_content(self, url: str) -> Optional[str]:
        """Récupère le contenu d'une page"""
        try:
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.debug(f"Erreur récupération {url}: {e}")
        return None

    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """Extrait les liens d'une page"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            links = set()

            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    full_url = urljoin(base_url, href)
                    full_url = full_url.split('#')[0]  # Retirer fragment
                    if self.is_valid_url(full_url):
                        links.add(full_url)

            return links
        except Exception:
            return set()

    def extract_persons_from_page(self, html: str, url: str) -> List[PersonInfo]:
        """Extrait les personnes d'une page"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(' ', strip=True)

            emails = self.extractor.extract_emails(text)
            phones = self.extractor.extract_phones(text)
            names = self.extractor.extract_names(text)

            persons = []

            # Créer une personne par email trouvé
            for email in emails:
                person = PersonInfo(email=email, source_url=url)

                # Essayer d'associer un nom
                if names:
                    name = list(names)[0]
                    parts = name.split()
                    if len(parts) >= 2:
                        person.prenom = ' '.join(parts[:-1])
                        person.nom = parts[-1]
                    else:
                        person.nom = name

                # Associer un téléphone
                if phones:
                    person.telephone = list(phones)[0]

                person.confidence = 0.7 if person.nom else 0.5
                persons.append(person)

            return persons

        except Exception as e:
            logger.debug(f"Erreur extraction {url}: {e}")
            return []

    def crawl(self) -> List[PersonInfo]:
        """Lance le crawling"""
        print(f"🕷️  Début du crawling de {self.start_url}")

        to_visit = [self.start_url]
        all_persons = []

        while to_visit and len(self.visited) < self.max_pages:
            url = to_visit.pop(0)

            if url in self.visited:
                continue

            self.visited.add(url)
            print(f"📄 Page {len(self.visited)}/{self.max_pages}: {url}")

            # Récupérer le contenu
            html = self.get_page_content(url)
            if not html:
                continue

            # Extraire les personnes
            persons = self.extract_persons_from_page(html, url)
            all_persons.extend(persons)

            if persons:
                print(f"   👥 {len(persons)} personne(s) trouvée(s)")

            # Découvrir de nouveaux liens
            if len(self.visited) < self.max_pages:
                links = self.extract_links(html, url)
                for link in links:
                    if link not in self.visited and link not in to_visit:
                        to_visit.append(link)

            # Pause respectueuse
            time.sleep(1)

        return all_persons

def load_env_config():
    """Charge la configuration depuis le fichier .env"""
    config = {}
    env_file = ".env"

    if os.path.exists(env_file):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)

            config['supabase_url'] = os.getenv('SUPABASE_URL', '').strip()
            config['supabase_key'] = os.getenv('SUPABASE_KEY', '').strip()
            config['default_max_pages'] = int(os.getenv('DEFAULT_MAX_PAGES', '50'))
            config['default_save_dir'] = os.getenv('DEFAULT_SAVE_DIR', '.').strip()
            config['default_url'] = os.getenv('DEFAULT_URL', '').strip()

            if config['supabase_url'] and config['supabase_key']:
                print("✅ Configuration .env trouvée et chargée")

        except Exception as e:
            print(f"⚠️  Erreur lecture .env: {e}")

    return config

def get_user_config():
    """Interface utilisateur pour la configuration"""
    print("🚀 Scraper Portable - Configuration")
    print("=" * 40)

    # Charger la config .env
    env_config = load_env_config()

    # URL avec valeur par défaut du .env
    default_url = env_config.get('default_url', '')
    if default_url:
        url_prompt = f"🔗 URL du site à scraper [{default_url}]: "
        url = input(url_prompt).strip()
        if not url:
            url = default_url
    else:
        url = input("🔗 URL du site à scraper: ").strip()

    if not url:
        print("❌ URL requise")
        sys.exit(1)

    # Paramètres avec valeur par défaut du .env
    default_max_pages = env_config.get('default_max_pages', 50)
    try:
        max_pages_input = input(f"📄 Nombre max de pages [{default_max_pages}]: ").strip()
        max_pages = int(max_pages_input) if max_pages_input else default_max_pages
    except ValueError:
        max_pages = default_max_pages

    # Configuration Supabase depuis .env ou saisie manuelle
    supabase_url = env_config.get('supabase_url', '')
    supabase_key = env_config.get('supabase_key', '')

    if supabase_url and supabase_key:
        print(f"\n🗄️  Configuration Supabase (depuis .env):")
        print(f"URL: {supabase_url}")
        print(f"Clé: {supabase_key[:20]}...")

        use_env = input("Utiliser cette configuration ? [O/n]: ").strip().lower()
        if use_env in ['', 'o', 'oui', 'y', 'yes']:
            pass  # Garder les valeurs du .env
        else:
            print("🗄️  Nouvelle configuration Supabase:")
            supabase_url = input("URL Supabase: ").strip()
            supabase_key = input("Clé Supabase: ").strip()
    else:
        print("\n🗄️  Configuration Supabase:")
        supabase_url = input("URL Supabase: ").strip()
        supabase_key = input("Clé Supabase: ").strip()

    # Choix du répertoire de sauvegarde avec valeur par défaut du .env
    default_save_dir = env_config.get('default_save_dir', '.')
    print("\n📁 Sauvegarde des résultats:")
    print("1) Répertoire courant (même dossier que le script)")
    print("2) Bureau")
    print("3) Téléchargements")
    print("4) Choisir un dossier personnalisé")

    choice = input("Votre choix [1]: ").strip() or "1"

    save_dir = default_save_dir if default_save_dir != '.' else "."

    if choice == "2":
        # Bureau
        if os.name == 'nt':  # Windows
            save_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        else:  # Mac/Linux
            save_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    elif choice == "3":
        # Téléchargements
        if os.name == 'nt':  # Windows
            save_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        else:  # Mac/Linux
            save_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    elif choice == "4":
        # Dossier personnalisé
        save_dir = input("Chemin du dossier: ").strip()
        if not save_dir:
            save_dir = "."

    # Vérifier que le dossier existe
    if not os.path.exists(save_dir):
        print(f"⚠️  Le dossier {save_dir} n'existe pas, utilisation du répertoire courant")
        save_dir = "."

    return {
        'url': url,
        'max_pages': max_pages,
        'supabase_url': supabase_url,
        'supabase_key': supabase_key,
        'save_dir': save_dir
    }

def main():
    """Fonction principale"""
    print("🚀 Scraper Portable Auto-Installable")
    print("=" * 40)

    # Vérifications système
    check_python_version()

    # Installation automatique des dépendances
    if not ensure_dependencies():
        print("❌ Impossible d'installer les dépendances")
        sys.exit(1)

    # Configuration utilisateur
    config = get_user_config()

    # Initialisation Supabase
    db = None
    if config['supabase_url'] and config['supabase_key']:
        db = SimpleSupabaseManager(config['supabase_url'], config['supabase_key'])
        if db.connect():
            print("✅ Connexion Supabase réussie")
        else:
            print("⚠️  Connexion Supabase échouée, sauvegarde locale uniquement")
            db = None

    # Lancement du scraping
    scraper = SimpleScraper(config['url'], config['max_pages'])
    persons = scraper.crawl()

    # Sauvegarde des résultats
    print(f"\n📊 Résultats: {len(persons)} personne(s) trouvée(s)")

    # Sauvegarde Supabase
    saved_to_db = 0
    if db:
        for person in persons:
            if db.save_person(person):
                saved_to_db += 1
        print(f"💾 {saved_to_db} personne(s) sauvegardée(s) en base")

    # Sauvegarde locale JSON avec structure organisée par date
    from urllib.parse import urlparse
    import re

    # Extraire le nom du site web
    domain = urlparse(config['url']).netloc
    site_name = domain.replace('www.', '').replace('.', '_')
    # Nettoyer le nom (caractères valides pour fichier)
    site_name = re.sub(r'[^\w\-_]', '_', site_name)

    # Date et heure formatées
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")  # 09
    month_name = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"][now.month]
    month_folder = f"{month}-{month_name}"  # 09-Septembre
    day = now.strftime("%d")
    time_str = now.strftime("%Hh%M")

    # Créer la structure de dossiers : saves/2025/09-Septembre/29/
    base_save_dir = os.path.join(config['save_dir'], "saves")
    date_dir = os.path.join(base_save_dir, year, month_folder, day)

    # Créer les dossiers s'ils n'existent pas
    os.makedirs(date_dir, exist_ok=True)

    # Nom de fichier avec horodatage
    filename = f"{time_str}_{site_name}_scraping.json"
    output_file = os.path.join(date_dir, filename)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(p) for p in persons], f, ensure_ascii=False, indent=2)

    print(f"📁 Résultats sauvés dans: {output_file}")

    # Affichage exemples
    print("\n👥 Exemples trouvés:")
    for i, person in enumerate(persons[:3]):
        print(f"  {i+1}. {person.prenom} {person.nom} - {person.email} - {person.telephone}")

    print("\n✅ Scraping terminé!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)