# Generated by Django 2.0.7 on 2018-07-29 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0007_auto_20180729_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentmarks',
            name='obtain_mark',
            field=models.IntegerField(default=None, null=True),
        ),
    ]