from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from datetime import datetime
import csv
import json
from .models import Expense, Category, Budget
from .forms import ExpenseForm, CategoryForm
from .budget_forms import BudgetForm
from accounts.motivation_messages import get_expense_message


@login_required
def expense_list_view(request):
    """
    Vue listant toutes les dépenses de l'utilisateur avec filtres et pagination.
    """
    expenses = Expense.objects.filter(user=request.user).select_related('category')
    
    # Recherche par description
    search_query = request.GET.get('search', '').strip()
    if search_query:
        expenses = expenses.filter(description__icontains=search_query)
    
    # Filtrage par mois si fourni
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month and year:
        expenses = expenses.filter(date__month=month, date__year=year)
    
    # Filtrage par catégorie si fourni
    category_id = request.GET.get('category')
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    
    # Filtrage par montant
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    
    if min_amount:
        try:
            expenses = expenses.filter(amount__gte=float(min_amount))
        except ValueError:
            pass
    
    if max_amount:
        try:
            expenses = expenses.filter(amount__lte=float(max_amount))
        except ValueError:
            pass
    
    # Calcul du total des dépenses affichées
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Liste des catégories pour le filtre
    categories = Category.objects.all()
    
    # Pagination: 20 items par page
    paginator = Paginator(expenses.order_by('-date', '-created_at'), 20)
    page = request.GET.get('page', 1)
    
    try:
        expenses_page = paginator.page(page)
    except PageNotAnInteger:
        expenses_page = paginator.page(1)
    except EmptyPage:
        expenses_page = paginator.page(paginator.num_pages)
    
    context = {
        'expenses': expenses_page,
        'total': total,
        'categories': categories,
        'selected_month': month,
        'selected_year': year,
        'selected_category': category_id,
        'search_query': search_query,
        'min_amount': min_amount,
        'max_amount': max_amount,
    }
    
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_create_view(request):
    """
    Vue de création d'une nouvelle dépense.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Dépense ajoutée avec succès!')
            
            # Message de motivation
            motivation = get_expense_message(expense.amount)
            messages.info(request, f"{motivation['icon']} {motivation['message']}")
            
            return redirect('expenses:list')
        else:
            messages.error(request, 'Erreur lors de l\'ajout de la dépense.')
    else:
        form = ExpenseForm()
    
    # Récupérer les catégories existantes pour les suggestions
    existing_categories = Category.objects.all().order_by('name')
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Ajouter une dépense',
        'existing_categories': existing_categories
    })


@login_required
def expense_update_view(request, pk):
    """
    Vue de modification d'une dépense existante.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dépense modifiée avec succès!')
            return redirect('expenses:list')
        else:
            messages.error(request, 'Erreur lors de la modification de la dépense.')
    else:
        form = ExpenseForm(instance=expense)
    
    # Récupérer les catégories existantes pour les suggestions
    existing_categories = Category.objects.all().order_by('name')
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Modifier la dépense',
        'expense': expense,
        'existing_categories': existing_categories
    })


