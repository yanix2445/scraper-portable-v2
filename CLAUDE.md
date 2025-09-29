# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a portable web scraper distribution package designed to extract contact information (names, emails, phone numbers) from websites and store results in Supabase database and local JSON files. The project consists of a single self-installing Python script that automatically manages dependencies.

## Repository Structure

- `portable_scraper.py` - Main self-installing scraper script with embedded dependencies management
- `recreate_table.sql` - PostgreSQL/Supabase table creation script for the `personnes` table
- `README.md` - Comprehensive French documentation and user guide

## Running the Scraper

### Basic Usage
```bash
python portable_scraper.py
```

The script is entirely interactive and will:
1. Check Python version (requires 3.7+)
2. Auto-install all required dependencies
3. Prompt for configuration (URL, page limits, Supabase credentials, save directory)
4. Execute the scraping process
5. Save results to both Supabase and local JSON file

### Dependencies Management
The script automatically handles all dependencies without requiring requirements.txt or manual pip installation:
- requests, beautifulsoup4, lxml (web scraping)
- supabase (database integration)
- spacy (natural language processing for name extraction)
- python-dotenv (environment handling)

### Database Setup
Before first run, execute `recreate_table.sql` in your Supabase SQL Editor to create the required `personnes` table with proper indexes and triggers.

## Code Architecture

### Core Components

**Dependency Management** (`check_python_version()`, `ensure_dependencies()`)
- Auto-installs missing packages
- Downloads spaCy language models (French/English fallback)
- Validates Python version compatibility

**Data Models** (`PersonInfo` dataclass)
- Structured representation of extracted contact information
- Fields: nom, prenom, email, telephone, poste, source_url, confidence, created_at

**Database Integration** (`SimpleSupabaseManager`)
- Simplified Supabase client wrapper
- Handles connection and person data insertion
- Graceful fallback if database unavailable

**Text Extraction** (`SimpleTextExtractor`)
- Regex-based email and phone number extraction
- spaCy-powered name entity recognition
- Phone number normalization for French formats

**Web Scraping** (`SimpleScraper`)
- Respectful crawling with 1-second delays
- Domain-restricted link following
- BeautifulSoup HTML parsing
- Duplicate prevention

### Key Features

- **Self-installing**: No manual dependency management required
- **Portable**: Single Python file with embedded functionality
- **Respectful crawling**: Implements delays and robots.txt compliance
- **Dual storage**: Supabase cloud database + local JSON backup
- **Multi-language support**: French/English spaCy models with fallback
- **Interactive configuration**: User-friendly prompts for all settings

## Development Notes

- The script is designed as a standalone executable for easy distribution
- All configuration is handled through interactive prompts (no config files)
- Error handling focuses on graceful degradation rather than hard failures
- Text extraction uses conservative patterns to minimize false positives
- Phone number handling specifically optimized for French formats but supports international numbers