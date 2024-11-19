# Generated by Django 5.1.1 on 2024-11-19 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_riskscenario_existing_applied_controls'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='internal_reference',
            new_name='ref_id'
        ),
        migrations.AlterField(
            model_name='project',
            name='ref_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='reference id'),
        ),
        migrations.AddField(
            model_name='appliedcontrol',
            name='ref_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='reference id'),
        ),
        migrations.AddField(
            model_name='complianceassessment',
            name='ref_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='reference id'),
        ),
        migrations.AddField(
            model_name='riskassessment',
            name='ref_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='reference id'),
        ),
    ]
