# Generated by Django 5.0.6 on 2024-05-22 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_alter_message_room_alter_message_sender'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('created_at',)},
        ),
    ]
