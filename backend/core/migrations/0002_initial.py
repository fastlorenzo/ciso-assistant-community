# Generated by Django 5.0.2 on 2024-02-23 00:51

import django.db.models.deletion
import iam.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('iam', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='folder',
            field=models.ForeignKey(default=iam.models.Folder.get_root_folder, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='asset',
            name='parent_assets',
            field=models.ManyToManyField(blank=True, to='core.asset', verbose_name='parent assets'),
        ),
        migrations.AddField(
            model_name='complianceassessment',
            name='authors',
            field=models.ManyToManyField(blank=True, related_name='%(class)s_authors', to=settings.AUTH_USER_MODEL, verbose_name='Authors'),
        ),
        migrations.AddField(
            model_name='complianceassessment',
            name='reviewers',
            field=models.ManyToManyField(blank=True, related_name='%(class)s_reviewers', to=settings.AUTH_USER_MODEL, verbose_name='Reviewers'),
        ),
        migrations.AddField(
            model_name='evidence',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='framework',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='complianceassessment',
            name='framework',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.framework', verbose_name='Framework'),
        ),
        migrations.AddField(
            model_name='library',
            name='dependencies',
            field=models.ManyToManyField(blank=True, to='core.library', verbose_name='Dependencies'),
        ),
        migrations.AddField(
            model_name='library',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='framework',
            name='library',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='frameworks', to='core.library'),
        ),
        migrations.AddField(
            model_name='project',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='complianceassessment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project', verbose_name='Project'),
        ),
        migrations.AddField(
            model_name='requirementassessment',
            name='compliance_assessment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requirement_assessments', to='core.complianceassessment', verbose_name='Compliance assessment'),
        ),
        migrations.AddField(
            model_name='requirementassessment',
            name='evidences',
            field=models.ManyToManyField(blank=True, related_name='requirement_assessments', to='core.evidence', verbose_name='Evidences'),
        ),
        migrations.AddField(
            model_name='requirementassessment',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='requirementlevel',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='requirementlevel',
            name='framework',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.framework', verbose_name='Framework'),
        ),
        migrations.AddField(
            model_name='requirementnode',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='requirementnode',
            name='framework',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.framework', verbose_name='Framework'),
        ),
        migrations.AddField(
            model_name='requirementassessment',
            name='requirement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.requirementnode', verbose_name='Requirement'),
        ),
        migrations.AddField(
            model_name='riskacceptance',
            name='approver',
            field=models.ForeignKey(blank=True, help_text='Risk owner and approver identity', max_length=200, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Approver'),
        ),
        migrations.AddField(
            model_name='riskacceptance',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='riskassessment',
            name='authors',
            field=models.ManyToManyField(blank=True, related_name='%(class)s_authors', to=settings.AUTH_USER_MODEL, verbose_name='Authors'),
        ),
        migrations.AddField(
            model_name='riskassessment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project', verbose_name='Project'),
        ),
        migrations.AddField(
            model_name='riskassessment',
            name='reviewers',
            field=models.ManyToManyField(blank=True, related_name='%(class)s_reviewers', to=settings.AUTH_USER_MODEL, verbose_name='Reviewers'),
        ),
        migrations.AddField(
            model_name='riskmatrix',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='riskmatrix',
            name='library',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='risk_matrices', to='core.library'),
        ),
        migrations.AddField(
            model_name='riskassessment',
            name='risk_matrix',
            field=models.ForeignKey(help_text='WARNING! After choosing it, you will not be able to change it', on_delete=django.db.models.deletion.PROTECT, to='core.riskmatrix', verbose_name='Risk matrix'),
        ),
        migrations.AddField(
            model_name='riskscenario',
            name='assets',
            field=models.ManyToManyField(blank=True, help_text='Assets impacted by the risk scenario', related_name='risk_scenarios', to='core.asset', verbose_name='Assets'),
        ),
        migrations.AddField(
            model_name='riskscenario',
            name='risk_assessment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='risk_scenarios', to='core.riskassessment', verbose_name='RiskAssessment'),
        ),
        migrations.AddField(
            model_name='riskacceptance',
            name='risk_scenarios',
            field=models.ManyToManyField(help_text='Select the risk scenarios to be accepted, attention they must be part of the chosen domain', to='core.riskscenario', verbose_name='Risk scenarios'),
        ),
        migrations.AddField(
            model_name='securityfunction',
            name='folder',
            field=models.ForeignKey(default=iam.models.Folder.get_root_folder, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='securityfunction',
            name='library',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='security_functions', to='core.library'),
        ),
        migrations.AddField(
            model_name='requirementnode',
            name='security_functions',
            field=models.ManyToManyField(blank=True, related_name='requirements', to='core.securityfunction', verbose_name='Security functions'),
        ),
        migrations.AddField(
            model_name='securitymeasure',
            name='evidences',
            field=models.ManyToManyField(blank=True, related_name='security_measures', to='core.evidence', verbose_name='Evidences'),
        ),
        migrations.AddField(
            model_name='securitymeasure',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='securitymeasure',
            name='security_function',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.securityfunction', verbose_name='Security Function'),
        ),
        migrations.AddField(
            model_name='riskscenario',
            name='security_measures',
            field=models.ManyToManyField(blank=True, related_name='risk_scenarios', to='core.securitymeasure', verbose_name='Security measures'),
        ),
        migrations.AddField(
            model_name='requirementassessment',
            name='security_measures',
            field=models.ManyToManyField(blank=True, related_name='requirement_assessments', to='core.securitymeasure', verbose_name='Security measures'),
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
            ],
            options={
                'verbose_name': 'Policy',
                'verbose_name_plural': 'Policies',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.securitymeasure',),
        ),
        migrations.AddField(
            model_name='threat',
            name='folder',
            field=models.ForeignKey(default=iam.models.Folder.get_root_folder, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder'),
        ),
        migrations.AddField(
            model_name='threat',
            name='library',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='threats', to='core.library'),
        ),
        migrations.AddField(
            model_name='riskscenario',
            name='threats',
            field=models.ManyToManyField(blank=True, related_name='risk_scenarios', to='core.threat', verbose_name='Threats'),
        ),
        migrations.AddField(
            model_name='requirementnode',
            name='threats',
            field=models.ManyToManyField(blank=True, related_name='requirements', to='core.threat', verbose_name='Threats'),
        ),
    ]
