# Generated manually on 2026-01-08
"""
Migration de données : créer un GroupGoal par défaut pour chaque Group existant
basé sur l'objectif principal du groupe (target_amount, current_amount, deadline).
"""

from django.db import migrations


def create_default_group_goals(apps, schema_editor):
    """
    Créer un GroupGoal "Objectif principal" pour chaque groupe existant,
    en reprenant les données de Group.target_amount, current_amount, deadline.
    """
    Group = apps.get_model('groups', 'Group')
    GroupGoal = apps.get_model('groups', 'GroupGoal')
    
    groups = Group.objects.all()
    goals_created = 0
    
    for group in groups:
        # Créer l'objectif par défaut basé sur l'objectif du groupe
        GroupGoal.objects.create(
            group=group,
            title=f"Objectif principal - {group.name}",
            description=group.description or f"Objectif de collecte pour {group.name}",
            goal_type='savings',  # Type par défaut
            target_amount=group.target_amount,
            current_amount=group.current_amount,
            deadline=group.deadline,
            status=group.status,
            created_by=group.creator,
        )
        goals_created += 1
    
    if goals_created > 0:
        print(f"✅ {goals_created} objectifs par défaut créés pour les groupes existants")
    else:
        print("ℹ️ Aucun groupe existant, pas d'objectifs à créer")


def reverse_migration(apps, schema_editor):
    """
    Supprimer tous les GroupGoal créés par cette migration.
    """
    GroupGoal = apps.get_model('groups', 'GroupGoal')
    count = GroupGoal.objects.all().count()
    GroupGoal.objects.all().delete()
    print(f"🔄 {count} objectifs supprimés (rollback)")


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0006_groupgoal'),
    ]

    operations = [
        migrations.RunPython(
            create_default_group_goals,
            reverse_code=reverse_migration
        ),
    ]
