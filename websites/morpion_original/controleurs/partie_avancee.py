"""
Contrôleur pour la partie avancée (avec combats et sorts)
"""
from model.model_pg import (
    get_equipes_for_select, 
    get_equipe_by_id, 
    get_morpions_equipe,
    get_morpion_by_id,
    create_partie,
    terminer_partie
)
from controleurs.includes import add_activity
import random

# Enregistrer l'activité
add_activity(SESSION['HISTORIQUE'], "visite page partie avancée")

# Initialiser les variables de session si besoin
if 'partie_avancee' not in SESSION:
    SESSION['partie_avancee'] = None

# Récupérer les équipes pour le formulaire
REQUEST_VARS['equipes'] = get_equipes_for_select(SESSION['CONNEXION'])
REQUEST_VARS['partie_en_cours'] = False
REQUEST_VARS['partie_terminee'] = False
REQUEST_VARS['message_combat'] = None


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def verifier_victoire(grille, taille):
    """
    Vérifie si un joueur a gagné par alignement
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
    Vérifie si toutes les cases sont du même joueur (et pas détruites)
    """
    # Filtrer les cases vides ou détruites
    if any(case == '' or case == 'DESTROYED' for case in cases):
        return None
    
    joueur = cases[0]['joueur']
    if all(case['joueur'] == joueur for case in cases):
        return joueur
    
    return None


def est_partie_finie(partie):
    """
    Vérifie si la partie est finie (plus de morpions pour un joueur)
    Ne compte que si les deux équipes ont déjà placé des morpions
    """
    morpions_eq1 = 0
    morpions_eq2 = 0
    
    for case in partie['grille']:
        if case != '' and case != 'DESTROYED':
            if case['joueur'] == 1:
                morpions_eq1 += 1
            else:
                morpions_eq2 += 1
    
    # Ne vérifier l'élimination que si les deux équipes ont déjà joué
    # (au moins 1 morpion utilisé par chaque équipe)
    eq1_a_joue = len(partie['morpions_utilises_eq1']) > 0
    eq2_a_joue = len(partie['morpions_utilises_eq2']) > 0
    
    if eq1_a_joue and eq2_a_joue:
        if morpions_eq1 == 0:
            return 2  # Équipe 2 gagne
        elif morpions_eq2 == 0:
            return 1  # Équipe 1 gagne
    
    return None


def get_cases_adjacentes(case_id, taille):
    """
    Retourne les indices des cases adjacentes (haut, bas, gauche, droite)
    """
    adjacentes = []
    ligne = case_id // taille
    colonne = case_id % taille
    
    # Haut
    if ligne > 0:
        adjacentes.append(case_id - taille)
    # Bas
    if ligne < taille - 1:
        adjacentes.append(case_id + taille)
    # Gauche
    if colonne > 0:
        adjacentes.append(case_id - 1)
    # Droite
    if colonne < taille - 1:
        adjacentes.append(case_id + 1)
    
    return adjacentes


def test_reussite(pts_reussite):
    """
    Test si une action réussit basé sur les points de réussite
    Probabilité = 10 × pts_reussite (en %)
    """
    probabilite = pts_reussite * 10
    tirage = random.randint(1, 100)
    return tirage <= probabilite


def fin_tour(partie):
    """
    Termine le tour et vérifie les conditions de victoire
    """
    # Vérifier victoire par alignement
    gagnant = verifier_victoire(partie['grille'], partie['taille'])
    
    if gagnant:
        if gagnant == 1:
            nom_gagnant = partie['equipe1'][1]
        else:
            nom_gagnant = partie['equipe2'][1]
        
        terminer_partie(SESSION['CONNEXION'], partie['id_partie'], nom_gagnant)
        REQUEST_VARS['partie_terminee'] = True
        REQUEST_VARS['gagnant'] = nom_gagnant
        SESSION['partie_avancee'] = None
        return
    
    # Vérifier victoire par élimination
    gagnant_elim = est_partie_finie(partie)
    if gagnant_elim:
        if gagnant_elim == 1:
            nom_gagnant = partie['equipe1'][1]
        else:
            nom_gagnant = partie['equipe2'][1]
        
        terminer_partie(SESSION['CONNEXION'], partie['id_partie'], nom_gagnant)
        REQUEST_VARS['partie_terminee'] = True
        REQUEST_VARS['gagnant'] = nom_gagnant
        SESSION['partie_avancee'] = None
        return
    
    # Vérifier nombre max de tours
    if partie['tour_actuel'] >= partie['max_tours']:
        terminer_partie(SESSION['CONNEXION'], partie['id_partie'], None)
        REQUEST_VARS['partie_terminee'] = True
        REQUEST_VARS['gagnant'] = None
        SESSION['partie_avancee'] = None
        return
    
    # Passer au joueur suivant
    if partie['joueur_courant'] == 1:
        partie['joueur_courant'] = 2
    else:
        partie['joueur_courant'] = 1
        partie['tour_actuel'] += 1
    
    # Réinitialiser les sélections
    partie['morpion_selectionne'] = None
    partie['action_selectionnee'] = 'placer'
    partie['case_selectionnee'] = None


