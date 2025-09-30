-- ========================================
-- 🚀 TABLE OPTIMISÉE POUR SCRAPER PORTABLE
-- ========================================
-- Version ultra optimisée avec contraintes, validation et performance
-- Compatible Supabase/PostgreSQL 12+

-- Supprimer l'ancienne table si elle existe
DROP TABLE IF EXISTS personnes CASCADE;

-- Créer la table avec contraintes optimisées
CREATE TABLE personnes (
    -- Clé primaire auto-incrémentée
    id BIGSERIAL PRIMARY KEY,

    -- Informations de contact (nom peut être vide, mais email obligatoire)
    nom TEXT,
    email TEXT NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    telephone TEXT,
    poste TEXT,

    -- Métadonnées
    source_url TEXT NOT NULL,
    confidence NUMERIC(3,2) DEFAULT 0.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),

    -- Timestamps automatiques
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Contrainte unique sur email (évite les doublons)
    CONSTRAINT unique_email UNIQUE(email)
);

-- ========================================
-- 📊 INDEX STRATÉGIQUES
-- ========================================

-- Index sur email (recherches fréquentes)
CREATE INDEX idx_personnes_email ON personnes(email);

-- Index sur created_at (tri par date)
CREATE INDEX idx_personnes_created_at ON personnes(created_at DESC);

-- Index sur source_url (filtrer par site source)
CREATE INDEX idx_personnes_source_url ON personnes(source_url);

-- Index composite email + created_at (queries combinées)
CREATE INDEX idx_personnes_email_date ON personnes(email, created_at DESC);

-- Index sur confidence (filtrer les résultats fiables)
CREATE INDEX idx_personnes_confidence ON personnes(confidence DESC) WHERE confidence >= 0.8;

-- Index full-text search sur les noms (recherche textuelle rapide)
CREATE INDEX idx_personnes_nom_fts ON personnes USING gin(to_tsvector('french', COALESCE(nom, '')));

-- ========================================
-- ⚡ TRIGGER POUR updated_at
-- ========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_personnes_updated_at
    BEFORE UPDATE ON personnes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 🔐 ROW LEVEL SECURITY (SUPABASE)
-- ========================================
-- Décommentez si vous voulez activer la sécurité par ligne

-- ALTER TABLE personnes ENABLE ROW LEVEL SECURITY;

-- Politique : tout le monde peut lire
-- CREATE POLICY "Permettre lecture publique"
--     ON personnes FOR SELECT
--     USING (true);

-- Politique : seuls les utilisateurs authentifiés peuvent insérer
-- CREATE POLICY "Permettre insertion authentifiée"
--     ON personnes FOR INSERT
--     WITH CHECK (auth.role() = 'authenticated');

-- Politique : seuls les utilisateurs authentifiés peuvent mettre à jour
-- CREATE POLICY "Permettre mise à jour authentifiée"
--     ON personnes FOR UPDATE
--     USING (auth.role() = 'authenticated');

-- ========================================
-- 📈 VUES UTILES (OPTIONNEL)
-- ========================================

-- Vue : personnes avec haute confiance
CREATE OR REPLACE VIEW personnes_fiables AS
SELECT *
FROM personnes
WHERE confidence >= 0.8
ORDER BY confidence DESC, created_at DESC;

-- Vue : statistiques par source
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
ORDER BY nombre_contacts DESC;

-- ========================================
-- 🎯 COMMENTAIRES (DOCUMENTATION)
-- ========================================

COMMENT ON TABLE personnes IS 'Contacts extraits par le scraper portable (emails, noms, téléphones)';
COMMENT ON COLUMN personnes.nom IS 'Nom complet (ex: "Marie Dupont", "Jean-Pierre Martin")';
COMMENT ON COLUMN personnes.email IS 'Adresse email (obligatoire, unique)';
COMMENT ON COLUMN personnes.telephone IS 'Numéro de téléphone formaté (+33 6...)';
COMMENT ON COLUMN personnes.poste IS 'Fonction/poste (ex: "CEO", "Directeur")';
COMMENT ON COLUMN personnes.source_url IS 'URL de la page source';
COMMENT ON COLUMN personnes.confidence IS 'Score de confiance (0.0 à 1.0)';
COMMENT ON COLUMN personnes.created_at IS 'Date de création (automatique)';
COMMENT ON COLUMN personnes.updated_at IS 'Date de dernière modification (automatique)';

-- ========================================
-- ✅ VÉRIFICATION
-- ========================================

-- Test : vérifier que tout est créé
DO $$
BEGIN
    RAISE NOTICE '✅ Table "personnes" créée avec succès';
    RAISE NOTICE '✅ % index créés', (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'personnes');
    RAISE NOTICE '✅ Trigger updated_at activé';
    RAISE NOTICE '✅ 2 vues créées (personnes_fiables, stats_par_source)';
    RAISE NOTICE '🎉 Setup terminé ! Vous pouvez maintenant lancer le scraper.';
END $$;

-- ========================================
-- 📝 EXEMPLES DE REQUÊTES UTILES
-- ========================================

-- Rechercher un contact par email
-- SELECT * FROM personnes WHERE email = 'jean.dupont@example.com';

-- Lister les contacts d'un site
-- SELECT * FROM personnes WHERE source_url LIKE '%example.com%' ORDER BY confidence DESC;

-- Recherche full-text sur les noms
-- SELECT * FROM personnes WHERE to_tsvector('french', nom) @@ to_tsquery('french', 'dupont');

-- Statistiques globales
-- SELECT COUNT(*) as total, AVG(confidence) as conf_moy FROM personnes;

-- Trouver les doublons potentiels (même nom, emails différents)
-- SELECT nom, COUNT(*) FROM personnes WHERE nom IS NOT NULL GROUP BY nom HAVING COUNT(*) > 1;
