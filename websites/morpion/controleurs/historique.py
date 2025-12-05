"""
Contrôleur pour l'historique
"""
from controleurs.includes import add_activity
from tempfile import mkstemp
from os.path import isfile, basename
from os import access, R_OK

# Enregistrer l'activité
add_activity(SESSION['HISTORIQUE'], "visite page historique")

# Génération du fichier
if POST and 'bouton_generer' in POST:
    # Créer un fichier temporaire
    filepath = mkstemp(suffix='.txt', dir=SESSION['DIR_HISTORIQUE'])[1]
    
    # Écrire l'historique dedans
    with open(filepath, 'w') as fichier:
        for date, activite in SESSION['HISTORIQUE'].items():
            fichier.write(f"{date} - {activite}\n")
    
    # Vérifier que le fichier existe
    if isfile(filepath) and access(filepath, R_OK):
        REQUEST_VARS['fichier_genere'] = basename(filepath)
    else:
        REQUEST_VARS['message'] = "Erreur lors de la génération du fichier."
        REQUEST_VARS['message_class'] = "alert-error"