# ============================================================
# CRÉER UNE NOUVELLE PARTIE
# ============================================================
if POST and 'bouton_creer_partie' in POST:
    equipe1_id = POST['equipe1'][0]
    equipe2_id = POST['equipe2'][0]
    taille = int(POST['taille'][0])
    max_tours = int(POST['max_tours'][0])
    
    if equipe1_id == equipe2_id:
        REQUEST_VARS['message'] = "Choisissez deux équipes différentes !"
        REQUEST_VARS['message_class'] = "alert-error"
    else:
        equipe1 = get_equipe_by_id(SESSION['CONNEXION'], equipe1_id)
        equipe2 = get_equipe_by_id(SESSION['CONNEXION'], equipe2_id)
        
        id_partie = create_partie(SESSION['CONNEXION'], equipe1_id, equipe2_id, taille, max_tours)
        
        if id_partie:
            SESSION['partie_avancee'] = {
                'id_partie': id_partie,
                'equipe1': equipe1,
                'equipe2': equipe2,
                'taille': taille,
                'max_tours': max_tours,
                'tour_actuel': 1,
                'joueur_courant': 1,
                'grille': [''] * (taille * taille),
                'morpion_selectionne': None,
                'action_selectionnee': 'placer',
                'case_selectionnee': None,
                'morpions_utilises_eq1': [],
                'morpions_utilises_eq2': []
            }
            REQUEST_VARS['message'] = "Partie avancée créée ! C'est parti !"
            REQUEST_VARS['message_class'] = "alert-success"
        else:
            REQUEST_VARS['message'] = "Erreur lors de la création de la partie."
            REQUEST_VARS['message_class'] = "alert-error"


# ============================================================
# ABANDONNER LA PARTIE
# ============================================================
if POST and 'bouton_abandonner' in POST:
    if SESSION['partie_avancee']:
        SESSION['partie_avancee'] = None
        REQUEST_VARS['message'] = "Partie abandonnée."
        REQUEST_VARS['message_class'] = "alert-warning"


# ============================================================
# SÉLECTIONNER UN MORPION (pour placer)
# ============================================================
if POST and 'morpion_choisi' in POST:
    if SESSION['partie_avancee']:
        SESSION['partie_avancee']['morpion_selectionne'] = POST['morpion_choisi'][0]


# ============================================================
# SÉLECTIONNER UNE ACTION
# ============================================================
if POST and 'action_choisie' in POST:
    if SESSION['partie_avancee']:
        SESSION['partie_avancee']['action_selectionnee'] = POST['action_choisie'][0]
        SESSION['partie_avancee']['case_selectionnee'] = None


# ============================================================
# SÉLECTIONNER UN MORPION SUR LA GRILLE (pour attaque/sort)
# ============================================================
if POST and 'select_case' in POST:
    if SESSION['partie_avancee']:
        nouvelle_case = int(POST['select_case'][0])
        partie = SESSION['partie_avancee']
        
        # Vérifier que c'est bien un morpion du joueur courant
        case_contenu = partie['grille'][nouvelle_case]
        if case_contenu != '' and case_contenu != 'DESTROYED':
            if case_contenu['joueur'] == partie['joueur_courant']:
                partie['case_selectionnee'] = nouvelle_case

