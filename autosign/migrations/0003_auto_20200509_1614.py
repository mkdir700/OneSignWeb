# Generated by Django 3.0.3 on 2020-05-09 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autosign', '0002_signtasks_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='signtasks',
            options={'ordering': ['-id'], 'verbose_name': '任务表', 'verbose_name_plural': '任务表'},
        ),
    ]
