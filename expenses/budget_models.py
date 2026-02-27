from django.db import models
from django.contrib.auth.models import User
from expenses.models import Category


class Budget(models.Model):
    """
    Modèle pour définir des budgets mensuels par catégorie.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets', null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant du budget")
    month = models.IntegerField(verbose_name="Mois (1-12)")
    year = models.IntegerField(verbose_name="Année")
    alert_threshold = models.IntegerField(default=80, verbose_name="Seuil d'alerte (%)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category', 'month', 'year']
        ordering = ['-year', '-month']
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
    
    def __str__(self):
        category_name = self.category.name if self.category else "Global"
        return f"{self.user.username} - {category_name} - {self.month}/{self.year}"
    
    def get_spent_amount(self):
        """Calcule le montant dépensé pour ce budget."""
        from expenses.models import Expense
        
        expenses = Expense.objects.filter(
            user=self.user,
            date__month=self.month,
            date__year=self.year
        )
        
        if self.category:
            expenses = expenses.filter(category=self.category)
        
        return expenses.aggregate(total=models.Sum('amount'))['total'] or 0
    
    def get_remaining_amount(self):
        """Calcule le montant restant."""
        return self.amount - self.get_spent_amount()
    
    def get_progress_percentage(self):
        """Calcule le pourcentage utilisé du budget."""
        spent = self.get_spent_amount()
        if self.amount == 0:
            return 0
        percentage = (spent / self.amount) * 100
        return min(percentage, 100)
    
    def is_exceeded(self):
        """Vérifie si le budget est dépassé."""
        return self.get_spent_amount() > self.amount
    
    def is_alert_threshold_reached(self):
        """Vérifie si le seuil d'alerte est atteint."""
        return self.get_progress_percentage() >= self.alert_threshold
    
    def get_status(self):
        """Retourne le statut du budget."""
        if self.is_exceeded():
            return 'exceeded'
        elif self.is_alert_threshold_reached():
            return 'warning'
        else:
            return 'ok'
    
    def get_status_color(self):
        """Retourne la couleur selon le statut."""
        status = self.get_status()
        return {
            'ok': 'success',
            'warning': 'warning',
            'exceeded': 'danger'
        }.get(status, 'secondary')