# ============================================================
# EXÉCUTER UNE ACTION
# ============================================================
if POST and 'case_jouee' in POST and 'morpion_choisi' not in POST and 'action_choisie' not in POST and 'select_case' not in POST and 'bouton_abandonner' not in POST:
    partie = SESSION['partie_avancee']
    
    if partie:
        case_cible = int(POST['case_jouee'][0])
        action = partie['action_selectionnee']
        morpion_id = partie['morpion_selectionne']
        case_source = partie['case_selectionnee']
        
        # ACTION: PLACER UN MORPION
        if action == 'placer':
            if not morpion_id:
                REQUEST_VARS['message'] = "Sélectionnez d'abord un morpion !"
                REQUEST_VARS['message_class'] = "alert-error"
            elif partie['grille'][case_cible] != '' and partie['grille'][case_cible] != 'DESTROYED':
                REQUEST_VARS['message'] = "Cette case est occupée !"
                REQUEST_VARS['message_class'] = "alert-error"
            elif partie['grille'][case_cible] == 'DESTROYED':
                REQUEST_VARS['message'] = "Cette case est détruite !"
                REQUEST_VARS['message_class'] = "alert-error"
            else:
                morpion = get_morpion_by_id(SESSION['CONNEXION'], morpion_id)
                
                if partie['joueur_courant'] == 1:
                    couleur = partie['equipe1'][2]
                    partie['morpions_utilises_eq1'].append(morpion_id)
                else:
                    couleur = partie['equipe2'][2]
                    partie['morpions_utilises_eq2'].append(morpion_id)
                
                partie['grille'][case_cible] = {
                    'id': morpion_id,
                    'nom': morpion[1],
                    'image': morpion[2],
                    'couleur': couleur,
                    'joueur': partie['joueur_courant'],
                    'pv': morpion[3],
                    'attaque': morpion[4],
                    'mana': morpion[5],
                    'reussite': morpion[6]
                }
                
                REQUEST_VARS['message_combat'] = f"✅ {morpion[1]} placé !"
                fin_tour(partie)
        
        # ACTION: ATTAQUER
        elif action == 'attaquer':
            if case_source is None:
                REQUEST_VARS['message'] = "Sélectionnez d'abord un de vos morpions sur la grille !"
                REQUEST_VARS['message_class'] = "alert-error"
            else:
                attaquant = partie['grille'][case_source]
                cible = partie['grille'][case_cible]
                
                if cible == '' or cible == 'DESTROYED':
                    REQUEST_VARS['message'] = "Pas de cible sur cette case !"
                    REQUEST_VARS['message_class'] = "alert-error"
                elif cible['joueur'] == partie['joueur_courant']:
                    REQUEST_VARS['message'] = "Vous ne pouvez pas attaquer votre propre équipe !"
                    REQUEST_VARS['message_class'] = "alert-error"
                elif case_cible not in get_cases_adjacentes(case_source, partie['taille']):
                    REQUEST_VARS['message'] = "La cible doit être sur une case adjacente !"
                    REQUEST_VARS['message_class'] = "alert-error"
                    partie['case_selectionnee'] = None  # AJOUT : permet de changer d'attaquant
                else:
                    if test_reussite(attaquant['reussite']):
                        degats = attaquant['attaque']
                        cible['pv'] -= degats
                        attaquant['reussite'] += 0.5
                        
                        REQUEST_VARS['message_combat'] = f"⚔️ {attaquant['nom']} attaque {cible['nom']} pour {degats} dégâts !"
                        
                        if cible['pv'] <= 0:
                            partie['grille'][case_cible] = ''
                            REQUEST_VARS['message_combat'] += f" 💀 {cible['nom']} est mort !"
                    else:
                        REQUEST_VARS['message_combat'] = f"❌ {attaquant['nom']} rate son attaque !"
                    
                    fin_tour(partie)
        
        # ACTION: BOULE DE FEU
        elif action == 'boule_de_feu':
            if case_source is None:
                REQUEST_VARS['message'] = "Sélectionnez d'abord un de vos morpions sur la grille !"
                REQUEST_VARS['message_class'] = "alert-error"
            else:
                lanceur = partie['grille'][case_source]
                cible = partie['grille'][case_cible]
                
                if lanceur['mana'] < 2:
                    REQUEST_VARS['message'] = f"Pas assez de mana ! (besoin: 2, actuel: {lanceur['mana']})"
                    REQUEST_VARS['message_class'] = "alert-error"
                    partie['case_selectionnee'] = None  # AJOUT : permet de changer de lanceur
                elif cible == '' or cible == 'DESTROYED':
                    REQUEST_VARS['message'] = "Pas de cible sur cette case !"
                    REQUEST_VARS['message_class'] = "alert-error"
                elif cible['joueur'] == partie['joueur_courant']:
                    REQUEST_VARS['message'] = "Vous ne pouvez pas cibler votre propre équipe !"
                    REQUEST_VARS['message_class'] = "alert-error"
                else:
                    lanceur['mana'] -= 2
                    
                    if test_reussite(lanceur['reussite']):
                        cible['pv'] -= 3
                        lanceur['reussite'] += 0.5
                        
                        REQUEST_VARS['message_combat'] = f"🔥 {lanceur['nom']} lance Boule de Feu sur {cible['nom']} (3 dégâts) !"
                        
                        if cible['pv'] <= 0:
                            partie['grille'][case_cible] = ''
                            REQUEST_VARS['message_combat'] += f" 💀 {cible['nom']} est mort !"
                    else:
                        REQUEST_VARS['message_combat'] = f"❌ {lanceur['nom']} rate sa Boule de Feu ! (mana consommé)"
                    
                    fin_tour(partie)
        
        # ACTION: SOIN
        elif action == 'soin':
            if case_source is None:
                REQUEST_VARS['message'] = "Sélectionnez d'abord un de vos morpions sur la grille !"
                REQUEST_VARS['message_class'] = "alert-error"
            else:
                lanceur = partie['grille'][case_source]
                cible = partie['grille'][case_cible]
                
                if lanceur['mana'] < 1:
                    REQUEST_VARS['message'] = f"Pas assez de mana ! (besoin: 1, actuel: {lanceur['mana']})"
                    REQUEST_VARS['message_class'] = "alert-error"
                    partie['case_selectionnee'] = None  # AJOUT : permet de changer de lanceur
                elif cible == '' or cible == 'DESTROYED':
                    REQUEST_VARS['message'] = "Pas de cible sur cette case !"
                    REQUEST_VARS['message_class'] = "alert-error"
                elif cible['joueur'] != partie['joueur_courant']:
                    REQUEST_VARS['message'] = "Vous ne pouvez soigner que votre propre équipe !"
                    REQUEST_VARS['message_class'] = "alert-error"
                else:
                    lanceur['mana'] -= 1
                    
                    if test_reussite(lanceur['reussite']):
                        cible['pv'] += 2
                        lanceur['reussite'] += 0.5
                        REQUEST_VARS['message_combat'] = f"💚 {lanceur['nom']} soigne {cible['nom']} (+2 PV) !"
                    else:
                        REQUEST_VARS['message_combat'] = f"❌ {lanceur['nom']} rate son Soin ! (mana consommé)"
                    
                    fin_tour(partie)
        
        # ACTION: ARMAGEDDON
        elif action == 'armageddon':
            if case_source is None:
                REQUEST_VARS['message'] = "Sélectionnez d'abord un de vos morpions sur la grille !"
                REQUEST_VARS['message_class'] = "alert-error"
            else:
                lanceur = partie['grille'][case_source]
                
                if lanceur['mana'] < 5:
                    REQUEST_VARS['message'] = f"Pas assez de mana ! (besoin: 5, actuel: {lanceur['mana']})"
                    REQUEST_VARS['message_class'] = "alert-error"
                    partie['case_selectionnee'] = None  # AJOUT : permet de changer de lanceur
                elif case_cible == case_source:
                    REQUEST_VARS['message'] = "Vous ne pouvez pas détruire votre propre case !"
                    REQUEST_VARS['message_class'] = "alert-error"
                elif partie['grille'][case_cible] == 'DESTROYED':
                    REQUEST_VARS['message'] = "Cette case est déjà détruite !"
                    REQUEST_VARS['message_class'] = "alert-error"
                else:
                    lanceur['mana'] -= 5
                    
                    if test_reussite(lanceur['reussite']):
                        cible = partie['grille'][case_cible]
                        if cible != '':
                            REQUEST_VARS['message_combat'] = f"💥 ARMAGEDDON ! {cible['nom']} est détruit avec la case !"
                        else:
                            REQUEST_VARS['message_combat'] = f"💥 ARMAGEDDON ! La case est détruite !"
                        
                        partie['grille'][case_cible] = 'DESTROYED'
                        lanceur['reussite'] += 0.5
                    else:
                        REQUEST_VARS['message_combat'] = f"❌ {lanceur['nom']} rate son Armageddon ! (mana consommé)"
                    
                    fin_tour(partie)


