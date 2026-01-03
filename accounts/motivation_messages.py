"""
Messages de motivation et conseils financiers pour MonNkap
"""
import random

# Messages pour les dépenses
EXPENSE_MESSAGES = [
    {
        'icon': '💡',
        'message': 'Astuce : Avant chaque achat, demandez-vous "En ai-je vraiment besoin ?"'
    },
    {
        'icon': '📊',
        'message': 'Le saviez-vous ? Suivre ses dépenses régulièrement permet d\'économiser jusqu\'à 20% par mois !'
    },
    {
        'icon': '🎯',
        'message': 'Conseil : Fixez-vous un budget mensuel pour cette catégorie et respectez-le !'
    },
    {
        'icon': '💰',
        'message': 'Dépense enregistrée ! Pensez à mettre de côté 10% de vos revenus chaque mois.'
    },
    {
        'icon': '🌟',
        'message': 'Bien joué ! Continuer à suivre vos dépenses, c\'est déjà un grand pas vers la liberté financière.'
    },
    {
        'icon': '📝',
        'message': 'Astuce : Gardez toujours vos reçus pour mieux analyser vos dépenses en fin de mois.'
    },
    {
        'icon': '⏰',
        'message': 'Conseil : Attendez 24h avant tout achat impulsif de plus de 10 000 FCFA.'
    },
    {
        'icon': '🔍',
        'message': 'Le saviez-vous ? Comparer les prix peut vous faire économiser jusqu\'à 30% sur vos achats.'
    },
    {
        'icon': '📱',
        'message': 'Bravo ! Suivre ses dépenses quotidiennement est la clé d\'une bonne gestion financière.'
    },
    {
        'icon': '💪',
        'message': 'Continuez ainsi ! Chaque dépense enregistrée vous rapproche de vos objectifs financiers.'
    },
]

# Messages pour les grosses dépenses (> 50000 FCFA)
BIG_EXPENSE_MESSAGES = [
    {
        'icon': '⚠️',
        'message': 'Grosse dépense ! Assurez-vous que c\'était prévu dans votre budget.'
    },
    {
        'icon': '🤔',
        'message': 'C\'est une dépense importante. Avez-vous comparé les prix avant d\'acheter ?'
    },
    {
        'icon': '💭',
        'message': 'Conseil : Pour les grosses dépenses, pensez toujours à mettre de l\'argent de côté en premier.'
    },
]

# Messages pour l'épargne/objectifs
SAVINGS_MESSAGES = [
    {
        'icon': '🎉',
        'message': 'Bravo ! Chaque contribution compte, continuez sur cette lancée !'
    },
    {
        'icon': '🚀',
        'message': 'Excellent ! Vous êtes un pas de plus vers votre objectif !'
    },
    {
        'icon': '💎',
        'message': 'Félicitations ! L\'épargne régulière est le secret des grandes réussites financières.'
    },
    {
        'icon': '🌱',
        'message': 'Bien joué ! Votre argent travaille pour vous maintenant.'
    },
    {
        'icon': '⭐',
        'message': 'Superbe ! Rappelez-vous : épargner petit à petit, c\'est construire un grand avenir.'
    },
    {
        'icon': '🎯',
        'message': 'Parfait ! Continuez à nourrir vos objectifs avec régularité.'
    },
    {
        'icon': '💪',
        'message': 'Vous êtes sur la bonne voie ! La discipline d\'aujourd\'hui est la liberté de demain.'
    },
    {
        'icon': '🏆',
        'message': 'Magnifique ! Chaque montant épargné vous rapproche de vos rêves.'
    },
]

# Messages pour les transactions du portefeuille (ajout)
WALLET_INCOME_MESSAGES = [
    {
        'icon': '💰',
        'message': 'Entrée d\'argent ! N\'oubliez pas la règle des 50/30/20 : 50% besoins, 30% envies, 20% épargne.'
    },
    {
        'icon': '📈',
        'message': 'Bien reçu ! Pensez à allouer une partie à vos objectifs d\'épargne.'
    },
    {
        'icon': '🎯',
        'message': 'Excellent ! C\'est le moment idéal pour alimenter vos objectifs financiers.'
    },
    {
        'icon': '💡',
        'message': 'Astuce : Mettez de côté au moins 10% avant de dépenser le reste.'
    },
    {
        'icon': '🌟',
        'message': 'Revenu enregistré ! Pensez à d\'abord "vous payer vous-même" en épargnant.'
    },
]

# Conseils généraux
GENERAL_TIPS = [
    {
        'icon': '📚',
        'message': 'Astuce du jour : Lisez un livre ou article sur les finances personnelles ce mois-ci !'
    },
    {
        'icon': '🎓',
        'message': 'Le saviez-vous ? La règle d\'or : dépenser moins que ce qu\'on gagne.'
    },
    {
        'icon': '🔐',
        'message': 'Conseil : Créez toujours un fonds d\'urgence équivalent à 3-6 mois de dépenses.'
    },
    {
        'icon': '🌍',
        'message': 'Pensée du jour : La richesse n\'est pas ce qu\'on gagne, mais ce qu\'on garde.'
    },
]


def get_expense_message(amount):
    """Retourne un message aléatoire pour une dépense"""
    if amount > 50000:
        return random.choice(BIG_EXPENSE_MESSAGES)
    return random.choice(EXPENSE_MESSAGES)


def get_savings_message():
    """Retourne un message aléatoire pour l'épargne"""
    return random.choice(SAVINGS_MESSAGES)


def get_wallet_income_message():
    """Retourne un message aléatoire pour un ajout au portefeuille"""
    return random.choice(WALLET_INCOME_MESSAGES)


def get_general_tip():
    """Retourne un conseil général aléatoire"""
    return random.choice(GENERAL_TIPS)
