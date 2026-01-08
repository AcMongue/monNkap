from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from decimal import Decimal
from .models import Group, Membership, GroupContribution, GroupExpense, GroupExpenseSplit, GroupSavingsGoal, GroupSavingsContribution
from .forms import GroupForm, MembershipForm, GroupContributionForm, GroupExpenseForm, GroupSavingsGoalForm, GroupSavingsContributionForm


@login_required
def group_list_view(request):
    """
    Vue listant tous les groupes dont l'utilisateur est membre.
    """
    # Groupes dont l'utilisateur est membre
    user_groups = Group.objects.filter(members=request.user)
    
    # Filtrage par statut si fourni
    status = request.GET.get('status')
    if status:
        user_groups = user_groups.filter(status=status)
    
    context = {
        'groups': user_groups,
        'selected_status': status
    }
    
    return render(request, 'groups/group_list.html', context)


@login_required
def group_help_view(request):
    """
    Vue affichant la page d'aide explicative sur les fonctionnalités des groupes.
    """
    return render(request, 'groups/group_help.html')


@login_required
def group_detail_view(request, pk):
    """
    Vue détaillée d'un groupe avec membres et contributions.
    """
    group = get_object_or_404(Group, pk=pk)
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    # Récupérer les membres et contributions
    members = Membership.objects.filter(group=group).select_related('user')
    contributions = GroupContribution.objects.filter(group=group).select_related('user')
    
    # Statistiques par membre
    member_stats = GroupContribution.objects.filter(
        group=group
    ).values('user__username').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'group': group,
        'membership': membership,
        'members': members,
        'contributions': contributions,
        'member_stats': member_stats
    }
    
    return render(request, 'groups/group_detail.html', context)


@login_required
def group_create_view(request):
    """
    Vue de création d'un nouveau groupe.
    Le créateur devient automatiquement administrateur.
    """
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            
            # Ajouter le créateur comme administrateur du groupe
            Membership.objects.create(
                user=request.user,
                group=group,
                role='admin'
            )
            
            messages.success(request, 'Groupe créé avec succès!')
            return redirect('groups:detail', pk=group.pk)
        else:
            messages.error(request, 'Erreur lors de la création du groupe.')
    else:
        form = GroupForm()
    
    return render(request, 'groups/group_form.html', {
        'form': form,
        'title': 'Créer un groupe'
    })


@login_required
def group_update_view(request, pk):
    """
    Vue de modification d'un groupe (réservé aux admins).
    """
    group = get_object_or_404(Group, pk=pk)
    
    # Vérifier que l'utilisateur est admin du groupe
    membership = Membership.objects.filter(user=request.user, group=group, role='admin').first()
    if not membership:
        messages.error(request, 'Seuls les administrateurs peuvent modifier ce groupe.')
        return redirect('groups:detail', pk=pk)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Groupe modifié avec succès!')
            return redirect('groups:detail', pk=pk)
        else:
            messages.error(request, 'Erreur lors de la modification du groupe.')
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'groups/group_form.html', {
        'form': form,
        'title': 'Modifier le groupe',
        'group': group
    })


@login_required
def group_delete_view(request, pk):
    """
    Vue de suppression d'un groupe (réservé au créateur).
    """
    group = get_object_or_404(Group, pk=pk, creator=request.user)
    
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Groupe supprimé avec succès!')
        return redirect('groups:list')
    
    return render(request, 'groups/group_confirm_delete.html', {
        'group': group
    })


@login_required
def member_add_view(request, group_pk):
    """
    Vue d'ajout d'un membre à un groupe (réservé aux admins).
    """
    group = get_object_or_404(Group, pk=group_pk)
    
    # Vérifier que l'utilisateur est admin du groupe
    membership = Membership.objects.filter(user=request.user, group=group, role='admin').first()
    if not membership:
        messages.error(request, 'Seuls les administrateurs peuvent ajouter des membres.')
        return redirect('groups:detail', pk=group_pk)
    
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            # Le clean_username retourne directement l'objet User
            user = form.cleaned_data['username']
            role = form.cleaned_data['role']
            
            # Vérifier que l'utilisateur n'est pas déjà membre
            if Membership.objects.filter(user=user, group=group).exists():
                messages.warning(request, f'{user.username} est déjà membre du groupe.')
            else:
                Membership.objects.create(user=user, group=group, role=role)
                messages.success(request, f'{user.username} a été ajouté au groupe avec le rôle {role}.')
                return redirect('groups:detail', pk=group_pk)
    else:
        form = MembershipForm()
    
    return render(request, 'groups/member_form.html', {
        'form': form,
        'group': group
    })


