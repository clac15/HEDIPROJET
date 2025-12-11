-- Script SQL pour le jeu Mord ton Pion
-- Base de données PostgreSQL

DROP SCHEMA IF EXISTS morpion CASCADE;
CREATE SCHEMA IF NOT EXISTS morpion;
SET search_path TO morpion;

-- Table des morpions (modèles/templates)
CREATE TABLE Morpion(
   idMorpion VARCHAR(50) PRIMARY KEY,
   nomMorpion VARCHAR(100) NOT NULL,
   image VARCHAR(200),
   pts_de_vie INT CHECK (pts_de_vie >= 1),
   pts_d_attaque INT CHECK (pts_d_attaque >= 1),
   pts_de_mana INT CHECK (pts_de_mana >= 1),
   pts_de_reussite INT CHECK (pts_de_reussite >= 1),
   CONSTRAINT check_sum_points CHECK (pts_de_vie + pts_d_attaque + pts_de_mana + pts_de_reussite = 15)
);

-- Table des configurations de partie
CREATE TABLE Configuration_(
   idConfiguration VARCHAR(50) PRIMARY KEY,
   dateConfig DATE NOT NULL,
   tailleGrille INT CHECK (tailleGrille IN (3, 4)),
   nombre_max_de_tours INT CHECK (nombre_max_de_tours > 0)
);

-- Table des journaux
CREATE TABLE Journal(
   idJournal VARCHAR(50) PRIMARY KEY,
   nb_lignes INT DEFAULT 0
);

-- Table des lignes de journal
CREATE TABLE Ligne(
   Id_Ligne SERIAL PRIMARY KEY,
   numero_ligne INT NOT NULL,
   dateAction TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   descriptionAction TEXT NOT NULL,
   idJournal VARCHAR(50) NOT NULL REFERENCES Journal(idJournal) ON DELETE CASCADE
);

-- Table des parties
CREATE TABLE Partie(
   idPartie VARCHAR(50) PRIMARY KEY,
   dateDebut TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   dateFin TIMESTAMP,
   gagnant VARCHAR(100),
   idJournal VARCHAR(50) NOT NULL REFERENCES Journal(idJournal),
   idConfiguration VARCHAR(50) NOT NULL REFERENCES Configuration_(idConfiguration)
);

-- Table des équipes
CREATE TABLE Equipe(
   idEquipe VARCHAR(50) PRIMARY KEY,
   nomEquipe VARCHAR(100) NOT NULL UNIQUE,
   couleur VARCHAR(50) NOT NULL,
   dateEquipe DATE NOT NULL,
   nb_morpions INT CHECK (nb_morpions BETWEEN 6 AND 8)
);

-- Table d'association partie-équipe
CREATE TABLE Partie_Equipe(
   idPartie VARCHAR(50) REFERENCES Partie(idPartie) ON DELETE CASCADE,
   idEquipe VARCHAR(50) REFERENCES Equipe(idEquipe) ON DELETE CASCADE,
   numero_equipe INT CHECK (numero_equipe IN (1, 2)),
   PRIMARY KEY(idPartie, idEquipe)
);

-- Table d'association morpion-équipe
CREATE TABLE Morpion_Equipe(
   idMorpion VARCHAR(50) REFERENCES Morpion(idMorpion) ON DELETE CASCADE,
   idEquipe VARCHAR(50) REFERENCES Equipe(idEquipe) ON DELETE CASCADE,
   PRIMARY KEY(idMorpion, idEquipe)
);

-- ===== INSERTION DES MORPIONS =====

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
INSERT INTO Morpion_Equipe VALUES ('t1', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t2', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t3', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t8', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t9', 'eq_001');
INSERT INTO Morpion_Equipe VALUES ('t6', 'eq_001');

INSERT INTO Morpion_Equipe VALUES ('t4', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t5', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t6', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t7', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t10', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t1', 'eq_002');
INSERT INTO Morpion_Equipe VALUES ('t2', 'eq_002');

INSERT INTO Morpion_Equipe VALUES ('t9', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t7', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t10', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t4', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t5', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t6', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t8', 'eq_003');
INSERT INTO Morpion_Equipe VALUES ('t3', 'eq_003');

-- Journaux de test
INSERT INTO Journal VALUES ('jrnl_001', 3);
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

-- ===== VÉRIFICATION =====
SELECT 'Morpions' as table_name, COUNT(*) as nb FROM Morpion
UNION ALL
SELECT 'Équipes', COUNT(*) FROM Equipe
UNION ALL
SELECT 'Parties', COUNT(*) FROM Partie;

COMMIT;
