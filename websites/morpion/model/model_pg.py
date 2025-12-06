"""
Modèle - Fonctions d'accès à la base de données PostgreSQL
"""
import psycopg
from psycopg import sql
from datetime import datetime

# ============================================================
# FONCTIONS GÉNÉRIQUES
# ============================================================

def execute_select(connexion, query, params=[]):
    """
    Exécute une requête SELECT et retourne les résultats
    """
    try:
        with connexion.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except psycopg.Error as e:
        print(f"Erreur SELECT : {e}")
        return None


def execute_insert_update_delete(connexion, query, params=[]):
    """
    Exécute une requête INSERT, UPDATE ou DELETE
    Retourne le nombre de lignes affectées
    """
    try:
        with connexion.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    except psycopg.Error as e:
        print(f"Erreur SQL : {e}")
        return None


# ============================================================
# FONCTIONS POUR LES STATISTIQUES (PAGE ACCUEIL)
# ============================================================

def get_count_table(connexion, nom_table):
    """
    Compte le nombre de lignes dans une table
    """
    query = f"SELECT COUNT(*) FROM morpion.{nom_table}"
    result = execute_select(connexion, query)
    if result:
        return result[0][0]
    return 0


def get_top_equipes(connexion):
    """
    Retourne le top 3 des équipes avec le plus de victoires
    """
    query = """
        SELECT e.nomEquipe, COUNT(p.idPartie), e.couleur
        FROM morpion.Equipe e
        LEFT JOIN morpion.Partie p ON e.nomEquipe = p.gagnant
        GROUP BY e.idEquipe, e.nomEquipe, e.couleur
        ORDER BY COUNT(p.idPartie) DESC
        LIMIT 3
    """
    return execute_select(connexion, query)


def get_partie_rapide(connexion):
    """
    Retourne la partie la plus rapide (moins de tours)
    """
    query = """
        SELECT p.gagnant, COUNT(l.Id_Ligne)
        FROM morpion.Partie p
        JOIN morpion.Journal j ON p.idJournal = j.idJournal
        JOIN morpion.Ligne l ON j.idJournal = l.idJournal
        WHERE p.dateFin IS NOT NULL
        GROUP BY p.idPartie, p.gagnant
        ORDER BY COUNT(l.Id_Ligne) ASC
        LIMIT 1
    """
    result = execute_select(connexion, query)
    if result:
        return result[0]
    return None


def get_partie_longue(connexion):
    """
    Retourne la partie la plus longue (plus de tours)
    """
    query = """
        SELECT p.gagnant, COUNT(l.Id_Ligne)
        FROM morpion.Partie p
        JOIN morpion.Journal j ON p.idJournal = j.idJournal
        JOIN morpion.Ligne l ON j.idJournal = l.idJournal
        WHERE p.dateFin IS NOT NULL
        GROUP BY p.idPartie, p.gagnant
        ORDER BY COUNT(l.Id_Ligne) DESC
        LIMIT 1
    """
    result = execute_select(connexion, query)
    if result:
        return result[0]
    return None


def get_activite_mensuelle(connexion):
    """
    Retourne le nombre d'actions par mois/année
    """
    query = """
        SELECT 
            EXTRACT(MONTH FROM dateAction),
            EXTRACT(YEAR FROM dateAction),
            COUNT(*)
        FROM morpion.Ligne
        GROUP BY EXTRACT(YEAR FROM dateAction), EXTRACT(MONTH FROM dateAction)
        ORDER BY EXTRACT(YEAR FROM dateAction) DESC, EXTRACT(MONTH FROM dateAction) DESC
        LIMIT 12
    """
    return execute_select(connexion, query)


# ============================================================
# FONCTIONS POUR LES MORPIONS
# ============================================================

def get_all_morpions(connexion):
    """
    Retourne tous les morpions
    """
    query = "SELECT * FROM morpion.Morpion ORDER BY nomMorpion"
    return execute_select(connexion, query)


