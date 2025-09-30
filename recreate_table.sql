-- ========================================
-- 🚀 TABLE OPTIMISÉE POUR SCRAPER PORTABLE
-- ========================================
-- Version ultra optimisée avec contraintes, validation et performance
-- Compatible Supabase/PostgreSQL 12+

-- Supprimer l'ancienne table si elle existe
DROP TABLE IF EXISTS personnes CASCADE;

-- Créer la table avec colonnes essentielles uniquement
CREATE TABLE personnes (
    -- Clé primaire auto-incrémentée
    id BIGSERIAL PRIMARY KEY,

    -- Données extraites (nom, email, téléphone)
    nom TEXT,
    email TEXT NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    telephone TEXT CHECK (telephone IS NULL OR telephone ~* '^\+?[0-9\s\.\-\(\)]{8,20}$'),

    -- Métadonnées essentielles
    source_url TEXT NOT NULL,
    confidence NUMERIC(3,2) DEFAULT 0.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Contrainte unique sur email (évite les doublons)
    CONSTRAINT unique_email UNIQUE(email)
);

-- ========================================
-- 📊 INDEX STRATÉGIQUES (pour tes 2 besoins)
-- ========================================

-- 1. BESOIN: Trier par fiabilité (du plus fiable au moins fiable)
CREATE INDEX idx_personnes_confidence ON personnes(confidence DESC);

-- 2. BESOIN: Filtrer par URL scrapée
CREATE INDEX idx_personnes_source_url ON personnes(source_url);

-- Bonus: Index composite pour "contacts d'un site triés par fiabilité"
CREATE INDEX idx_personnes_url_confidence ON personnes(source_url, confidence DESC);


-- ========================================
-- 🔐 ROW LEVEL SECURITY (SUPABASE)
-- ========================================

-- Activer RLS (sécurité par ligne)
ALTER TABLE personnes ENABLE ROW LEVEL SECURITY;

-- Politique 1: Lecture publique (tout le monde peut consulter les contacts)
CREATE POLICY "Lecture publique des contacts"
    ON personnes FOR SELECT
    USING (true);

-- Politique 2: Insertion authentifiée uniquement (seul ton scraper peut ajouter)
CREATE POLICY "Insertion authentifiée uniquement"
    ON personnes FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Politique 3: Mise à jour authentifiée uniquement
CREATE POLICY "Mise à jour authentifiée uniquement"
    ON personnes FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Politique 4: Suppression authentifiée uniquement
CREATE POLICY "Suppression authentifiée uniquement"
    ON personnes FOR DELETE
    USING (auth.role() = 'authenticated');

-- ========================================
-- 📈 VUES UTILES (OPTIONNEL)
-- ========================================

-- Vue : personnes les plus fiables (BESOIN: trier par fiabilité)
CREATE OR REPLACE VIEW personnes_fiables AS
SELECT *
FROM personnes
WHERE confidence >= 0.8
ORDER BY confidence DESC;

-- Vue : statistiques par site scrapé (BESOIN: filtrer par URL)
CREATE OR REPLACE VIEW stats_par_source AS
SELECT
    source_url,
    COUNT(*) as nombre_contacts,
    AVG(confidence) as confiance_moyenne,
    COUNT(*) FILTER (WHERE nom IS NOT NULL AND nom != '') as avec_nom,
    COUNT(*) FILTER (WHERE telephone IS NOT NULL AND telephone != '') as avec_telephone,
    MAX(created_at) as dernier_scraping
FROM personnes
GROUP BY source_url
ORDER BY confiance_moyenne DESC;

-- ========================================
-- 🎯 COMMENTAIRES (DOCUMENTATION)
-- ========================================

COMMENT ON TABLE personnes IS 'Contacts extraits par le scraper (nom, email, téléphone) avec fiabilité et source';
COMMENT ON COLUMN personnes.nom IS 'Nom complet (ex: "Marie Dupont", "Jean-Pierre Martin")';
COMMENT ON COLUMN personnes.email IS 'Adresse email (obligatoire, unique, validé par regex)';
COMMENT ON COLUMN personnes.telephone IS 'Numéro de téléphone formaté (+33 6...), validé par regex';
COMMENT ON COLUMN personnes.source_url IS 'URL de la page scrapée (pour filtrer par site)';
COMMENT ON COLUMN personnes.confidence IS 'Score de fiabilité (0.0 à 1.0) pour trier les meilleurs contacts';
COMMENT ON COLUMN personnes.created_at IS 'Date du scraping (automatique)';

-- ========================================
-- ✅ VÉRIFICATION
-- ========================================

-- Test : vérifier que tout est créé
DO $$
DECLARE
    index_count INT;
BEGIN
    SELECT COUNT(*) INTO index_count FROM pg_indexes WHERE tablename = 'personnes';

    RAISE NOTICE '✅ Table "personnes" créée (7 colonnes essentielles)';
    RAISE NOTICE '✅ Colonnes: id, nom, email, telephone, source_url, confidence, created_at';
    RAISE NOTICE '✅ % index créés pour tes besoins:', index_count;
    RAISE NOTICE '   - Index confidence (trier par fiabilité)';
    RAISE NOTICE '   - Index source_url (filtrer par site)';
    RAISE NOTICE '   - Index composite (URL + fiabilité)';
    RAISE NOTICE '✅ Contraintes: email unique, validation email/téléphone';
    RAISE NOTICE '✅ 2 vues: personnes_fiables, stats_par_source';
    RAISE NOTICE '🎉 Setup terminé ! Lance ton scraper.';
END $$;

-- ========================================
-- 📝 EXEMPLES DE REQUÊTES (pour tes besoins)
-- ========================================

-- BESOIN 1: Trier tous les contacts par fiabilité (du plus fiable au moins fiable)
-- SELECT * FROM personnes ORDER BY confidence DESC;

-- BESOIN 2: Voir tous les contacts d'un site spécifique
-- SELECT * FROM personnes WHERE source_url = 'https://example.com';

-- COMBO: Contacts d'un site, triés par fiabilité (utilise index composite)
-- SELECT * FROM personnes WHERE source_url = 'https://example.com' ORDER BY confidence DESC;

-- Voir les contacts les plus fiables uniquement (confidence >= 0.8)
-- SELECT * FROM personnes_fiables;

-- Statistiques par site scrapé
-- SELECT * FROM stats_par_source;

-- Trouver les meilleurs contacts tous sites confondus
-- SELECT * FROM personnes WHERE confidence >= 0.9 ORDER BY confidence DESC LIMIT 100;