@login_required
def expense_delete_view(request, pk):
    """
    Vue de suppression d'une dépense.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Dépense supprimée avec succès!')
        return redirect('expenses:list')
    
    return render(request, 'expenses/expense_confirm_delete.html', {
        'expense': expense
    })


@login_required
def expense_statistics_view(request):
    """
    Vue des statistiques de dépenses par catégorie et par mois.
    """
    # Dépenses totales de l'utilisateur
    total_expenses = Expense.objects.filter(user=request.user).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Dépenses par catégorie
    expenses_by_category = Expense.objects.filter(user=request.user).values(
        'category__name', 'category__color'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Dépenses par mois (6 derniers mois)
    expenses_by_month = Expense.objects.filter(
        user=request.user
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')[:6]  # Changé -month en month pour l'ordre chronologique
    
    # Préparer les données pour Chart.js
    category_labels = [cat['category__name'] or 'Non catégorisé' for cat in expenses_by_category]
    category_data = [float(cat['total']) for cat in expenses_by_category]
    category_colors = [cat['category__color'] or '#6c757d' for cat in expenses_by_category]
    
    month_labels = [item['month'].strftime('%B %Y') for item in expenses_by_month]
    month_data = [float(item['total']) for item in expenses_by_month]
    
    context = {
        'total_expenses': total_expenses,
        'expenses_by_category': expenses_by_category,
        'expenses_by_month': expenses_by_month,
        # Données JSON pour Chart.js
        'category_labels_json': json.dumps(category_labels),
        'category_data_json': json.dumps(category_data),
        'category_colors_json': json.dumps(category_colors),
        'month_labels_json': json.dumps(month_labels),
        'month_data_json': json.dumps(month_data),
    }
    
    return render(request, 'expenses/expense_statistics.html', context)


@login_required
def category_list_view(request):
    """
    Vue listant toutes les catégories disponibles.
    """
    categories = Category.objects.all()
    return render(request, 'expenses/category_list.html', {
        'categories': categories
    })


@login_required
def export_expenses_csv(request):
    """
    Exporte toutes les dépenses de l'utilisateur en CSV avec statistiques.
    """
    # Créer la réponse HTTP avec le type CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="depenses_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    response.write('\ufeff')  # BOM UTF-8 pour Excel
    
    # Créer le writer CSV
    writer = csv.writer(response, delimiter=';')
    
    # Récupérer les dépenses avec les mêmes filtres que la liste
    expenses = Expense.objects.filter(user=request.user).select_related('category')
    
    # Appliquer les mêmes filtres que dans expense_list_view
    month = request.GET.get('month')
    year = request.GET.get('year')
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    
    # Construire le titre avec les filtres actifs
    filter_info = []
    if month and year:
        expenses = expenses.filter(date__month=month, date__year=year)
        month_name = datetime(int(year), int(month), 1).strftime('%B %Y')
        filter_info.append(f"Mois: {month_name}")
    if category_id:
        expenses = expenses.filter(category_id=category_id)
        category = Category.objects.filter(id=category_id).first()
        if category:
            filter_info.append(f"Catégorie: {category.name}")
    if search_query:
        expenses = expenses.filter(description__icontains=search_query)
        filter_info.append(f"Recherche: {search_query}")
    if min_amount:
        expenses = expenses.filter(amount__gte=float(min_amount))
        filter_info.append(f"Montant min: {min_amount} FCFA")
    if max_amount:
        expenses = expenses.filter(amount__lte=float(max_amount))
        filter_info.append(f"Montant max: {max_amount} FCFA")
    
    # Calculer les statistiques
    expenses_list = expenses.order_by('-date')
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    count = expenses.count()
    average = total / count if count > 0 else 0
    
    # En-tête du document
    writer.writerow(['EXPORT DES DÉPENSES - MonNkap'])
    writer.writerow([f'Généré le: {datetime.now().strftime("%d/%m/%Y à %H:%M")}'])
    writer.writerow([f'Utilisateur: {request.user.get_full_name() or request.user.username}'])
    if filter_info:
        writer.writerow([f'Filtres: {" | ".join(filter_info)}'])
    writer.writerow([])  # Ligne vide
    
    # Statistiques globales
    writer.writerow(['STATISTIQUES'])
    writer.writerow(['Nombre de dépenses', count])
    writer.writerow(['Total', f'{total:.2f}', 'FCFA'])
    writer.writerow(['Moyenne par dépense', f'{average:.2f}', 'FCFA'])
    writer.writerow([])  # Ligne vide
    
    # Statistiques par catégorie
    expenses_by_category = expenses.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    if expenses_by_category:
        writer.writerow(['RÉPARTITION PAR CATÉGORIE'])
        writer.writerow(['Catégorie', 'Nombre', 'Total (FCFA)', 'Pourcentage'])
        for cat in expenses_by_category:
            cat_name = cat['category__name'] or 'Non catégorisé'
            cat_total = cat['total']
            cat_count = cat['count']
            percentage = (cat_total / total * 100) if total > 0 else 0
            writer.writerow([cat_name, cat_count, f'{cat_total:.2f}', f'{percentage:.1f}%'])
        writer.writerow([])  # Ligne vide
    
    # Données détaillées
    writer.writerow(['DÉTAIL DES DÉPENSES'])
    writer.writerow(['N°', 'Date', 'Description', 'Catégorie', 'Montant (FCFA)', 'Notes', 'Créé le'])
    
    # Écrire les données
    for idx, expense in enumerate(expenses_list, 1):
        writer.writerow([
            idx,
            expense.date.strftime('%d/%m/%Y'),
            expense.description,
            expense.get_category_name,
            f'{expense.amount:.2f}',
            expense.notes or '',
            expense.created_at.strftime('%d/%m/%Y %H:%M')
        ])
    
    # Ligne de total
    writer.writerow([])
    writer.writerow(['', '', '', 'TOTAL', f'{total:.2f}', '', ''])
    
    return response


# ==================== VUES POUR LES BUDGETS ====================

@login_required
def budget_list_view(request):
    """
    Liste tous les budgets de l'utilisateur.
    """
    today = datetime.now()
    current_month = request.GET.get('month', today.month)
    current_year = request.GET.get('year', today.year)
    
    try:
        current_month = int(current_month)
        current_year = int(current_year)
    except (ValueError, TypeError):
        current_month = today.month
        current_year = today.year
    
    # Budgets du mois sélectionné
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    ).select_related('category').order_by('category__name')
    
    # Calculer les statistiques pour chaque budget
    budget_stats = []
    total_budgeted = 0
    total_spent = 0
    
    for budget in budgets:
        spent = budget.get_spent_amount()
        remaining = budget.get_remaining_amount()
        progress = budget.get_progress_percentage()
        status = budget.get_status()
        
        budget_stats.append({
            'budget': budget,
            'spent': spent,
            'remaining': remaining,
            'progress': progress,
            'status': status,
            'status_color': budget.get_status_color()
        })
        
        total_budgeted += float(budget.amount)
        total_spent += float(spent)
    
    # Générer les options de mois/années
    months = [
        {'value': i, 'name': datetime(2000, i, 1).strftime('%B')}
        for i in range(1, 13)
    ]
    years = list(range(today.year - 2, today.year + 2))
    
    context = {
        'budget_stats': budget_stats,
        'current_month': current_month,
        'current_year': current_year,
        'months': months,
        'years': years,
        'total_budgeted': total_budgeted,
        'total_spent': total_spent,
        'has_budgets': budgets.exists()
    }
    
    return render(request, 'expenses/budget_list.html', context)


@login_required
def budget_create_view(request):
    """
    Créer un nouveau budget.
    """
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            
            category_name = budget.category.name if budget.category else "global"
            messages.success(
                request,
                f"✅ Budget {category_name} créé avec succès pour {budget.month}/{budget.year}"
            )
            return redirect('expenses:budget_list')
    else:
        form = BudgetForm(user=request.user)
    
    return render(request, 'expenses/budget_form.html', {
        'form': form,
        'title': 'Créer un budget',
        'button_text': 'Créer'
    })


@login_required
def budget_update_view(request, pk):
    """
    Modifier un budget existant.
    """
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Budget modifié avec succès")
            return redirect('expenses:budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    
    return render(request, 'expenses/budget_form.html', {
        'form': form,
        'budget': budget,
        'title': 'Modifier le budget',
        'button_text': 'Enregistrer'
    })


@login_required
def budget_delete_view(request, pk):
    """
    Supprimer un budget.
    """
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category_name = budget.category.name if budget.category else "global"
        budget.delete()
        messages.success(request, f"🗑️ Budget {category_name} supprimé")
        return redirect('expenses:budget_list')
    
    return render(request, 'expenses/budget_confirm_delete.html', {
        'budget': budget
    })
