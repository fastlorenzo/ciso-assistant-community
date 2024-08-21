# Generated by Django 5.0.4 on 2024-08-21 10:29

import django.db.models.deletion
import iam.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('iam', '0005_alter_user_managers'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('is_published', models.BooleanField(default=False, verbose_name='published')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('mission', models.TextField(blank=True, null=True)),
                ('reference_link', models.URLField(blank=True, null=True)),
                ('folder', models.ForeignKey(default=iam.models.Folder.get_root_folder, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_folder', to='iam.folder')),
                ('owned_folders', models.ManyToManyField(blank=True, related_name='owner', to='iam.folder', verbose_name='Owned folders')),
            ],
            options={
                'verbose_name': 'Entity',
                'verbose_name_plural': 'Entities',
            },
        ),
        migrations.CreateModel(
            name='Representative',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('is_published', models.BooleanField(default=False, verbose_name='published')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('phone', models.CharField(blank=True, max_length=255)),
                ('role', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='representatives', to='tprm.entity', verbose_name='Entity')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
