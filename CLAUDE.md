# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A portable, self-installing web scraper that extracts contact information (names, emails, phone numbers) from websites. Designed as a single-file Python script with automatic dependency management, it saves results to both Supabase database and local JSON files. The scraper uses intelligent NLP-based extraction with multilingual support (French/English).

## Essential Commands

### Running the Scraper

**macOS (REQUIRED due to Python 3.13+ PEP 668):**
```bash
source setup_venv.sh  # Activates venv automatically
python portable_scraper.py
```

**Linux/Windows:**
```bash
# Try direct execution first
python3 portable_scraper.py

# If fails, use venv
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
python portable_scraper.py
```

### Database Setup
```bash
# Execute in Supabase SQL Editor before first run
# Copy contents of recreate_table.sql
```

### Configuration
```bash
# Optional: Create .env file for default values
cp .env.example .env
# Edit .env with your Supabase credentials
```

## Architecture Overview

### Single-File Design Philosophy
The entire scraper is contained in `portable_scraper.py` (~1500 lines) with three main sections:
1. **Dependency Management** (lines 1-250): Self-installation logic
2. **Core Extraction Engine** (lines 250-1100): NLP and pattern-based extraction
3. **Scraping & Orchestration** (lines 1100-1500): URL crawling and coordination

### Key Architectural Decisions

**Intelligent Contact Extraction Pipeline:**
```
HTML Page → Profile Zones Detection → Element Extraction → Clustering → Validation → Person Objects
```

1. **Profile Zone Identification** (`identify_profile_zones`):
   - Searches for sections with classes like "team", "staff", "contact"
   - Validates zones contain both email AND (phone OR name context)
   - Fallback: analyzes entire page in chunks if no specific zones found

2. **Smart Clustering Strategy** (`cluster_by_proximity`):
   - **Case 1**: Single unique email in zone → groups ALL elements together (handles scattered info)
   - **Case 2**: Multiple emails → proximity-based clustering (handles team pages)
   - Adaptive thresholds: email+other=500 chars, name+phone=800 chars

3. **Name Selection Scoring** (`validate_and_score_profiles`):
   - Formula: `(distance/100) - (confidence * 10)`
   - Prioritizes high-confidence names even if slightly farther from email
   - Prevents extraction of section headings ("My Journey", "Our Team") as names

### Data Models

**PersonInfo** (dataclass):
- `nom`: Full name (e.g., "Marie Dupont", "Jean-Pierre Martin")
- `email`: Email address
- `telephone`: Formatted phone number
- `poste`: Job title/position
- `source_url`: Source page URL
- `confidence`: Score 0.0-1.0 based on extraction quality
- `created_at`: ISO timestamp

**ExtractedElement** (internal):
- `type`: "email" | "phone" | "name"
- `value`: Extracted text
- `position`: Character position in page text
- `html_position`: Position in HTML structure
- `context`: Surrounding text (±50 chars)
- `html_element`: Parent tag name
- `confidence`: Extraction reliability score

### Name Validation Logic

**Multilingual Avoid-Words Filter** (~200 terms):
- Form labels: "First Name", "Prénom", "Last Name", "Nom"
- Job titles: "Developer", "Développeur", "Engineer"
- Soft skills: "Team Player", "Collaborative", "Passionate"
- Tech terms: "React", "Python", "Docker"
- Portfolio sections: "My Journey", "My Projects", "Get Started"
- Cities: "Paris", "London", "New York"

**Name Pattern Matching**:
- Requires 2+ words (firstname + lastname) unless prefixed (M., Mme, Dr)
- Must match: `[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-z]+\s+[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-z]+`
- Rejects: starts with digit, contains special chars, >4 words, <3 chars

### Deduplication Strategy

**Global Deduplication** (`deduplicate_persons`):
- Groups profiles by email (case-insensitive)
- For duplicates, scores each profile:
  - Base: confidence value
  - +0.5: Valid name (length>3, contains space)
  - +0.2: Phone present
- Keeps highest-scoring profile per email
- Handles case: same person found on homepage + contact page

### Language Detection

**Supported Languages**: French (fr) + English (en)

Detection order:
1. HTML `lang` attribute (`<html lang="fr">` or `<html lang="en">`)
2. Meta tags (`<meta name="language" content="fr">`)
3. Content analysis: counts language indicators
   - French: "équipe", "à propos", "société", "téléphone"
   - English: "team", "about", "company", "phone"
   - Threshold: ≥2 indicators of either language

### Phone Number Handling

**Supported Formats**:
- French: `06 12 34 56 78`, `+33 6 12 34 56 78`, `01.23.45.67.89`
- International: `+1 234 567 8900`, `+44 20 1234 5678`
- Contextual: `Tel: 01 23 45 67 89`, `Phone: +33612345678`

**Normalization**:
- Converts to international format when possible
- French mobile: `06...` → `+33 6...`
- Formats with spaces: `+33 6 12 34 56 78`

### File Organization

**JSON Save Structure**:
```
saves/
└── 2025/
    └── 09-Septembre/
        └── 30/
            └── 14h30_example_com_scraping.json
```

Format: `[HHhMM]_[domain-slug]_scraping.json`

## Development Notes

### Testing Extraction on New Sites

When a site doesn't extract correctly, debug with:
```python
from portable_scraper import SimpleScraper
scraper = SimpleScraper("https://example.com", max_pages=1)
html = scraper.get_page_content("https://example.com")

# Check language detection
print(scraper.is_supported_language(html))

# Check profile zones
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
zones = scraper.extractor.identify_profile_zones(soup)
print(f"Found {len(zones)} profile zones")

# Check extracted elements
for zone in zones:
    elements = scraper.extractor.extract_elements_with_position(zone)
    emails = [e for e in elements if e.type == 'email']
    names = [e for e in elements if e.type == 'name']
    print(f"Emails: {len(emails)}, Names: {len(names)}")
```

### Adding New Avoid-Words

When false positives occur (e.g., "Creative Thinker" extracted as name):
1. Locate `is_likely_name()` method in `IntelligentPersonExtractor`
2. Add terms to appropriate category in `avoid_words` set
3. Test with: `extractor.is_likely_name("Creative Thinker")` → should return False

### Adjusting Clustering Behavior

If names/emails not grouping correctly:
- **Single person page**: Check `unique_emails` logic in `cluster_by_proximity` (line ~903)
- **Team page**: Adjust proximity thresholds in `get_proximity_threshold` (line ~938)
- **Debug positions**: Print `element.position` to see distance between email and name

### spaCy Model Management

The script auto-downloads models in this order:
1. Try `fr_core_news_sm` (French, 17MB)
2. Fallback to `en_core_web_sm` (English, 17MB)
3. Multiple installation methods attempted (system, --user, --break-system-packages)

If spaCy fails, extraction continues with regex-only (reduced name detection accuracy).

### macOS Python 3.13+ Compatibility

**PEP 668 Issue**: Homebrew Python 3.13+ prevents system-wide package installation.

**Solutions implemented**:
1. `setup_venv.sh`: Automated venv creation and activation
2. `install_package()`: Tries multiple pip flags (--break-system-packages, --user)
3. README instructions: Emphasize venv requirement for macOS users

### Respectful Crawling

- 1-second delay between pages (`time.sleep(1)`)
- User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
- Domain-restricted: only follows links on same domain
- Timeout: 10 seconds per page
- Language filtering: skips non-FR/EN pages early
