# Generated by Django 5.2 on 2025-04-14 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PinLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='status',
            field=models.CharField(default='Active'),
        ),
    ]
