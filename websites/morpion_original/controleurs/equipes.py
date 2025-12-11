"""
Contrôleur pour afficher et supprimer les équipes
"""
from model.model_pg import get_all_equipes, get_morpions_equipe, delete_equipe
from controleurs.includes import add_activity

# Enregistrer l'activité
add_activity(SESSION['HISTORIQUE'], "visite page équipes")

# Récupérer toutes les équipes
REQUEST_VARS['equipes'] = get_all_equipes(SESSION['CONNEXION'])

# Récupérer les morpions de chaque équipe
REQUEST_VARS['morpions_par_equipe'] = {}
if REQUEST_VARS['equipes']:
    for equipe in REQUEST_VARS['equipes']:
        id_equipe = equipe[0]
        REQUEST_VARS['morpions_par_equipe'][id_equipe] = get_morpions_equipe(SESSION['CONNEXION'], id_equipe)

# Traitement suppression
if POST and 'bouton_supprimer' in POST:
    id_equipe = POST['id_equipe_suppr'][0]
    
    # Trouver le nom de l'équipe
    nom_equipe = "inconnue"
    for equipe in REQUEST_VARS['equipes']:
        if equipe[0] == id_equipe:
            nom_equipe = equipe[1]
            break
    
    # Supprimer
    result = delete_equipe(SESSION['CONNEXION'], id_equipe)
    
    if result:
        REQUEST_VARS['message'] = f"Équipe '{nom_equipe}' supprimée !"
        REQUEST_VARS['message_class'] = "alert-success"
        # Recharger la liste
        REQUEST_VARS['equipes'] = get_all_equipes(SESSION['CONNEXION'])
        REQUEST_VARS['morpions_par_equipe'] = {}
        if REQUEST_VARS['equipes']:
            for equipe in REQUEST_VARS['equipes']:
                id_equipe = equipe[0]
                REQUEST_VARS['morpions_par_equipe'][id_equipe] = get_morpions_equipe(SESSION['CONNEXION'], id_equipe)
    else:
        REQUEST_VARS['message'] = "Erreur lors de la suppression."
        REQUEST_VARS['message_class'] = "alert-error"
