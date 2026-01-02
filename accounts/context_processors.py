def theme_preference(request):
    """
    Context processor pour rendre la préférence de thème disponible dans tous les templates.
    """
    if request.user.is_authenticated:
        try:
            return {
                'user_theme': request.user.profile.theme_preference
            }
        except:
            return {'user_theme': 'auto'}
    return {'user_theme': 'auto'}