def get_morpion_by_id(connexion, id_morpion):
    """
    Retourne un morpion par son ID
    """
    query = "SELECT * FROM morpion.Morpion WHERE idMorpion = %s"
    result = execute_select(connexion, query, [id_morpion])
    if result:
        return result[0]
    return None


# ============================================================
# FONCTIONS POUR LES ÉQUIPES
# ============================================================

def get_all_equipes(connexion):
    """
    Retourne toutes les équipes
    """
    query = "SELECT * FROM morpion.Equipe ORDER BY dateEquipe DESC"
    return execute_select(connexion, query)


def get_morpions_equipe(connexion, id_equipe):
    """
    Retourne les morpions d'une équipe
    """
    query = """
        SELECT m.*
        FROM morpion.Morpion m
        JOIN morpion.Morpion_Equipe me ON m.idMorpion = me.idMorpion
        WHERE me.idEquipe = %s
    """
    return execute_select(connexion, query, [id_equipe])


def insert_equipe(connexion, nom_equipe, couleur, morpions_ids):
    """
    Crée une nouvelle équipe avec ses morpions
    Retourne l'ID de l'équipe créée ou None si erreur
    """
    # Vérifier le nombre de morpions
    if len(morpions_ids) < 6 or len(morpions_ids) > 8:
        print("Erreur : une équipe doit avoir entre 6 et 8 morpions")
        return None
    
    try:
        # Générer un ID unique
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        id_equipe = f"eq_{timestamp}"
        date_creation = datetime.now().strftime('%Y-%m-%d')
        
        # Insérer l'équipe
        query_equipe = """
            INSERT INTO morpion.Equipe (idEquipe, nomEquipe, couleur, dateEquipe, nb_morpions)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_insert_update_delete(connexion, query_equipe, [
            id_equipe, nom_equipe, couleur, date_creation, len(morpions_ids)
        ])
        
        # Associer les morpions à l'équipe
        query_assoc = "INSERT INTO morpion.Morpion_Equipe (idMorpion, idEquipe) VALUES (%s, %s)"
        for morpion_id in morpions_ids:
            execute_insert_update_delete(connexion, query_assoc, [morpion_id, id_equipe])
        
        return id_equipe
        
    except Exception as e:
        print(f"Erreur création équipe : {e}")
        return None


def delete_equipe(connexion, id_equipe):
    """
    Supprime une équipe et ses associations
    """
    try:
        # D'abord supprimer les associations morpion-équipe
        query1 = "DELETE FROM morpion.Morpion_Equipe WHERE idEquipe = %s"
        execute_insert_update_delete(connexion, query1, [id_equipe])
        
        # Ensuite supprimer l'équipe
        query2 = "DELETE FROM morpion.Equipe WHERE idEquipe = %s"
        return execute_insert_update_delete(connexion, query2, [id_equipe])
        
    except Exception as e:
        print(f"Erreur suppression équipe : {e}")
        return None


# ============================================================
# FONCTIONS POUR LES PARTIES
# ============================================================

def create_partie(connexion, id_equipe1, id_equipe2, taille_grille, max_tours):
    """
    Crée une nouvelle partie
    Retourne l'ID de la partie créée ou None si erreur
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 1. Créer la configuration
        id_config = f"cfg_{timestamp}"
        date_config = datetime.now().strftime('%Y-%m-%d')
        query_config = """
            INSERT INTO morpion.Configuration_ (idConfiguration, dateConfig, tailleGrille, nombre_max_de_tours)
            VALUES (%s, %s, %s, %s)
        """
        execute_insert_update_delete(connexion, query_config, [id_config, date_config, taille_grille, max_tours])
        
        # 2. Créer le journal
        id_journal = f"jrnl_{timestamp}"
        query_journal = "INSERT INTO morpion.Journal (idJournal, nb_lignes) VALUES (%s, 0)"
        execute_insert_update_delete(connexion, query_journal, [id_journal])
        
        # 3. Créer la partie
        id_partie = f"part_{timestamp}"
        date_debut = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query_partie = """
            INSERT INTO morpion.Partie (idPartie, dateDebut, dateFin, gagnant, idJournal, idConfiguration)
            VALUES (%s, %s, NULL, NULL, %s, %s)
        """
        execute_insert_update_delete(connexion, query_partie, [id_partie, date_debut, id_journal, id_config])
        
        # 4. Associer les équipes
        query_equipe = "INSERT INTO morpion.Partie_Equipe (idPartie, idEquipe, numero_equipe) VALUES (%s, %s, %s)"
        execute_insert_update_delete(connexion, query_equipe, [id_partie, id_equipe1, 1])
        execute_insert_update_delete(connexion, query_equipe, [id_partie, id_equipe2, 2])
        
        return id_partie
        
    except Exception as e:
        print(f"Erreur création partie : {e}")
        return None


