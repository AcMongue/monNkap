from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Goal, Contribution
from .forms import GoalForm, ContributionForm
from accounts.emails import send_goal_achieved_email


@login_required
def goal_list_view(request):
    """
    Vue listant tous les objectifs financiers de l'utilisateur.
    """
    goals = Goal.objects.filter(user=request.user)
    
    # Filtrage par statut si fourni
    status = request.GET.get('status')
    if status:
        goals = goals.filter(status=status)
    
    # Statistiques globales
    total_target = goals.filter(status='active').aggregate(total=Sum('target_amount'))['total'] or 0
    total_saved = goals.filter(status='active').aggregate(total=Sum('current_amount'))['total'] or 0
    
    context = {
        'goals': goals,
        'total_target': total_target,
        'total_saved': total_saved,
        'selected_status': status
    }
    
    return render(request, 'goals/goal_list.html', context)


@login_required
def goal_detail_view(request, pk):
    """
    Vue détaillée d'un objectif avec historique des contributions.
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    contributions = goal.contributions.all()
    
    context = {
        'goal': goal,
        'contributions': contributions
    }
    
    return render(request, 'goals/goal_detail.html', context)


@login_required
def goal_create_view(request):
    """
    Vue de création d'un nouvel objectif financier.
    """
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Objectif créé avec succès!')
            return redirect('goals:list')
        else:
            messages.error(request, 'Erreur lors de la création de l\'objectif.')
    else:
        form = GoalForm()
    
    return render(request, 'goals/goal_form.html', {
        'form': form,
        'title': 'Créer un objectif'
    })


@login_required
def goal_update_view(request, pk):
    """
    Vue de modification d'un objectif existant.
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Objectif modifié avec succès!')
            return redirect('goals:detail', pk=pk)
        else:
            messages.error(request, 'Erreur lors de la modification de l\'objectif.')
    else:
        form = GoalForm(instance=goal)
    
    return render(request, 'goals/goal_form.html', {
        'form': form,
        'title': 'Modifier l\'objectif',
        'goal': goal
    })


@login_required
def goal_delete_view(request, pk):
    """
    Vue de suppression d'un objectif.
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Objectif supprimé avec succès!')
        return redirect('goals:list')
    
    return render(request, 'goals/goal_confirm_delete.html', {
        'goal': goal
    })


@login_required
def contribution_create_view(request, goal_pk):
    """
    Vue d'ajout d'une contribution à un objectif.
    """
    goal = get_object_or_404(Goal, pk=goal_pk, user=request.user)
    
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.goal = goal
            contribution.save()
            
            # Vérifier si l'objectif est atteint et envoyer un email
            if goal.get_progress_percentage() >= 100 and goal.status == 'active':
                goal.status = 'completed'
                goal.save()
                try:
                    send_goal_achieved_email(request.user, goal)
                except Exception as e:
                    print(f"Erreur envoi email objectif atteint: {e}")
                messages.success(request, f'🎉 Félicitations ! Objectif "{goal.title}" atteint !')
            else:
                messages.success(request, f'Contribution de {contribution.amount} FCFA ajoutée!')
            
            return redirect('goals:detail', pk=goal_pk)
        else:
            messages.error(request, 'Erreur lors de l\'ajout de la contribution.')
    else:
        form = ContributionForm()
    
    return render(request, 'goals/contribution_form.html', {
        'form': form,
        'goal': goal
    })
