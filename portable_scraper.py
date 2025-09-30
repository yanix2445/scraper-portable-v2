#!/usr/bin/env python3
"""
Scraper Portable - Version auto-installable
Fonctionne sur n'importe quelle machine avec Python 3.7+

Usage: python portable_scraper.py
"""

from urllib.parse import urljoin, urlparse, urldefrag
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional, Tuple
import logging
import asyncio
import re
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
        print(
            f"❌ Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ requis. Version actuelle: {sys.version_info[0]}.{sys.version_info[1]}"
        )
        sys.exit(1)
    print(f"✅ Python {sys.version_info[0]}.{sys.version_info[1]} détecté")


def install_package(package):
    """Installe un package Python"""
    try:
        # Essayer d'abord installation normale
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        # Essayer avec --break-system-packages --user pour Python 3.13+ sur macOS/Homebrew
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    package,
                    "--break-system-packages",
                    "--user",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            # Essayer juste --user
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package, "--user"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except subprocess.CalledProcessError:
                return False


def ensure_dependencies():
    """S'assure que toutes les dépendances sont installées"""
    print("🔧 Vérification des dépendances...")

    dependencies = {
        "requests": "requests>=2.25.0",
        "beautifulsoup4": "beautifulsoup4>=4.11.0",
        "lxml": "lxml>=4.9.0",
        "supabase": "supabase>=1.0.0",
        "spacy": "spacy>=3.5.0",
        "python-dotenv": "python-dotenv>=1.0.0",
    }

    missing = []

    for module, package in dependencies.items():
        try:
            if module == "beautifulsoup4":
                import bs4
            elif module == "python-dotenv":
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

                if module == "beautifulsoup4":
                    import bs4
                elif module == "python-dotenv":
                    import dotenv
                else:
                    __import__(module)
                print(f"  ✅ {module} vérifié")
            except ImportError:
                print(f"  ❌ {module} toujours manquant après installation")
                print(
                    f"  ℹ️  Essayez d'activer un environnement virtuel ou utilisez 'python3 -m venv venv && source venv/bin/activate' avant de relancer"
                )
                return False

    # Vérifier et installer spaCy model
    try:
        # Forcer le rechargement de spacy si déjà importé
        if "spacy" in sys.modules:
            del sys.modules["spacy"]
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
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.7.0/fr_core_news_sm-3.7.0-py3-none-any.whl",
                        "--break-system-packages",
                        "--user",
                    ],
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.7.0/fr_core_news_sm-3.7.0-py3-none-any.whl",
                        "--user",
                    ],
                ]:
                    if (
                        subprocess.call(
                            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                        == 0
                    ):
                        success = True
                        break

                if success:
                    print("  ✅ Modèle spaCy français installé")
                else:
                    print("  ⚠️  Échec modèle français, tentative anglais...")
                    success = False
                    for args in [
                        [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl",
                            "--break-system-packages",
                            "--user",
                        ],
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl",
                            "--user",
                        ],
                    ]:
                        if (
                            subprocess.call(
                                args,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                            == 0
                        ):
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


# Configuration logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PersonInfo:
    """Structure pour les informations d'une personne"""

    nom: str = ""  # Nom complet (ex: "Marie Dupont" ou "Jean-Pierre Martin")
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
            result = self.client.table("personnes").insert(data).execute()
            return True
        except Exception as e:
            logger.debug(f"Erreur sauvegarde: {e}")
            return False


@dataclass
class ExtractedElement:
    """Élément extrait avec sa position et contexte"""

    type: str  # 'email', 'phone', 'name'
    value: str
    position: int  # Position dans le texte
    html_position: int  # Position dans le HTML
    context: str  # Contexte environnant
    html_element: str  # Tag HTML parent
    confidence: float = 0.0


class IntelligentPersonExtractor:
    """Extracteur intelligent qui analyse la proximité et le contexte"""

    def __init__(self):
        self.setup_patterns()
        self.nlp = self.load_spacy()

    def setup_patterns(self):
        """Configure les patterns regex améliorés"""
        # Email pattern amélioré
        self.email_pattern = re.compile(
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        )

        # Phone patterns français améliorés avec contexte
        self.phone_patterns = [
            re.compile(
                r"(?:tel|tél|phone|mobile|téléphone)[\s:]+([+\d\s.-]{8,20})", re.I
            ),
            re.compile(r"(?:\+33\s?|0)([1-9])(?:[\s.-]?\d{2}){4}"),
            re.compile(r"(?:\+33\s?|0)([1-9])\s?\d{8}"),
            re.compile(r"\+\d{1,3}[\s.-]?\d{6,14}"),
            re.compile(r"0[1-9](?:[\s.-]?\d{2}){4}"),
        ]

        # Patterns de contexte pour identifier les zones de profil
        self.profile_contexts = [
            re.compile(r"(?:équipe|team|staff|contact|about|à propos)", re.I),
            re.compile(r"(?:directeur|manager|responsable|chef|président)", re.I),
            re.compile(r"(?:email|e-mail|mail|contact|joindre)", re.I),
        ]

        # Patterns pour les noms français
        self.name_patterns = [
            re.compile(
                r"\b[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+(?:\s+[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+)+\b"
            ),
            re.compile(
                r"(?:M\.|Mme|Monsieur|Madame|Mr|Mrs)\s+([A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+(?:\s+[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+)*)",
                re.I,
            ),
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

    def extract_names_from_html_structure(self, zone):
        """Extrait les noms directement depuis la structure HTML - TRÈS PRÉCIS"""
        names = []

        # 1. Balises HTML qui contiennent souvent des noms
        name_selectors = [
            "h1, h2, h3, h4",  # Titres
            '[class*="name"]',
            '[id*="name"]',  # class="name", id="username"
            '[class*="team"]',
            '[class*="staff"]',  # class="team-member"
            '[class*="person"]',
            '[class*="member"]',  # class="person-name"
            '[class*="contact"]',
            '[class*="about"]',  # sections contact/about
            "figcaption",  # Légendes d'images
            # titles mais pas page-title
            '[class*="title"]:not([class*="page"])',
            "strong, b",  # Texte en gras (souvent des noms)
        ]

        for selector in name_selectors:
            elements = zone.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if text and self.is_likely_name(text):
                    # Score selon le type d'élément HTML
                    confidence = self.get_html_confidence(elem, selector)

                    names.append(
                        ExtractedElement(
                            type="name",
                            value=text,
                            position=0,  # Position sera calculée plus tard
                            html_position=0,
                            context=f"HTML:{elem.name} class:{elem.get('class', '')}",
                            html_element=elem.name,
                            confidence=confidence,
                        )
                    )

        return names

    def is_likely_name(self, text: str) -> bool:
        """Vérifie si un texte ressemble à un nom complet - SANS DICTIONNAIRE"""
        # Nettoyer le texte
        text = text.strip()

        # Trop court ou trop long
        if len(text) < 2 or len(text) > 50:
            return False

        # Contient des mots à éviter
        avoid_words = {
            "contact",
            "accueil",
            "société",
            "entreprise",
            "company",
            "home",
            "about",
            "services",
            "produits",
            "lorem",
            "ipsum",
            "exemple",
            "téléphone",
            "email",
            "adresse",
            "phone",
            "mail",
            "website",
            "mentions",
            "légales",
            "politique",
            "confidentialité",
            "portfolio",
            "prénom",
            "prenom",
            "nom",
            "name",
            "firstname",
            "lastname",
            "message",
            "subject",
            "objet",
        }

        if any(word in text.lower() for word in avoid_words):
            return False

        # Contient trop de mots (probablement pas un nom)
        words = text.split()
        if len(words) > 4:
            return False

        # Patterns qui NE ressemblent PAS à des noms
        bad_patterns = [
            r"^\d",  # Commence par un chiffre
            r"[^\w\s\-àâäéèêëïîôöùûüÿç\.]",  # Caractères bizarres
            r"^[a-z]",  # Commence par minuscule (sauf exceptions)
            r"\.com|\.fr|\.org",  # URLs
            r"@",  # Emails
            r"^\d{2}/\d{2}",  # Dates
        ]

        for pattern in bad_patterns:
            if re.search(pattern, text):
                return False

        # Patterns qui ressemblent à des noms (EXIGER prénom + nom)
        name_patterns = [
            # Marie Dupont (au moins 2 mots)
            r"^[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+\s+[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+",
            # Jean-Pierre Martin (avec tiret)
            r"^[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+\-[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+\s+[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]",
            # M. Dupont, Mme Martin
            r"^(?:M\.|Mme|Dr|Pr)\s+[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+",
        ]

        # Doit correspondre à un pattern ET avoir au moins 2 mots (sauf si préfixe M./Mme)
        has_valid_pattern = any(re.match(pattern, text) for pattern in name_patterns)
        has_two_words = len(words) >= 2 or any(text.startswith(prefix) for prefix in ["M.", "Mme", "Dr", "Pr"])

        return has_valid_pattern and has_two_words

    def get_html_confidence(self, elem, selector: str) -> float:
        """Score de confiance selon l'élément HTML"""
        base_confidence = 0.8

        # Bonus selon la balise
        if elem.name in ["h1", "h2", "h3"]:
            base_confidence += 0.1
        elif "name" in str(elem.get("class", "")):
            base_confidence += 0.15
        elif elem.name in ["strong", "b"]:
            base_confidence += 0.05

        # Malus si dans certains contextes
        parent_text = elem.parent.get_text() if elem.parent else ""
        if any(word in parent_text.lower() for word in ["copyright", "footer", "menu"]):
            base_confidence -= 0.2

        return min(0.95, max(0.5, base_confidence))

    def identify_profile_zones(self, soup):
        """Identifie les zones HTML qui peuvent contenir des profils"""
        profile_zones = []

        # Chercher des divs/sections avec des classes/ids suggestifs
        profile_selectors = [
            '[class*="team"]',
            '[class*="staff"]',
            '[class*="member"]',
            '[class*="contact"]',
            '[class*="about"]',
            '[class*="profile"]',
            '[class*="person"]',
            '[class*="employee"]',
            '[class*="card"]',
            '[id*="team"]',
            '[id*="staff"]',
            '[id*="contact"]',
        ]

        for selector in profile_selectors:
            elements = soup.select(selector)
            for element in elements:
                if self.contains_person_indicators(element):
                    profile_zones.append(element)

        # Si pas de zones spécifiques, analyser par sections
        if not profile_zones:
            for tag in ["div", "section", "article", "main"]:
                elements = soup.find_all(tag)
                for element in elements:
                    if self.contains_person_indicators(element):
                        profile_zones.append(element)

        # En dernier recours, utiliser le body entier par chunks
        if not profile_zones:
            profile_zones = [soup]

        return profile_zones

    def contains_person_indicators(self, element):
        """Vérifie si un élément contient des indicateurs de profil"""
        text = element.get_text().lower()

        # Vérifier présence d'email ET (nom OU téléphone)
        has_email = "@" in text
        has_phone = any(pattern.search(text) for pattern in self.phone_patterns)
        has_name_context = any(
            pattern.search(text) for pattern in self.profile_contexts
        )

        return has_email and (has_phone or has_name_context)

    def extract_elements_with_position(self, zone):
        """Extrait tous les éléments avec leur position dans la zone"""
        elements = []
        text = zone.get_text()

        # 1. PRIORITÉ - Extraire depuis les balises mailto: et tel:
        elements.extend(self.extract_from_mailto_tel_tags(zone))

        # 2. Extraire emails depuis le texte (fallback)
        for match in self.email_pattern.finditer(text):
            email = match.group()
            if not any(x in email.lower() for x in ["noreply", "example", "test"]):
                # Éviter les doublons avec les balises mailto:
                if not any(
                    elem.value == email for elem in elements if elem.type == "email"
                ):
                    context = self.get_context(text, match.start(), match.end())
                    elements.append(
                        ExtractedElement(
                            type="email",
                            value=email,
                            position=match.start(),
                            html_position=str(zone).find(email),
                            context=context,
                            html_element=self.get_parent_tag(zone, email),
                            confidence=0.7,  # Moins fiable que mailto:
                        )
                    )

        # 3. Extraire téléphones depuis le texte (fallback)
        for pattern in self.phone_patterns:
            for match in pattern.finditer(text):
                phone = self.normalize_phone(match.group())
                if phone and not any(
                    elem.value == phone for elem in elements if elem.type == "phone"
                ):
                    context = self.get_context(text, match.start(), match.end())
                    elements.append(
                        ExtractedElement(
                            type="phone",
                            value=phone,
                            position=match.start(),
                            html_position=str(zone).find(match.group()),
                            context=context,
                            html_element=self.get_parent_tag(zone, match.group()),
                            confidence=0.6,  # Moins fiable que tel:
                        )
                    )

        # 4. Extraire noms avec structure HTML (PRIORITÉ) + proximité
        html_names = self.extract_names_from_html_structure(zone)
        proximity_names = self.extract_names_with_proximity(zone, elements)

        # Fusionner en évitant les doublons
        all_names = html_names + proximity_names
        unique_names = []
        seen_names = set()

        for name in all_names:
            if name.value.lower() not in seen_names:
                seen_names.add(name.value.lower())
                unique_names.append(name)

        elements.extend(unique_names)

        return sorted(elements, key=lambda x: x.position)

    def extract_from_mailto_tel_tags(self, zone):
        """Extrait emails et téléphones depuis les balises mailto: et tel:"""
        elements = []

        # Chercher les liens mailto:
        for mailto_link in zone.find_all("a", href=re.compile(r"^mailto:", re.I)):
            email = mailto_link.get("href", "").replace("mailto:", "").strip()
            if email and "@" in email:
                # Nettoyer l'email (enlever paramètres ?subject=...)
                email = email.split("?")[0]

                # Trouver le nom associé dans le texte du lien ou à proximité
                link_text = mailto_link.get_text().strip()
                parent_text = (
                    mailto_link.parent.get_text() if mailto_link.parent else ""
                )

                # Position approximative dans le texte global
                full_text = zone.get_text()
                position = full_text.find(email) if email in full_text else 0

                elements.append(
                    ExtractedElement(
                        type="email",
                        value=email,
                        position=position,
                        html_position=0,
                        context=f"{link_text} | {parent_text}",
                        html_element=mailto_link.name,
                        # Très fiable car c'est une balise mailto:
                        confidence=0.95,
                    )
                )

        # Chercher les liens tel:
        for tel_link in zone.find_all("a", href=re.compile(r"^tel:", re.I)):
            tel = tel_link.get("href", "").replace("tel:", "").strip()
            if tel:
                normalized_tel = self.normalize_phone(tel)
                if normalized_tel:
                    link_text = tel_link.get_text().strip()
                    parent_text = tel_link.parent.get_text() if tel_link.parent else ""

                    full_text = zone.get_text()
                    position = full_text.find(tel) if tel in full_text else 0

                    elements.append(
                        ExtractedElement(
                            type="phone",
                            value=normalized_tel,
                            position=position,
                            html_position=0,
                            context=f"{link_text} | {parent_text}",
                            html_element=tel_link.name,
                            # Très fiable car c'est une balise tel:
                            confidence=0.95,
                        )
                    )

        return elements

    def get_context(self, text, start, end, window=50):
        """Récupère le contexte autour d'un élément"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()

    def get_parent_tag(self, zone, value):
        """Trouve le tag HTML parent d'un élément"""
        try:
            for elem in zone.find_all(text=re.compile(re.escape(value))):
                parent = elem.parent
                if parent:
                    return parent.name
        except:
            pass
        return "unknown"

    def extract_names_with_proximity(self, zone, existing_elements):
        """Extrait les noms en se basant sur la proximité avec emails/téléphones"""
        names = []
        text = zone.get_text()

        # D'abord chercher les noms dans les balises mailto: et tel: existantes
        for elem in existing_elements:
            if elem.type in ["email", "phone"] and elem.confidence >= 0.9:
                # Récupérer le contexte de la balise
                context_names = self.extract_names_from_context(elem.context)
                for name in context_names:
                    names.append(
                        ExtractedElement(
                            type="name",
                            value=name,
                            position=elem.position,  # Même position que l'email/tel
                            html_position=elem.html_position,
                            context=elem.context,
                            html_element=elem.html_element,
                            # Très fiable car associé à mailto:/tel:
                            confidence=0.9,
                        )
                    )

        # Ensuite, utiliser spaCy pour les noms généraux
        if self.nlp:
            try:
                doc = self.nlp(text[:5000])
                for ent in doc.ents:
                    if ent.label_ in ("PER", "PERSON") and len(ent.text.strip()) > 2:
                        name = ent.text.strip()
                        if self.is_likely_name(name) and not any(elem.value == name for elem in names):
                            # Calculer la proximité avec les emails/téléphones
                            proximity_bonus = self.calculate_proximity_to_contacts(
                                ent.start_char, existing_elements
                            )

                            context = self.get_context(
                                text, ent.start_char, ent.end_char
                            )
                            names.append(
                                ExtractedElement(
                                    type="name",
                                    value=name,
                                    position=ent.start_char,
                                    html_position=str(zone).find(name),
                                    context=context,
                                    html_element=self.get_parent_tag(zone, name),
                                    confidence=0.7 + proximity_bonus,
                                )
                            )
            except Exception as e:
                logger.debug(f"Erreur spaCy: {e}")

        # Patterns regex avec bonus de proximité
        for pattern in self.name_patterns:
            for match in pattern.finditer(text):
                name = match.group().strip()
                if (
                    len(name) > 3
                    and self.is_likely_name(name)  # Utiliser le filtre is_likely_name
                    and not any(
                        x.lower() in name.lower() for x in ["lorem", "ipsum", "example"]
                    )
                    and not any(elem.value == name for elem in names)
                ):

                    proximity_bonus = self.calculate_proximity_to_contacts(
                        match.start(), existing_elements
                    )

                    context = self.get_context(text, match.start(), match.end())
                    names.append(
                        ExtractedElement(
                            type="name",
                            value=name,
                            position=match.start(),
                            html_position=str(zone).find(name),
                            context=context,
                            html_element=self.get_parent_tag(zone, name),
                            confidence=0.6 + proximity_bonus,
                        )
                    )

        return names

    def extract_names_from_context(self, context: str) -> list:
        """Extrait les noms depuis le contexte d'une balise mailto:/tel:"""
        names = []

        # Chercher des patterns comme "Marie Dupont" dans le contexte
        for pattern in self.name_patterns:
            for match in pattern.finditer(context):
                name = match.group().strip()
                if len(name) > 3:
                    names.append(name)

        # Si pas de nom trouvé, essayer de nettoyer le texte du lien
        if not names:
            # Nettoyer le contexte (enlever "Email", "Téléphone", etc.)
            clean_context = re.sub(
                r"\b(email|mail|tel|téléphone|phone)\b", "", context, flags=re.I
            )
            clean_context = re.sub(r"[^\w\s\-àâäéèêëïîôöùûüÿç]", " ", clean_context)
            clean_context = " ".join(clean_context.split())

            if len(clean_context) > 3 and len(clean_context.split()) <= 4:
                names.append(clean_context)

        return names

    def calculate_proximity_to_contacts(
        self, name_position: int, contact_elements: list
    ) -> float:
        """Calcule un bonus de proximité entre un nom et les contacts"""
        if not contact_elements:
            return 0.0

        # Trouver la distance minimum avec un email ou téléphone
        min_distance = float("inf")
        for elem in contact_elements:
            if elem.type in ["email", "phone"]:
                distance = abs(name_position - elem.position)
                min_distance = min(min_distance, distance)

        # Bonus inversement proportionnel à la distance
        if min_distance <= 50:
            return 0.2  # Très proche
        elif min_distance <= 150:
            return 0.1  # Proche
        elif min_distance <= 300:
            return 0.05  # Moyennement proche
        else:
            return 0.0  # Pas de bonus

    def normalize_phone(self, phone: str) -> str:
        """Normalise un téléphone"""
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 8 or len(digits) > 15:
            return ""

        # Format français
        if digits.startswith("33") and len(digits) == 11:
            d = digits[2:]
            return f"+33 {d[0]} {d[1:3]} {d[3:5]} {d[5:7]} {d[7:9]}"
        elif digits.startswith("0") and len(digits) == 10:
            return f"{digits[0:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:10]}"

        return phone.strip()

    def cluster_by_proximity(self, elements):
        """Groupe les éléments par proximité"""
        if not elements:
            return []

        clusters = []
        current_cluster = [elements[0]]

        for i in range(1, len(elements)):
            current_elem = elements[i]
            last_elem = current_cluster[-1]

            # Calculer la distance de proximité
            position_distance = abs(current_elem.position - last_elem.position)

            # Seuil de proximité adaptatif selon le type
            max_distance = self.get_proximity_threshold(last_elem, current_elem)

            if position_distance <= max_distance:
                current_cluster.append(current_elem)
            else:
                if len(current_cluster) > 0:
                    clusters.append(current_cluster)
                current_cluster = [current_elem]

        if current_cluster:
            clusters.append(current_cluster)

        return clusters

    def get_proximity_threshold(self, elem1, elem2):
        """Calcule le seuil de proximité entre deux éléments"""
        # Plus strict pour email-nom, plus souple pour nom-téléphone
        if (elem1.type == "email" and elem2.type == "name") or (
            elem1.type == "name" and elem2.type == "email"
        ):
            return 200  # Caractères
        elif (elem1.type == "name" and elem2.type == "phone") or (
            elem1.type == "phone" and elem2.type == "name"
        ):
            return 300
        else:
            return 150

    def validate_and_score_profiles(self, clusters, url):
        """Valide et score chaque profil potentiel"""
        persons = []

        for cluster in clusters:
            person = PersonInfo(source_url=url)
            cluster_score = 0

            emails = [e for e in cluster if e.type == "email"]
            phones = [e for e in cluster if e.type == "phone"]
            names = [e for e in cluster if e.type == "name"]

            # Une personne doit avoir AU MOINS un email
            if not emails:
                continue

            # Prendre le meilleur email (celui avec le meilleur contexte)
            best_email = max(emails, key=lambda x: x.confidence)
            person.email = best_email.value
            cluster_score += 0.4

            # Associer le nom complet le plus proche de l'email
            if names:
                closest_name = min(
                    names, key=lambda x: abs(x.position - best_email.position)
                )
                person.nom = closest_name.value.strip()
                cluster_score += 0.4

            # Associer le téléphone le plus proche
            if phones:
                closest_phone = min(
                    phones, key=lambda x: abs(x.position - best_email.position)
                )
                person.telephone = closest_phone.value
                cluster_score += 0.2

            # Bonus pour contexte professionnel
            if any(
                "contact" in e.context.lower() or "équipe" in e.context.lower()
                for e in cluster
            ):
                cluster_score += 0.1

            person.confidence = min(1.0, cluster_score)

            # Ne garder que les profils avec un score minimum
            if person.confidence >= 0.4:
                persons.append(person)

        return persons


class SmartURLPrioritizer:
    """Système intelligent de priorisation des URLs"""

    def __init__(self):
        # URLs TRÈS PROMETTEUSES (Score: 10)
        self.high_priority_patterns = [
            r"/(?:equipe|team|staff|personnel)(?:/|$)",
            r"/(?:about-us|a-propos|qui-sommes-nous)(?:/|$)",
            r"/(?:contact|contacts|nous-contacter)(?:/|$)",
            r"/(?:management|direction|dirigeants)(?:/|$)",
            r"/(?:leadership|executives|board)(?:/|$)",
        ]

        # URLs PROMETTEUSES (Score: 8)
        self.medium_priority_patterns = [
            r"/(?:about|apropos)(?:/|$)",
            r"/(?:people|membres|member)(?:/|$)",
            r"/(?:our-team|notre-equipe)(?:/|$)",
            r"/(?:organization|organisation)(?:/|$)",
            r"/(?:advisors|conseillers|founders|fondateurs)(?:/|$)",
        ]

        # URLs MOYENNEMENT PROMETTEUSES (Score: 6)
        self.low_priority_patterns = [
            r"/(?:company|entreprise|societe)(?:/|$)",
            r"/(?:history|histoire)(?:/|$)",
            r"/(?:office|bureau|offices)(?:/|$)",
            r"/(?:locations|implantations)(?:/|$)",
            r"/services(?:/|$)",
        ]

        # URLs SPÉCIALISÉES - profils individuels (Score: 9)
        self.individual_patterns = [
            r"/(?:team|equipe|staff|personnel)/[^/]+(?:/|$)",
            r"/(?:contact|bureau)/[^/]+(?:/|$)",
            r"/(?:member|membre)/[^/]+(?:/|$)",
        ]

        # URLs À ÉVITER (Score: 1)
        self.avoid_patterns = [
            r"/(?:blog|news|actualites|presse)(?:/|$)",
            r"/(?:products|produits|catalogue)(?:/|$)",
            r"/(?:legal|mentions-legales|cgv)(?:/|$)",
            r"/(?:faq|aide|support)(?:/|$)",
            r"/(?:media|gallery|galerie)(?:/|$)",
            r"/(?:login|register|cart|panier)(?:/|$)",
        ]

        # Compiler les patterns pour la performance
        self.compiled_patterns = {
            "high": [re.compile(p, re.I) for p in self.high_priority_patterns],
            "medium": [re.compile(p, re.I) for p in self.medium_priority_patterns],
            "low": [re.compile(p, re.I) for p in self.low_priority_patterns],
            "individual": [re.compile(p, re.I) for p in self.individual_patterns],
            "avoid": [re.compile(p, re.I) for p in self.avoid_patterns],
        }

    def score_url(self, url: str) -> int:
        """Score une URL selon sa probabilité de contenir des profils"""
        path = urlparse(url).path.lower()

        # Vérifier les patterns à éviter d'abord
        for pattern in self.compiled_patterns["avoid"]:
            if pattern.search(path):
                return 1

        # Profils individuels = priorité maximale
        for pattern in self.compiled_patterns["individual"]:
            if pattern.search(path):
                return 9

        # Haute priorité
        for pattern in self.compiled_patterns["high"]:
            if pattern.search(path):
                return 10

        # Moyenne priorité
        for pattern in self.compiled_patterns["medium"]:
            if pattern.search(path):
                return 8

        # Basse priorité
        for pattern in self.compiled_patterns["low"]:
            if pattern.search(path):
                return 6

        # URL inconnue = score neutre
        return 5

    def prioritize_urls(self, urls: list) -> list:
        """Trie les URLs par ordre de priorité décroissante"""
        url_scores = [(url, self.score_url(url)) for url in urls]
        # Trier par score décroissant, puis alphabétiquement pour la cohérence
        return [url for url, score in sorted(url_scores, key=lambda x: (-x[1], x[0]))]


class SimpleScraper:
    """Scraper simplifié et portable avec ciblage intelligent"""

    def __init__(self, start_url: str, max_pages: int = 50):
        self.start_url = start_url
        self.max_pages = max_pages
        self.domain = urlparse(start_url).netloc
        self.visited: set[str] = set()
        self.extractor = IntelligentPersonExtractor()
        self.prioritizer = SmartURLPrioritizer()
        self.results: list[PersonInfo] = []
        self.successful_patterns: set[str] = (
            set()
        )  # Patterns qui ont donné des résultats

    def is_valid_url(self, url: str) -> bool:
        """Vérifie si l'URL est valide pour ce scraping"""
        parsed = urlparse(url)
        return (
            parsed.netloc == self.domain
            and parsed.scheme in ("http", "https")
            and not any(
                skip in url.lower() for skip in [".pdf", ".jpg", ".png", ".gif"]
            )
        )

    def is_french_page(self, html: str) -> bool:
        """Vérifie si une page est en français"""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Vérifier l'attribut lang de la page
            html_tag = soup.find("html")
            if html_tag:
                lang_attr = html_tag.get("lang")
                if isinstance(lang_attr, str) and lang_attr.lower().startswith("fr"):
                    return True

            # Vérifier les meta tags de langue
            meta_lang = soup.find("meta", attrs={"name": "language"})
            if meta_lang:
                content_attr = meta_lang.get("content", "")
                if isinstance(content_attr, str) and content_attr.lower().startswith(
                    "fr"
                ):
                    return True

            # Vérifier les indicateurs français dans le contenu
            text = soup.get_text().lower()
            french_indicators = [
                "équipe",
                "à propos",
                "société",
                "entreprise",
                "contact",
                "téléphone",
                "adresse",
                "france",
                "français",
                "nos services",
                "notre équipe",
                "qui sommes-nous",
            ]

            french_count = sum(
                1 for indicator in french_indicators if indicator in text
            )

            # Si au moins 2 indicateurs français trouvés
            return french_count >= 2

        except Exception as e:
            logger.debug(f"Erreur détection langue: {e}")
            return True  # Par défaut, on considère comme français

    def get_page_content(self, url: str) -> Optional[str]:
        """Récupère le contenu d'une page"""
        try:
            import requests

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.debug(f"Erreur récupération {url}: {e}")
        return None

    def extract_links(self, html: str, base_url: str) -> list:
        """Extrait et priorise les liens d'une page"""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            links = set()

            for a in soup.find_all("a", href=True):
                href_attr = a["href"]
                if isinstance(href_attr, str):
                    href = href_attr.strip()
                    if href and not href.startswith(
                        ("#", "javascript:", "mailto:", "tel:")
                    ):
                        full_url = urljoin(base_url, href)
                        full_url = full_url.split("#")[0]  # Retirer fragment
                        if self.is_valid_url(full_url):
                            links.add(full_url)

            # Prioriser les liens trouvés
            prioritized_links = self.prioritizer.prioritize_urls(list(links))

            # Afficher les liens prioritaires pour debug
            if prioritized_links:
                high_priority = [
                    url
                    for url in prioritized_links
                    if self.prioritizer.score_url(url) >= 8
                ]
                if high_priority:
                    print(
                        f"   🎯 {len(high_priority)} lien(s) prioritaire(s) trouvé(s)"
                    )

            return prioritized_links
        except Exception:
            return []

    def extract_persons_from_page(self, html: str, url: str) -> List[PersonInfo]:
        """Extrait les personnes d'une page avec analyse intelligente"""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # 1. Identifier les zones de profils potentielles
            profile_zones = self.extractor.identify_profile_zones(soup)
            all_persons = []

            # 2. Traiter chaque zone séparément
            for zone in profile_zones:
                # Extraire les éléments avec leur position
                elements = self.extractor.extract_elements_with_position(zone)

                if not elements:
                    continue

                # Regrouper par proximité
                clusters = self.extractor.cluster_by_proximity(elements)

                # Valider et créer les profils
                persons = self.extractor.validate_and_score_profiles(clusters, url)
                all_persons.extend(persons)

            # 3. Déduplication des personnes similaires
            unique_persons = self.deduplicate_persons(all_persons)

            logger.debug(
                f"Extraction {url}: {len(unique_persons)} personne(s) trouvée(s)"
            )
            return unique_persons

        except Exception as e:
            logger.debug(f"Erreur extraction {url}: {e}")
            return []

    def deduplicate_persons(self, persons):
        """Supprime les doublons de personnes"""
        if not persons:
            return []

        unique_persons = []
        seen_emails = set()

        for person in sorted(persons, key=lambda p: p.confidence, reverse=True):
            if person.email and person.email.lower() not in seen_emails:
                seen_emails.add(person.email.lower())
                unique_persons.append(person)

        return unique_persons

    def crawl(self) -> List[PersonInfo]:
        """Lance le crawling avec priorisation intelligente"""
        print(f"🕷️  Début du crawling intelligent de {self.start_url}")

        # Utiliser une liste prioritaire au lieu d'une FIFO simple
        to_visit = []
        all_persons = []

        # Ajouter l'URL de départ avec sa priorité
        initial_score = self.prioritizer.score_url(self.start_url)
        to_visit.append((self.start_url, initial_score))
        print(f"🎯 URL de départ (score: {initial_score}): {self.start_url}")

        while to_visit and len(self.visited) < self.max_pages:
            # Trier par priorité décroissante et prendre la meilleure
            to_visit.sort(key=lambda x: x[1], reverse=True)
            url, score = to_visit.pop(0)

            if url in self.visited:
                continue

            self.visited.add(url)
            score_emoji = "🔥" if score >= 9 else "⭐" if score >= 8 else "📄"
            print(
                f"{score_emoji} Page {len(self.visited)}/{self.max_pages} (score:{score}): {url}"
            )

            # Récupérer le contenu
            html = self.get_page_content(url)
            if not html:
                continue

            # Vérifier si la page est en français
            if not self.is_french_page(html):
                print(f"   🚫 Page non-française, ignorée")
                continue

            # Extraire les personnes
            persons = self.extract_persons_from_page(html, url)
            all_persons.extend(persons)

            if persons:
                print(f"   👥 {len(persons)} personne(s) trouvée(s)")
                # Enregistrer le pattern comme réussi
                self.track_successful_pattern(url)

                for person in persons:
                    confidence_str = f"({person.confidence:.1f})"
                    name_str = person.nom or "❓"
                    phone_str = person.telephone or "❓"
                    print(
                        f"      • {name_str} - {person.email} - {phone_str} {confidence_str}"
                    )

            # Découvrir de nouveaux liens avec priorisation
            if len(self.visited) < self.max_pages:
                links = self.extract_links(html, url)
                for link in links:
                    if link not in self.visited and not any(
                        l[0] == link for l in to_visit
                    ):
                        link_score = self.prioritizer.score_url(link)
                        # Bonus si c'est un pattern qui a déjà donné des résultats
                        if self.matches_successful_pattern(link):
                            link_score += 2
                        to_visit.append((link, link_score))

            # Pause respectueuse
            time.sleep(1)

        print(f"\n✅ Crawling terminé - {len(all_persons)} profils uniques trouvés")
        return all_persons

    def track_successful_pattern(self, url: str):
        """Enregistre les patterns d'URLs qui ont donné des résultats"""
        path = urlparse(url).path.lower()

        # Identifier le pattern principal
        if "/team" in path or "/equipe" in path:
            self.successful_patterns.add("team")
        elif "/contact" in path:
            self.successful_patterns.add("contact")
        elif "/about" in path or "/apropos" in path:
            self.successful_patterns.add("about")
        elif "/staff" in path or "/personnel" in path:
            self.successful_patterns.add("staff")

    def matches_successful_pattern(self, url: str) -> bool:
        """Vérifie si une URL correspond à un pattern qui a déjà donné des résultats"""
        path = urlparse(url).path.lower()

        for pattern in self.successful_patterns:
            if pattern in path:
                return True
        return False


def load_env_config():
    """Charge la configuration depuis le fichier .env"""
    config = {}
    env_file = ".env"

    if os.path.exists(env_file):
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)

            config["supabase_url"] = os.getenv("SUPABASE_URL", "").strip()
            config["supabase_key"] = os.getenv("SUPABASE_KEY", "").strip()
            config["default_max_pages"] = int(os.getenv("DEFAULT_MAX_PAGES", "50"))
            config["default_save_dir"] = os.getenv("DEFAULT_SAVE_DIR", ".").strip()
            config["default_url"] = os.getenv("DEFAULT_URL", "").strip()

            if config["supabase_url"] and config["supabase_key"]:
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
    default_url = env_config.get("default_url", "")
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
    default_max_pages = env_config.get("default_max_pages", 50)
    try:
        max_pages_input = input(
            f"📄 Nombre max de pages [{default_max_pages}]: "
        ).strip()
        max_pages = int(max_pages_input) if max_pages_input else default_max_pages
    except ValueError:
        max_pages = default_max_pages

    # Configuration Supabase depuis .env ou saisie manuelle
    supabase_url = env_config.get("supabase_url", "")
    supabase_key = env_config.get("supabase_key", "")

    if supabase_url and supabase_key:
        print(f"\n🗄️  Configuration Supabase (depuis .env):")
        print(f"URL: {supabase_url}")
        print(f"Clé: {supabase_key[:20]}...")

        use_env = input("Utiliser cette configuration ? [O/n]: ").strip().lower()
        if use_env in ["", "o", "oui", "y", "yes"]:
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
    default_save_dir = env_config.get("default_save_dir", ".")
    print("\n📁 Sauvegarde des résultats:")
    print("1) Répertoire courant (même dossier que le script)")
    print("2) Bureau")
    print("3) Téléchargements")
    print("4) Choisir un dossier personnalisé")

    choice = input("Votre choix [1]: ").strip() or "1"

    save_dir = default_save_dir if default_save_dir != "." else "."

    if choice == "2":
        # Bureau
        if os.name == "nt":  # Windows
            save_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        else:  # Mac/Linux
            save_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    elif choice == "3":
        # Téléchargements
        if os.name == "nt":  # Windows
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
        print(
            f"⚠️  Le dossier {save_dir} n'existe pas, utilisation du répertoire courant"
        )
        save_dir = "."

    return {
        "url": url,
        "max_pages": max_pages,
        "supabase_url": supabase_url,
        "supabase_key": supabase_key,
        "save_dir": save_dir,
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
    if config["supabase_url"] and config["supabase_key"]:
        db = SimpleSupabaseManager(config["supabase_url"], config["supabase_key"])
        if db.connect():
            print("✅ Connexion Supabase réussie")
        else:
            print("⚠️  Connexion Supabase échouée, sauvegarde locale uniquement")
            db = None

    # Lancement du scraping
    scraper = SimpleScraper(config["url"], config["max_pages"])
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
    domain = urlparse(config["url"]).netloc
    site_name = domain.replace("www.", "").replace(".", "_")
    # Nettoyer le nom (caractères valides pour fichier)
    site_name = re.sub(r"[^\w\-_]", "_", site_name)

    # Date et heure formatées
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")  # 09
    month_name = [
        "",
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ][now.month]
    month_folder = f"{month}-{month_name}"  # 09-Septembre
    day = now.strftime("%d")
    time_str = now.strftime("%Hh%M")

    # Créer la structure de dossiers : saves/2025/09-Septembre/29/
    base_save_dir = os.path.join(config["save_dir"], "saves")
    date_dir = os.path.join(base_save_dir, year, month_folder, day)

    # Créer les dossiers s'ils n'existent pas
    os.makedirs(date_dir, exist_ok=True)

    # Nom de fichier avec horodatage
    filename = f"{time_str}_{site_name}_scraping.json"
    output_file = os.path.join(date_dir, filename)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in persons], f, ensure_ascii=False, indent=2)

    print(f"📁 Résultats sauvés dans: {output_file}")

    # Affichage exemples
    print("\n👥 Exemples trouvés:")
    for i, person in enumerate(persons[:3]):
        print(f"  {i+1}. {person.nom} - {person.email} - {person.telephone}")

    print("\n✅ Scraping terminé!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
