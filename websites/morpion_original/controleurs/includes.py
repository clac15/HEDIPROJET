"""
Fonctions utilisées par plusieurs contrôleurs
"""
from datetime import datetime


def add_activity(historique, activite):
    """
    Ajoute une activité dans l'historique avec la date actuelle
    """
    date = datetime.now()
    historique[date] = activite
