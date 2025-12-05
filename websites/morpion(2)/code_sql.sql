

DROP SCHEMA IF EXISTS morpion CASCADE;
CREATE SCHEMA IF NOT EXISTS morpion;
SET search_path TO morpion;

-- Table des morpions (templates/modèles)
CREATE TABLE Morpion(
   idMorpion VARCHAR(50) PRIMARY KEY,
   nomMorpion VARCHAR(100) NOT NULL,
   image VARCHAR(200),
   pts_de_vie INT CHECK (pts_de_vie >= 1),
   pts_d_attaque INT CHECK (pts_d_attaque >= 1),
   pts_de_mana INT CHECK (pts_de_mana >= 1),
   pts_de_reussite INT CHECK (pts_de_reussite >= 1),
   -- Contrainte : la somme des points doit être exactement 15 (par défaut)
   CONSTRAINT check_sum_points CHECK (pts_de_vie + pts_d_attaque + pts_de_mana + pts_de_reussite = 15)
);

-- Table des configurations de partie
CREATE TABLE Configuration_(
   idConfiguration VARCHAR(50) PRIMARY KEY,
   dateConfig DATE NOT NULL,
   tailleGrille INT CHECK (tailleGrille IN (3, 4)),  -- Grille 3x3 ou 4x4
   nombre_max_de_tours INT CHECK (nombre_max_de_tours > 0)
);

-- Table des journaux (un journal par partie)
CREATE TABLE Journal(
   idJournal VARCHAR(50) PRIMARY KEY,
   nb_lignes INT DEFAULT 0  -- Nombre de lignes dans le journal
);

-- Table des lignes de journal (actions détaillées)
CREATE TABLE Ligne(
   Id_Ligne SERIAL PRIMARY KEY,
   numero_ligne INT NOT NULL,  -- Numéro unique au niveau de la partie
   dateAction TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   descriptionAction TEXT NOT NULL,
   idJournal VARCHAR(50) NOT NULL REFERENCES Journal(idJournal) ON DELETE CASCADE
);

-- Table des parties
CREATE TABLE Partie(
   idPartie VARCHAR(50) PRIMARY KEY,
   dateDebut TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   dateFin TIMESTAMP,
   gagnant VARCHAR(100),  -- Nom de l'équipe gagnante (NULL si pas de gagnant)
   idJournal VARCHAR(50) NOT NULL REFERENCES Journal(idJournal),
   idConfiguration VARCHAR(50) NOT NULL REFERENCES Configuration_(idConfiguration)
);

-- Table des équipes
CREATE TABLE Equipe(
   idEquipe VARCHAR(50) PRIMARY KEY,
   nomEquipe VARCHAR(100) NOT NULL UNIQUE,
   couleur VARCHAR(50) NOT NULL,  -- Ex: '#FF0000' ou 'red'
   dateEquipe DATE NOT NULL,
   nb_morpions INT CHECK (nb_morpions BETWEEN 6 AND 8)
);

-- Table d'association : une partie oppose 2 équipes
CREATE TABLE Partie_Equipe(
   idPartie VARCHAR(50) REFERENCES Partie(idPartie) ON DELETE CASCADE,
   idEquipe VARCHAR(50) REFERENCES Equipe(idEquipe) ON DELETE CASCADE,
   numero_equipe INT CHECK (numero_equipe IN (1, 2)),  -- Équipe 1 ou 2
   PRIMARY KEY(idPartie, idEquipe)
);

-- Table d'association : un morpion peut appartenir à plusieurs équipes
CREATE TABLE Morpion_Equipe(
   idMorpion VARCHAR(50) REFERENCES Morpion(idMorpion) ON DELETE CASCADE,
   idEquipe VARCHAR(50) REFERENCES Equipe(idEquipe) ON DELETE CASCADE,
   PRIMARY KEY(idMorpion, idEquipe)
);

-- ===== INSERTION DES MORPIONS =====
-- 10 morpions avec des caractéristiques variées (somme = 15)

-- Guerriers (fort en attaque)
INSERT INTO Morpion VALUES ('t1', 'ElFuego', 't1.png', 4, 6, 2, 3);
INSERT INTO Morpion VALUES ('t2', 'Cavaliero', 't5.png', 5, 5, 2, 3);
INSERT INTO Morpion VALUES ('t3', 'Bucherono', 't9.png', 6, 4, 2, 3);

-- Mages (fort en mana)
INSERT INTO Morpion VALUES ('t4', 'ElDiablo', 't3.png', 3, 2, 6, 4);
INSERT INTO Morpion VALUES ('t5', 'Captaino', 't8.png', 3, 3, 5, 4);

-- Équilibrés
INSERT INTO Morpion VALUES ('t6', 'Cyclopio', 't2.png', 4, 4, 4, 3);
INSERT INTO Morpion VALUES ('t7', 'Maskito', 't4.png', 4, 3, 4, 4);

