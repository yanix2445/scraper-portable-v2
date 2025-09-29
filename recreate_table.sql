-- ✅ TABLE EXACTE REPRODUITE DEPUIS VOTRE SUPABASE EXISTANTE
-- Structure analysée automatiquement
-- Donnez ce fichier à votre pote pour reproduire exactement votre table

DROP TABLE IF EXISTS personnes;

CREATE TABLE personnes (
    id SERIAL PRIMARY KEY,
    nom TEXT,  -- Nom complet (ex: "Marie Dupont", "Jean-Pierre Martin")
    email TEXT,
    telephone TEXT,
    poste TEXT,
    source_url TEXT,
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index (exactement comme chez vous)
CREATE INDEX idx_personnes_email ON personnes(email);
CREATE INDEX idx_personnes_created_at ON personnes(created_at);

-- Trigger pour updated_at automatique (si vous l'avez)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_personnes_updated_at
    BEFORE UPDATE ON personnes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