@login_required
def member_remove_view(request, group_pk, member_pk):
    """
    Vue de suppression d'un membre d'un groupe (réservé aux admins).
    Un admin ne peut pas se retirer lui-même.
    Le créateur du groupe ne peut pas être retiré.
    """
    group = get_object_or_404(Group, pk=group_pk)
    
    # Vérifier que l'utilisateur est admin du groupe
    admin_membership = Membership.objects.filter(user=request.user, group=group, role='admin').first()
    if not admin_membership:
        messages.error(request, 'Seuls les administrateurs peuvent retirer des membres.')
        return redirect('groups:detail', pk=group_pk)
    
    # Récupérer le membre à retirer
    member_to_remove = get_object_or_404(Membership, pk=member_pk, group=group)
    
    # Vérifications de sécurité
    if member_to_remove.user == group.creator:
        messages.error(request, 'Le créateur du groupe ne peut pas être retiré.')
        return redirect('groups:detail', pk=group_pk)
    
    if member_to_remove.user == request.user:
        messages.error(request, 'Vous ne pouvez pas vous retirer vous-même. Utilisez "Quitter le groupe".')
        return redirect('groups:detail', pk=group_pk)
    
    if request.method == 'POST':
        username = member_to_remove.user.username
        member_to_remove.delete()
        messages.success(request, f'{username} a été retiré du groupe.')
        return redirect('groups:detail', pk=group_pk)
    
    return render(request, 'groups/member_confirm_remove.html', {
        'group': group,
        'member': member_to_remove
    })


@login_required
def contribution_create_view(request, group_pk):
    """
    Vue d'ajout d'une contribution à un groupe.
    """
    group = get_object_or_404(Group, pk=group_pk)
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous devez être membre du groupe pour contribuer.')
        return redirect('groups:list')
    
    if request.method == 'POST':
        form = GroupContributionForm(request.POST)
        if form.is_valid():
            # Sauvegarder le montant avant pour débug
            old_amount = group.current_amount
            
            contribution = form.save(commit=False)
            contribution.group = group
            contribution.user = request.user
            contribution.save()  # La méthode save() du modèle met à jour le groupe automatiquement
            
            # Recharger le groupe depuis la base pour vérifier
            group.refresh_from_db()
            
            # Message de succès avec détail
            messages.success(
                request, 
                f'Contribution de {contribution.amount:,.0f} FCFA ajoutée ! '
                f'Montant collecté : {old_amount:,.0f} FCFA → {group.current_amount:,.0f} FCFA'
            )
            return redirect('groups:detail', pk=group_pk)
        else:
            messages.error(request, 'Erreur lors de l\'ajout de la contribution.')
    else:
        form = GroupContributionForm()
    
    return render(request, 'groups/contribution_form.html', {
        'form': form,
        'group': group
    })


@login_required
def join_group_view(request, invite_code=None):
    """
    Vue pour rejoindre un groupe via un code d'invitation.
    """
    if request.method == 'POST':
        code = request.POST.get('invite_code', '').strip().upper()
        
        if not code:
            messages.error(request, 'Veuillez entrer un code d\'invitation.')
            return redirect('groups:join')
        
        # Rechercher le groupe avec ce code
        try:
            group = Group.objects.get(invite_code=code)
        except Group.DoesNotExist:
            messages.error(request, 'Code d\'invitation invalide.')
            return redirect('groups:join')
        
        # Vérifier si l'utilisateur est déjà membre
        if Membership.objects.filter(user=request.user, group=group).exists():
            messages.info(request, 'Vous êtes déjà membre de ce groupe.')
            return redirect('groups:detail', pk=group.pk)
        
        # Ajouter l'utilisateur au groupe
        Membership.objects.create(
            user=request.user,
            group=group,
            role='member'
        )
        
        messages.success(request, f'Vous avez rejoint le groupe "{group.name}" avec succès!')
        return redirect('groups:detail', pk=group.pk)
    
    # Si un code est fourni dans l'URL, pré-remplir le formulaire
    context = {'invite_code': invite_code if invite_code else ''}
    return render(request, 'groups/join_group.html', context)


@login_required
def group_invite_view(request, pk):
    """
    Vue pour afficher le code d'invitation et le lien d'un groupe.
    """
    group = get_object_or_404(Group, pk=pk)
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    # Générer l'URL complète d'invitation
    invite_url = request.build_absolute_uri(f'/groups/join/{group.invite_code}/')
    
    context = {
        'group': group,
        'membership': membership,
        'invite_url': invite_url
    }
    
    return render(request, 'groups/group_invite.html', context)