-- Tanks (beaucoup de vie)
INSERT INTO Morpion VALUES ('t8', 'Bandano', 't6.png', 6, 3, 3, 3);
INSERT INTO Morpion VALUES ('t9', 'Ninjago', 't7.png', 5, 4, 3, 3);

-- Chanceux (haute réussite)
INSERT INTO Morpion VALUES ('t10', 'Vacancia', 't10.png', 3, 3, 3, 6);

-- ===== DONNÉES DE TEST =====

-- Configurations
INSERT INTO Configuration_ VALUES ('cfg_001', '2025-01-15', 3, 50);
INSERT INTO Configuration_ VALUES ('cfg_002', '2025-01-20', 4, 100);

-- Équipes de test
INSERT INTO Equipe VALUES ('eq_001', 'Les Guerriers du Feu', '#FF4444', '2025-01-10', 6);
INSERT INTO Equipe VALUES ('eq_002', 'Les Mages de Glace', '#4444FF', '2025-01-12', 7);
INSERT INTO Equipe VALUES ('eq_003', 'Les Ninjas Masqués', '#44FF44', '2025-01-14', 8);

-- Association morpions-équipes
-- Équipe 1 : Guerriers du Feu
INSERT INTO Morpion_Equipe VALUES ('t1', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t2', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t3', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t8', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t9', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t6', 'eq_001');

-- Équipe 2 : Mages de Glace
INSERT INTO Morpion_Equipe VALUES ('t4', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t5', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t6', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t7', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t10', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t1', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t2', 'eq_002');

-- Équipe 3 : Ninjas Masqués
INSERT INTO Morpion_Equipe VALUES ('t9', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t7', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t10', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t4', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t5', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t6', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t8', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t3', 'eq_003');

-- Journaux de test
INSERT INTO Journal VALUES ('jrnl_001', 0);
INSERT INTO Journal VALUES ('jrnl_002', 0);

-- Parties de test
INSERT INTO Partie VALUES ('part_001', '2025-01-15 14:30:00', '2025-01-15 15:00:00', 'Les Guerriers du Feu', 'jrnl_001', 'cfg_001');
INSERT INTO Partie VALUES ('part_002', '2025-01-20 16:00:00', '2025-01-20 17:30:00', 'Les Mages de Glace', 'jrnl_002', 'cfg_002');

-- Association parties-équipes
INSERT INTO Partie_Equipe VALUES ('part_001', 'eq_001', 1);
INSERT INTO Partie_Equipe VALUES ('part_001', 'eq_002', 2);
INSERT INTO Partie_Equipe VALUES ('part_002', 'eq_002', 1);
INSERT INTO Partie_Equipe VALUES ('part_002', 'eq_003', 2);

-- Lignes de journal
INSERT INTO Ligne (numero_ligne, dateAction, descriptionAction, idJournal) 
VALUES (1, '2025-01-15 14:30:05', 'Équipe 1 place ElFuego en (1,1)', 'jrnl_001');
INSERT INTO Ligne (numero_ligne, dateAction, descriptionAction, idJournal) 
VALUES (2, '2025-01-15 14:30:15', 'Équipe 2 place ElDiablo en (2,2)', 'jrnl_001');
INSERT INTO Ligne (numero_ligne, dateAction, descriptionAction, idJournal) 
VALUES (3, '2025-01-15 14:30:25', 'ElFuego attaque ElDiablo pour 6 dégâts', 'jrnl_001');

-- Mise à jour du nombre de lignes dans les journaux
UPDATE Journal SET nb_lignes = 3 WHERE idJournal = 'jrnl_001';

-- ===== VUES UTILES =====

-- Vue pour afficher les équipes avec leur nombre de victoires
CREATE VIEW v_equipes_stats AS
SELECT 
    e.idEquipe,
    e.nomEquipe,
    e.couleur,
    e.dateEquipe,
    COUNT(p.idPartie) as nb_victoires
FROM Equipe e
LEFT JOIN Partie p ON e.nomEquipe = p.gagnant
GROUP BY e.idEquipe, e.nomEquipe, e.couleur, e.dateEquipe;

-- Vue pour afficher les morpions d'une équipe
CREATE VIEW v_equipes_morpions AS
SELECT 
    e.nomEquipe,
    e.couleur,
    m.nomMorpion,
    m.image,
    m.pts_de_vie,
    m.pts_d_attaque,
    m.pts_de_mana,
    m.pts_de_reussite
FROM Equipe e
JOIN Morpion_Equipe me ON e.idEquipe = me.idEquipe
JOIN Morpion m ON me.idMorpion = m.idMorpion;

-- ===== TEST DES DONNÉES =====
-- Vérifier que tout est bien inséré
SELECT 'Morpions' as table_name, COUNT(*) as nb_lignes FROM Morpion
UNION ALL
SELECT 'Équipes', COUNT(*) FROM Equipe
UNION ALL
SELECT 'Parties', COUNT(*) FROM Partie
UNION ALL
SELECT 'Configurations', COUNT(*) FROM Configuration_
UNION ALL
SELECT 'Journaux', COUNT(*) FROM Journal;

COMMIT;
