"""
Contrôleur pour la partie normale (sans combats)
"""
from model.model_pg import (
    get_equipes_for_select, 
    get_equipe_by_id, 
    get_morpions_equipe,
    get_morpion_by_id,
    create_partie,
    terminer_partie,
    add_ligne_journal
)
from controleurs.includes import add_activity

# Enregistrer l'activité
add_activity(SESSION['HISTORIQUE'], "visite page partie normale")

# Initialiser les variables de session si besoin
if 'partie_normale' not in SESSION:
    SESSION['partie_normale'] = None

# Récupérer les équipes pour le formulaire
REQUEST_VARS['equipes'] = get_equipes_for_select(SESSION['CONNEXION'])
REQUEST_VARS['partie_en_cours'] = False
REQUEST_VARS['partie_terminee'] = False


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def verifier_victoire(grille, taille):
    """
    Vérifie si un joueur a gagné
    Retourne le numéro du joueur gagnant (1 ou 2) ou None
    """
    # Vérifier les lignes
    for ligne in range(taille):
        debut = ligne * taille
        cases = [grille[debut + col] for col in range(taille)]
        gagnant = verifier_alignement(cases)
        if gagnant:
            return gagnant
    
    # Vérifier les colonnes
    for col in range(taille):
        cases = [grille[ligne * taille + col] for ligne in range(taille)]
        gagnant = verifier_alignement(cases)
        if gagnant:
            return gagnant
    
    # Vérifier diagonale principale
    cases = [grille[i * taille + i] for i in range(taille)]
    gagnant = verifier_alignement(cases)
    if gagnant:
        return gagnant
    
    # Vérifier diagonale inverse
    cases = [grille[i * taille + (taille - 1 - i)] for i in range(taille)]
    gagnant = verifier_alignement(cases)
    if gagnant:
        return gagnant
    
    return None


def verifier_alignement(cases):
    """
    Vérifie si toutes les cases sont du même joueur
    """
    # Vérifier que toutes les cases sont remplies
    if any(case == '' for case in cases):
        return None
    
    # Vérifier que toutes appartiennent au même joueur
    joueur = cases[0]['joueur']
    if all(case['joueur'] == joueur for case in cases):
        return joueur
    
    return None


def est_grille_pleine(grille):
    """
    Vérifie si la grille est pleine
    """
    return all(case != '' for case in grille)


# ============================================================
# CRÉER UNE NOUVELLE PARTIE
# ============================================================
if POST and 'bouton_creer_partie' in POST:
    equipe1_id = POST['equipe1'][0]
    equipe2_id = POST['equipe2'][0]
    taille = int(POST['taille'][0])
    max_tours = int(POST['max_tours'][0])
    
    # Vérifier que les 2 équipes sont différentes
    if equipe1_id == equipe2_id:
        REQUEST_VARS['message'] = "Choisissez deux équipes différentes !"
        REQUEST_VARS['message_class'] = "alert-error"
    else:
        # Récupérer les infos des équipes
        equipe1 = get_equipe_by_id(SESSION['CONNEXION'], equipe1_id)
        equipe2 = get_equipe_by_id(SESSION['CONNEXION'], equipe2_id)
        
        # Créer la partie dans la BD
        result = create_partie(SESSION['CONNEXION'], equipe1_id, equipe2_id, taille, max_tours)
        id_partie, id_journal = result
        
        if id_partie:
            # Initialiser la partie en session
            SESSION['partie_normale'] = {
                'id_partie': id_partie,
                'id_journal': id_journal,
                'equipe1': equipe1,
                'equipe2': equipe2,
                'taille': taille,
                'max_tours': max_tours,
                'tour_actuel': 1,
                'joueur_courant': 1,
                'grille': [''] * (taille * taille),
                'morpion_selectionne': None,
                'morpions_utilises_eq1': [],
                'morpions_utilises_eq2': []
            }
            REQUEST_VARS['message'] = "Partie créée ! C'est parti !"
            REQUEST_VARS['message_class'] = "alert-success"
        else:
            REQUEST_VARS['message'] = "Erreur lors de la création de la partie."
            REQUEST_VARS['message_class'] = "alert-error"


# ============================================================
# ABANDONNER LA PARTIE
# ============================================================
if POST and 'bouton_abandonner' in POST:
    if SESSION['partie_normale']:
        SESSION['partie_normale'] = None
        REQUEST_VARS['message'] = "Partie abandonnée."
        REQUEST_VARS['message_class'] = "alert-warning"


# ============================================================
# SÉLECTIONNER UN MORPION
# ============================================================
if POST and 'morpion_choisi' in POST:
    if SESSION['partie_normale']:
        SESSION['partie_normale']['morpion_selectionne'] = POST['morpion_choisi'][0]


