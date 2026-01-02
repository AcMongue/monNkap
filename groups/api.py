from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


@login_required
def search_users_api(request):
    """
    API pour rechercher des utilisateurs par nom d'utilisateur.
    Retourne une liste d'utilisateurs correspondant à la recherche.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    # Rechercher les utilisateurs dont le username contient la requête
    users = User.objects.filter(
        username__icontains=query
    ).exclude(
        id=request.user.id  # Exclure l'utilisateur actuel
    ).values('username', 'first_name', 'last_name')[:10]
    
    return JsonResponse(list(users), safe=False)
