"""
Contrôleur pour la page d'accueil
"""
from model.model_pg import get_count_table, get_top_equipes, get_partie_rapide, get_partie_longue, get_activite_mensuelle
from controleurs.includes import add_activity

# Enregistrer l'activité
add_activity(SESSION['HISTORIQUE'], "visite page accueil")

# Récupérer les statistiques
REQUEST_VARS['nb_morpions'] = get_count_table(SESSION['CONNEXION'], 'morpion')
REQUEST_VARS['nb_equipes'] = get_count_table(SESSION['CONNEXION'], 'equipe')
REQUEST_VARS['nb_parties'] = get_count_table(SESSION['CONNEXION'], 'partie')

REQUEST_VARS['top_equipes'] = get_top_equipes(SESSION['CONNEXION'])
REQUEST_VARS['partie_rapide'] = get_partie_rapide(SESSION['CONNEXION'])
REQUEST_VARS['partie_longue'] = get_partie_longue(SESSION['CONNEXION'])
REQUEST_VARS['activite_mensuelle'] = get_activite_mensuelle(SESSION['CONNEXION'])