# ============================================================
# JOUER UN COUP
# ============================================================
if POST and 'case_jouee' in POST and 'morpion_choisi' not in POST and 'bouton_abandonner' not in POST:
    partie = SESSION['partie_normale']
    
    if partie:
        case_id = int(POST['case_jouee'][0])
        morpion_id = partie['morpion_selectionne']
        
        # Vérifier qu'un morpion est sélectionné
        if not morpion_id:
            REQUEST_VARS['message'] = "Sélectionnez d'abord un morpion !"
            REQUEST_VARS['message_class'] = "alert-error"
        
        # Vérifier que la case est vide
        elif partie['grille'][case_id] != '':
            REQUEST_VARS['message'] = "Cette case est déjà occupée !"
            REQUEST_VARS['message_class'] = "alert-error"
        
        else:
            # Récupérer les infos du morpion
            morpion = get_morpion_by_id(SESSION['CONNEXION'], morpion_id)
            
            # Déterminer la couleur selon le joueur
            if partie['joueur_courant'] == 1:
                couleur = partie['equipe1'][2]
                partie['morpions_utilises_eq1'].append(morpion_id)
                nom_equipe = partie['equipe1'][1]
            else:
                couleur = partie['equipe2'][2]
                partie['morpions_utilises_eq2'].append(morpion_id)
                nom_equipe = partie['equipe2'][1]
            
            # Placer le morpion
            partie['grille'][case_id] = {
                'id': morpion_id,
                'nom': morpion[1],
                'image': morpion[2],
                'couleur': couleur,
                'joueur': partie['joueur_courant']
            }
            
            # Enregistrer l'action dans le journal
            add_ligne_journal(
                SESSION['CONNEXION'],
                partie['id_journal'],
                f"{morpion[1]} placé en case {case_id} par {nom_equipe}"
            )
            
            # Vérifier victoire
            gagnant = verifier_victoire(partie['grille'], partie['taille'])
            
            if gagnant:
                # Partie gagnée !
                if gagnant == 1:
                    nom_gagnant = partie['equipe1'][1]
                else:
                    nom_gagnant = partie['equipe2'][1]
                
                # Enregistrer la victoire dans le journal
                add_ligne_journal(
                    SESSION['CONNEXION'],
                    partie['id_journal'],
                    f"Victoire de {nom_gagnant} !"
                )
                
                terminer_partie(SESSION['CONNEXION'], partie['id_partie'], nom_gagnant)
                REQUEST_VARS['partie_terminee'] = True
                REQUEST_VARS['gagnant'] = nom_gagnant
                SESSION['partie_normale'] = None
            
            elif est_grille_pleine(partie['grille']):
                # Match nul
                add_ligne_journal(
                    SESSION['CONNEXION'],
                    partie['id_journal'],
                    "Match nul - grille pleine"
                )
                
                terminer_partie(SESSION['CONNEXION'], partie['id_partie'], None)
                REQUEST_VARS['partie_terminee'] = True
                REQUEST_VARS['gagnant'] = None
                SESSION['partie_normale'] = None
            
            elif partie['tour_actuel'] >= partie['max_tours']:
                # Nombre max de tours atteint
                add_ligne_journal(
                    SESSION['CONNEXION'],
                    partie['id_journal'],
                    "Match nul - nombre max de tours atteint"
                )
                
                terminer_partie(SESSION['CONNEXION'], partie['id_partie'], None)
                REQUEST_VARS['partie_terminee'] = True
                REQUEST_VARS['gagnant'] = None
                SESSION['partie_normale'] = None
            
            else:
                # Passer au joueur suivant
                if partie['joueur_courant'] == 1:
                    partie['joueur_courant'] = 2
                else:
                    partie['joueur_courant'] = 1
                    partie['tour_actuel'] += 1
                
                partie['morpion_selectionne'] = None


# ============================================================
# PRÉPARER LES DONNÉES POUR LE TEMPLATE
# ============================================================
if SESSION['partie_normale']:
    partie = SESSION['partie_normale']
    
    REQUEST_VARS['partie_en_cours'] = True
    REQUEST_VARS['equipe1'] = partie['equipe1']
    REQUEST_VARS['equipe2'] = partie['equipe2']
    REQUEST_VARS['taille'] = partie['taille']
    REQUEST_VARS['max_tours'] = partie['max_tours']
    REQUEST_VARS['tour_actuel'] = partie['tour_actuel']
    REQUEST_VARS['grille'] = partie['grille']
    REQUEST_VARS['morpion_selectionne'] = partie['morpion_selectionne']
    
    # Équipe courante
    if partie['joueur_courant'] == 1:
        REQUEST_VARS['equipe_courante'] = partie['equipe1']
        morpions = get_morpions_equipe(SESSION['CONNEXION'], partie['equipe1'][0])
        # Filtrer les morpions déjà utilisés
        REQUEST_VARS['morpions_disponibles'] = [m for m in morpions if m[0] not in partie['morpions_utilises_eq1']]
    else:
        REQUEST_VARS['equipe_courante'] = partie['equipe2']
        morpions = get_morpions_equipe(SESSION['CONNEXION'], partie['equipe2'][0])
        REQUEST_VARS['morpions_disponibles'] = [m for m in morpions if m[0] not in partie['morpions_utilises_eq2']]
