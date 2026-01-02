from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import datetime
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm


@login_required
def expense_list_view(request):
    """
    Vue listant toutes les dépenses de l'utilisateur avec filtres.
    """
    expenses = Expense.objects.filter(user=request.user).select_related('category')
    
    # Filtrage par mois si fourni
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month and year:
        expenses = expenses.filter(date__month=month, date__year=year)
    
    # Filtrage par catégorie si fourni
    category_id = request.GET.get('category')
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    
    # Calcul du total des dépenses affichées
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Liste des catégories pour le filtre
    categories = Category.objects.all()
    
    context = {
        'expenses': expenses,
        'total': total,
        'categories': categories,
        'selected_month': month,
        'selected_year': year,
        'selected_category': category_id
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
            return redirect('expenses:list')
        else:
            messages.error(request, 'Erreur lors de l\'ajout de la dépense.')
    else:
        form = ExpenseForm()
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Ajouter une dépense'
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
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Modifier la dépense',
        'expense': expense
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
    ).order_by('-month')[:6]
    
    context = {
        'total_expenses': total_expenses,
        'expenses_by_category': expenses_by_category,
        'expenses_by_month': expenses_by_month
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
