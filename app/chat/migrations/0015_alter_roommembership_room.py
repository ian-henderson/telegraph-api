# Generated by Django 5.0.6 on 2024-05-24 20:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0014_alter_message_room_alter_message_sender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roommembership',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='chat.room'),
        ),
    ]