@login_required
def group_expense_list_view(request, group_pk):
    """
    Vue listant toutes les dépenses d'un groupe.
    """
    group = get_object_or_404(Group, pk=group_pk)
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    # Récupérer toutes les dépenses du groupe
    expenses = GroupExpense.objects.filter(group=group).select_related('paid_by', 'category').order_by('-date')
    
    # Statistiques
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    my_paid = expenses.filter(paid_by=request.user).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Mon solde (ce que j'ai payé - ma part)
    member_count = group.members.count()
    my_share = total_expenses / member_count if member_count > 0 else Decimal('0.00')
    my_balance = my_paid - my_share
    
    context = {
        'group': group,
        'membership': membership,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'my_paid': my_paid,
        'my_share': my_share,
        'my_balance': my_balance,
    }
    
    return render(request, 'groups/expense_list.html', context)


@login_required
def group_expense_create_view(request, group_pk):
    """
    Vue de création d'une dépense de groupe.
    """
    group = get_object_or_404(Group, pk=group_pk)
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    if request.method == 'POST':
        form = GroupExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.paid_by = request.user
            expense.save()
            
            # Créer les splits pour chaque membre
            members = group.members.all()
            split_amount = expense.amount / members.count()
            
            for member in members:
                GroupExpenseSplit.objects.create(
                    expense=expense,
                    user=member,
                    amount=split_amount,
                    is_paid=(member == request.user)  # La personne qui paie est déjà "payée"
                )
            
            messages.success(request, f'Dépense de {expense.amount} FCFA ajoutée et répartie entre {members.count()} membres.')
            return redirect('groups:expense_list', group_pk=group_pk)
    else:
        form = GroupExpenseForm()
    
    return render(request, 'groups/expense_form.html', {
        'form': form,
        'group': group
    })


@login_required
def group_expense_detail_view(request, pk):
    """
    Vue détaillée d'une dépense de groupe avec répartition.
    """
    expense = get_object_or_404(GroupExpense, pk=pk)
    group = expense.group
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    # Récupérer tous les splits
    splits = expense.splits.select_related('user').order_by('user__username')
    
    context = {
        'expense': expense,
        'group': group,
        'membership': membership,
        'splits': splits,
    }
    
    return render(request, 'groups/expense_detail.html', context)


@login_required
def mark_split_paid_view(request, split_pk):
    """
    Marquer un split comme payé.
    """
    split = get_object_or_404(GroupExpenseSplit, pk=split_pk)
    expense = split.expense
    group = expense.group
    
    # Vérifier que l'utilisateur est admin du groupe ou le membre concerné
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership or (membership.role != 'admin' and split.user != request.user):
        messages.error(request, 'Vous n\'avez pas la permission de faire cela.')
        return redirect('groups:expense_detail', pk=expense.pk)
    
    if not split.is_paid:
        split.is_paid = True
        from django.utils import timezone
        split.paid_at = timezone.now()
        split.save()
        messages.success(request, f'{split.user.username} a marqué sa part comme payée.')
    
    return redirect('groups:expense_detail', pk=expense.pk)


# ============= VUES D'ÉPARGNE DE GROUPE =============

@login_required
def group_savings_list_view(request, group_pk):
    """
    Liste des objectifs d'épargne d'un groupe.
    """
    group = get_object_or_404(Group, pk=group_pk)
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    # Récupérer les objectifs d'épargne
    savings_goals = GroupSavingsGoal.objects.filter(group=group)
    
    # Filtrage par statut
    status = request.GET.get('status')
    if status:
        savings_goals = savings_goals.filter(status=status)
    
    # Statistiques globales
    active_goals = savings_goals.filter(status='active')
    total_target = active_goals.aggregate(total=Sum('target_amount'))['total'] or Decimal('0.00')
    total_saved = active_goals.aggregate(total=Sum('current_amount'))['total'] or Decimal('0.00')
    
    context = {
        'group': group,
        'membership': membership,
        'savings_goals': savings_goals,
        'total_target': total_target,
        'total_saved': total_saved,
        'selected_status': status
    }
    
    return render(request, 'groups/savings_list.html', context)


@login_required
def group_savings_create_view(request, group_pk):
    """
    Créer un objectif d'épargne pour un groupe.
    """
    group = get_object_or_404(Group, pk=group_pk)
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    if request.method == 'POST':
        form = GroupSavingsGoalForm(request.POST)
        if form.is_valid():
            savings_goal = form.save(commit=False)
            savings_goal.group = group
            savings_goal.created_by = request.user
            savings_goal.save()
            
            messages.success(request, 'Objectif d\'épargne créé avec succès!')
            return redirect('groups:savings_detail', pk=savings_goal.pk)
        else:
            messages.error(request, 'Erreur lors de la création de l\'objectif.')
    else:
        form = GroupSavingsGoalForm()
    
    context = {
        'form': form,
        'group': group,
        'membership': membership,
        'title': 'Nouvel objectif d\'épargne'
    }
    
    return render(request, 'groups/savings_form.html', context)


@login_required
def group_savings_detail_view(request, pk):
    """
    Vue détaillée d'un objectif d'épargne de groupe.
    """
    savings_goal = get_object_or_404(GroupSavingsGoal, pk=pk)
    group = savings_goal.group
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    # Récupérer les contributions
    contributions = GroupSavingsContribution.objects.filter(
        savings_goal=savings_goal
    ).select_related('user').order_by('-date', '-created_at')
    
    # Statistiques par membre
    member_stats = GroupSavingsContribution.objects.filter(
        savings_goal=savings_goal
    ).values('user__username').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'savings_goal': savings_goal,
        'group': group,
        'membership': membership,
        'contributions': contributions,
        'member_stats': member_stats
    }
    
    return render(request, 'groups/savings_detail.html', context)


