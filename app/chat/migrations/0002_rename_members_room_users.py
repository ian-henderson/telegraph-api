# Generated by Django 5.0.6 on 2024-05-21 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='members',
            new_name='users',
        ),
    ]