from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Max, Min
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from expenses.models import Expense, Category
from goals.models import Goal
from groups.models import Group, GroupContribution


@login_required
def home_view(request):
    """
    Vue principale du tableau de bord.
    Affiche un résumé des dépenses, objectifs et groupes de l'utilisateur.
    """
    # Période actuelle
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # === DÉPENSES ===
    # Dépenses du mois en cours
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year
    )
    
    total_monthly_expenses = monthly_expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Dépenses par catégorie ce mois
    expenses_by_category = monthly_expenses.values(
        'category__name', 'category__color', 'category__icon'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    # Dernières dépenses
    recent_expenses = Expense.objects.filter(
        user=request.user
    ).select_related('category').order_by('-date', '-created_at')[:5]
    
    # === OBJECTIFS PERSONNELS ===
    # Objectifs actifs
    active_goals = Goal.objects.filter(
        user=request.user,
        status='active'
    ).order_by('deadline')[:5]
    
    total_goals_target = active_goals.aggregate(
        total=Sum('target_amount')
    )['total'] or 0
    
    total_goals_saved = active_goals.aggregate(
        total=Sum('current_amount')
    )['total'] or 0
    
    # === GROUPES ===
    # Groupes dont l'utilisateur est membre
    user_groups = Group.objects.filter(
        members=request.user,
        status='active'
    ).order_by('deadline')[:5]
    
    # Contributions de l'utilisateur ce mois
    monthly_contributions = GroupContribution.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year,
        payment_status='paid'
    )
    
    total_monthly_contributions = monthly_contributions.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # === STATISTIQUES GLOBALES ===
    # Nombre total de dépenses
    total_expenses_count = Expense.objects.filter(user=request.user).count()
    
    # Nombre d'objectifs complétés
    completed_goals_count = Goal.objects.filter(
        user=request.user,
        status='completed'
    ).count()
    
    # Nombre de groupes actifs
    active_groups_count = user_groups.count()
    
    context = {
        # Dépenses
        'total_monthly_expenses': total_monthly_expenses,
        'expenses_by_category': expenses_by_category,
        'recent_expenses': recent_expenses,
        'total_expenses_count': total_expenses_count,
        
        # Objectifs
        'active_goals': active_goals,
        'total_goals_target': total_goals_target,
        'total_goals_saved': total_goals_saved,
        'completed_goals_count': completed_goals_count,
        
        # Groupes
        'user_groups': user_groups,
        'total_monthly_contributions': total_monthly_contributions,
        'active_groups_count': active_groups_count,
        
        # Période
        'current_month': current_month,
        'current_year': current_year,
        'today': today,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def statistics_view(request):
    """
    Vue des statistiques détaillées avec analyses avancées.
    Affiche des graphiques et KPIs pour une meilleure compréhension des finances.
    """
    today = timezone.now().date()
    current_year = today.year
    
    # === PÉRIODE D'ANALYSE ===
    twelve_months_ago = today - timedelta(days=365)
    six_months_ago = today - timedelta(days=180)
    
    # === DÉPENSES PAR MOIS (12 derniers mois) ===
    expenses_by_month = Expense.objects.filter(
        user=request.user,
        date__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')
    
    # Préparer les données pour Chart.js
    months_labels = []
    months_data = []
    for item in expenses_by_month:
        months_labels.append(item['month'].strftime('%B %Y'))
        months_data.append(float(item['total']))
    
    # === STATISTIQUES MENSUELLES ===
    if expenses_by_month:
        monthly_amounts = [item['total'] for item in expenses_by_month]
        avg_monthly_expense = sum(monthly_amounts) / len(monthly_amounts)
        max_monthly_expense = max(monthly_amounts)
        min_monthly_expense = min(monthly_amounts)
        
        # Trouver le mois le plus dépensier
        max_expense_month = max(expenses_by_month, key=lambda x: x['total'])
        most_expensive_month = max_expense_month['month'].strftime('%B %Y')
        most_expensive_amount = max_expense_month['total']
    else:
        avg_monthly_expense = 0
        max_monthly_expense = 0
        min_monthly_expense = 0
        most_expensive_month = "N/A"
        most_expensive_amount = 0
    
    # === DÉPENSES PAR CATÉGORIE (année en cours) ===
    expenses_by_category = Expense.objects.filter(
        user=request.user,
        date__year=current_year
    ).values(
        'category__name', 'category__color', 'category__icon'
    ).annotate(
        total=Sum('amount'),
        count=Count('id'),
        avg=Avg('amount')
    ).order_by('-total')
    
    # Pour le graphique en camembert
    category_labels = [item['category__name'] for item in expenses_by_category]
    category_data = [float(item['total']) for item in expenses_by_category]
    category_colors = [item['category__color'] for item in expenses_by_category]
    
    # === ÉVOLUTION HEBDOMADAIRE (8 dernières semaines) ===
    eight_weeks_ago = today - timedelta(weeks=8)
    expenses_by_week = Expense.objects.filter(
        user=request.user,
        date__gte=eight_weeks_ago
    ).annotate(
        week=TruncWeek('date')
    ).values('week').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('week')
    
    week_labels = [f"Semaine {item['week'].isocalendar()[1]}" for item in expenses_by_week]
    week_data = [float(item['total']) for item in expenses_by_week]
    
    # === TOP 5 DÉPENSES ===
    top_expenses = Expense.objects.filter(
        user=request.user,
        date__year=current_year
    ).select_related('category').order_by('-amount')[:5]
    
    # === STATISTIQUES GÉNÉRALES ===
    total_expenses_year = Expense.objects.filter(
        user=request.user,
        date__year=current_year
    ).aggregate(
        total=Sum('amount'),
        count=Count('id'),
        avg=Avg('amount')
    )
    
    # === OBJECTIFS - ANALYSE ===
    goals_stats = {
        'active': Goal.objects.filter(user=request.user, status='active').count(),
        'completed': Goal.objects.filter(user=request.user, status='completed').count(),
        'cancelled': Goal.objects.filter(user=request.user, status='cancelled').count(),
    }
    
    # Progression moyenne des objectifs actifs
    active_goals = Goal.objects.filter(user=request.user, status='active')
    if active_goals.exists():
        total_progress = sum([goal.get_progress_percentage() for goal in active_goals])
        avg_goal_progress = total_progress / active_goals.count()
    else:
        avg_goal_progress = 0
    
    # === CONTRIBUTIONS AUX GROUPES ===
    group_contributions_by_month = GroupContribution.objects.filter(
        user=request.user,
        payment_status='paid',
        date__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')
    
    contribution_labels = [item['month'].strftime('%B %Y') for item in group_contributions_by_month]
    contribution_data = [float(item['total']) for item in group_contributions_by_month]
    
    # Total des contributions
    total_contributions = GroupContribution.objects.filter(
        user=request.user,
        payment_status='paid',
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # === COMPARAISON DÉPENSES vs CONTRIBUTIONS ===
    comparison_labels = []
    comparison_expenses = []
    comparison_contributions = []
    
    for i in range(6):
        month_date = today - timedelta(days=30 * i)
        month_name = month_date.strftime('%B')
        comparison_labels.insert(0, month_name)
        
        # Dépenses du mois
        month_expenses = Expense.objects.filter(
            user=request.user,
            date__month=month_date.month,
            date__year=month_date.year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        comparison_expenses.insert(0, float(month_expenses))
        
        # Contributions du mois
        month_contrib = GroupContribution.objects.filter(
            user=request.user,
            payment_status='paid',
            date__month=month_date.month,
            date__year=month_date.year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        comparison_contributions.insert(0, float(month_contrib))
    
    context = {
        # Graphiques mensuels
        'months_labels': json.dumps(months_labels),
        'months_data': json.dumps(months_data),
        
        # Statistiques mensuelles
        'avg_monthly_expense': avg_monthly_expense,
        'max_monthly_expense': max_monthly_expense,
        'min_monthly_expense': min_monthly_expense,
        'most_expensive_month': most_expensive_month,
        'most_expensive_amount': most_expensive_amount,
        
        # Graphiques par catégorie
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'category_colors': json.dumps(category_colors),
        'expenses_by_category': expenses_by_category,
        
        # Évolution hebdomadaire
        'week_labels': json.dumps(week_labels),
        'week_data': json.dumps(week_data),
        
        # Top dépenses
        'top_expenses': top_expenses,
        
        # Statistiques générales
        'total_expenses_year': total_expenses_year['total'] or 0,
        'total_expenses_count': total_expenses_year['count'] or 0,
        'avg_expense_amount': total_expenses_year['avg'] or 0,
        
        # Objectifs
        'goals_stats': goals_stats,
        'avg_goal_progress': avg_goal_progress,
        
        # Contributions
        'contribution_labels': json.dumps(contribution_labels),
        'contribution_data': json.dumps(contribution_data),
        'total_contributions': total_contributions,
        
        # Comparaison
        'comparison_labels': json.dumps(comparison_labels),
        'comparison_expenses': json.dumps(comparison_expenses),
        'comparison_contributions': json.dumps(comparison_contributions),
        
        # Période
        'current_year': current_year,
    }
    
    return render(request, 'dashboard/statistics.html', context)