# ============================================================
# PRÉPARER LES DONNÉES POUR LE TEMPLATE
# ============================================================
if SESSION['partie_avancee']:
    partie = SESSION['partie_avancee']
    
    REQUEST_VARS['partie_en_cours'] = True
    REQUEST_VARS['equipe1'] = partie['equipe1']
    REQUEST_VARS['equipe2'] = partie['equipe2']
    REQUEST_VARS['taille'] = partie['taille']
    REQUEST_VARS['max_tours'] = partie['max_tours']
    REQUEST_VARS['tour_actuel'] = partie['tour_actuel']
    REQUEST_VARS['grille'] = partie['grille']
    REQUEST_VARS['morpion_selectionne'] = partie['morpion_selectionne']
    REQUEST_VARS['action_selectionnee'] = partie['action_selectionnee']
    REQUEST_VARS['case_selectionnee'] = partie['case_selectionnee']
    REQUEST_VARS['joueur_courant'] = partie['joueur_courant']
    
    if partie['joueur_courant'] == 1:
        REQUEST_VARS['equipe_courante'] = partie['equipe1']
        morpions = get_morpions_equipe(SESSION['CONNEXION'], partie['equipe1'][0])
        REQUEST_VARS['morpions_disponibles'] = [m for m in morpions if m[0] not in partie['morpions_utilises_eq1']]
    else:
        REQUEST_VARS['equipe_courante'] = partie['equipe2']
        morpions = get_morpions_equipe(SESSION['CONNEXION'], partie['equipe2'][0])
        REQUEST_VARS['morpions_disponibles'] = [m for m in morpions if m[0] not in partie['morpions_utilises_eq2']]