@login_required
def group_savings_contribute_view(request, pk):
    """
    Ajouter une contribution à un objectif d'épargne de groupe.
    """
    savings_goal = get_object_or_404(GroupSavingsGoal, pk=pk)
    group = savings_goal.group
    
    # Vérifier que l'utilisateur est membre du groupe
    membership = Membership.objects.filter(user=request.user, group=group).first()
    if not membership:
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('groups:list')
    
    # Vérifier que l'objectif est actif
    if savings_goal.status != 'active':
        messages.error(request, 'Cet objectif d\'épargne n\'est pas actif.')
        return redirect('groups:savings_detail', pk=savings_goal.pk)
    
    if request.method == 'POST':
        form = GroupSavingsContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.savings_goal = savings_goal
            contribution.user = request.user
            contribution.save()
            
            messages.success(request, f'Contribution de {contribution.amount} FCFA ajoutée avec succès!')
            return redirect('groups:savings_detail', pk=savings_goal.pk)
        else:
            messages.error(request, 'Erreur lors de l\'ajout de la contribution.')
    else:
        form = GroupSavingsContributionForm()
    
    context = {
        'form': form,
        'savings_goal': savings_goal,
        'group': group,
        'membership': membership,
        'title': f'Contribuer à {savings_goal.title}'
    }
    
    return render(request, 'groups/savings_contribute.html', context)


@login_required
def group_savings_edit_view(request, pk):
    """
    Modifier un objectif d'épargne de groupe.
    """
    savings_goal = get_object_or_404(GroupSavingsGoal, pk=pk)
    group = savings_goal.group
    
    # Vérifier que l'utilisateur est admin du groupe
    membership = Membership.objects.filter(user=request.user, group=group, role='admin').first()
    if not membership:
        messages.error(request, 'Seuls les administrateurs peuvent modifier les objectifs d\'épargne.')
        return redirect('groups:savings_detail', pk=savings_goal.pk)
    
    if request.method == 'POST':
        form = GroupSavingsGoalForm(request.POST, instance=savings_goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Objectif d\'épargne mis à jour avec succès!')
            return redirect('groups:savings_detail', pk=savings_goal.pk)
        else:
            messages.error(request, 'Erreur lors de la modification.')
    else:
        form = GroupSavingsGoalForm(instance=savings_goal)
    
    context = {
        'form': form,
        'savings_goal': savings_goal,
        'group': group,
        'membership': membership,
        'title': f'Modifier {savings_goal.title}'
    }
    
    return render(request, 'groups/savings_form.html', context)


@login_required
def group_savings_delete_view(request, pk):
    """
    Supprimer un objectif d'épargne de groupe.
    """
    savings_goal = get_object_or_404(GroupSavingsGoal, pk=pk)
    group = savings_goal.group
    
    # Vérifier que l'utilisateur est admin du groupe
    membership = Membership.objects.filter(user=request.user, group=group, role='admin').first()
    if not membership:
        messages.error(request, 'Seuls les administrateurs peuvent supprimer les objectifs d\'épargne.')
        return redirect('groups:savings_detail', pk=savings_goal.pk)
    
    if request.method == 'POST':
        group_pk = group.pk
        savings_goal.delete()
        messages.success(request, 'Objectif d\'épargne supprimé avec succès.')
        return redirect('groups:savings_list', group_pk=group_pk)
    
    context = {
        'savings_goal': savings_goal,
        'group': group,
        'membership': membership
    }
    
    return render(request, 'groups/savings_confirm_delete.html', context)
