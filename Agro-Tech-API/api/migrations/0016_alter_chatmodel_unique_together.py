# Generated by Django 5.0.6 on 2024-09-04 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_rename_room_group_name_chatmodel_room_name_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='chatmodel',
            unique_together={('name', 'receiver')},
        ),
    ]
