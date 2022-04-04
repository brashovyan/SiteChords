# Generated by Django 4.0.3 on 2022-03-31 07:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0006_remove_album_year_remove_singer_sostav'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favourites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guitarist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.contentwithchords', verbose_name='Песня')),
            ],
        ),
    ]