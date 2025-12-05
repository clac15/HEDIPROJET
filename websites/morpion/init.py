"""
Fichier d'initialisation - chargé au démarrage
"""
from datetime import datetime
from os import path

SESSION['APP'] = "Mord ton pion"
SESSION['BASELINE'] = "à l'attaque !"
SESSION['DIR_HISTORIQUE'] = path.join(SESSION['DIRECTORY'], "historiques")
SESSION['HISTORIQUE'] = dict()
SESSION['CURRENT_YEAR'] = datetime.now().year