def add_ligne_journal(connexion, id_journal, description):
    """
    Ajoute une ligne au journal d'une partie
    """
    try:
        # Compter les lignes existantes
        query_count = "SELECT COUNT(*) FROM morpion.Ligne WHERE idJournal = %s"
        result = execute_select(connexion, query_count, [id_journal])
        numero = result[0][0] + 1 if result else 1
        
        # Insérer la nouvelle ligne
        query_insert = """
            INSERT INTO morpion.Ligne (numero_ligne, descriptionAction, idJournal)
            VALUES (%s, %s, %s)
        """
        execute_insert_update_delete(connexion, query_insert, [numero, description, id_journal])
        
        # Mettre à jour le compteur du journal
        query_update = "UPDATE morpion.Journal SET nb_lignes = %s WHERE idJournal = %s"
        execute_insert_update_delete(connexion, query_update, [numero, id_journal])
        
        return numero
        
    except Exception as e:
        print(f"Erreur ajout ligne journal : {e}")
        return None

# ============================================================
# FONCTIONS POUR LES PARTIES (à ajouter à model_pg.py)
# ============================================================

def get_equipes_for_select(connexion):
    """
    Retourne les équipes pour le menu déroulant (id, nom, couleur)
    """
    query = "SELECT idEquipe, nomEquipe, couleur FROM morpion.Equipe ORDER BY nomEquipe"
    return execute_select(connexion, query)


def get_equipe_by_id(connexion, id_equipe):
    """
    Retourne une équipe par son ID
    """
    query = "SELECT * FROM morpion.Equipe WHERE idEquipe = %s"
    result = execute_select(connexion, query, [id_equipe])
    if result:
        return result[0]
    return None


def get_partie_by_id(connexion, id_partie):
    """
    Retourne une partie par son ID
    """
    query = "SELECT * FROM morpion.Partie WHERE idPartie = %s"
    result = execute_select(connexion, query, [id_partie])
    if result:
        return result[0]
    return None


def get_config_by_id(connexion, id_config):
    """
    Retourne une configuration par son ID
    """
    query = "SELECT * FROM morpion.Configuration_ WHERE idConfiguration = %s"
    result = execute_select(connexion, query, [id_config])
    if result:
        return result[0]
    return None


def get_equipes_partie(connexion, id_partie):
    """
    Retourne les 2 équipes d'une partie
    """
    query = """
        SELECT e.*, pe.numero_equipe
        FROM morpion.Equipe e
        JOIN morpion.Partie_Equipe pe ON e.idEquipe = pe.idEquipe
        WHERE pe.idPartie = %s
        ORDER BY pe.numero_equipe
    """
    return execute_select(connexion, query, [id_partie])


def terminer_partie(connexion, id_partie, gagnant):
    """
    Termine une partie en enregistrant le gagnant et la date de fin
    """
    query = """
        UPDATE morpion.Partie 
        SET dateFin = %s, gagnant = %s 
        WHERE idPartie = %s
    """
    date_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return execute_insert_update_delete(connexion, query, [date_fin, gagnant, id_partie])