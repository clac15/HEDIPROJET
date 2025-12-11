"""
Contrôleur pour créer une équipe
"""
from model.model_pg import get_all_morpions, get_all_equipes, insert_equipe
from controleurs.includes import add_activity

# Enregistrer l'activité
add_activity(SESSION['HISTORIQUE'], "visite page création équipe")

# Récupérer tous les morpions disponibles
REQUEST_VARS['morpions'] = get_all_morpions(SESSION['CONNEXION'])

# Traitement du formulaire
if POST and 'bouton_creer' in POST:
    nom_equipe = POST['nom_equipe'][0]
    couleur = POST['couleur_equipe'][0]
    morpions_selected = POST.get('morpions_selected', [])
    
    # Vérifications
    if not nom_equipe or not couleur:
        REQUEST_VARS['message'] = "Le nom et la couleur sont obligatoires."
        REQUEST_VARS['message_class'] = "alert-error"
    
    elif len(morpions_selected) < 6 or len(morpions_selected) > 8:
        REQUEST_VARS['message'] = f"Sélectionnez entre 6 et 8 morpions (vous en avez {len(morpions_selected)})."
        REQUEST_VARS['message_class'] = "alert-error"
    
    else:
        # Vérifier si le nom existe déjà
        equipes = get_all_equipes(SESSION['CONNEXION'])
        noms_existants = [eq[1] for eq in equipes] if equipes else []
        
        if nom_equipe in noms_existants:
            REQUEST_VARS['message'] = f"Une équipe '{nom_equipe}' existe déjà."
            REQUEST_VARS['message_class'] = "alert-error"
        
        else:
            # Créer l'équipe
            id_equipe = insert_equipe(SESSION['CONNEXION'], nom_equipe, couleur, morpions_selected)
            
            if id_equipe:
                REQUEST_VARS['message'] = f"Équipe '{nom_equipe}' créée avec succès !"
                REQUEST_VARS['message_class'] = "alert-success"
            else:
                REQUEST_VARS['message'] = "Erreur lors de la création."
                REQUEST_VARS['message_class'] = "alert-error"
