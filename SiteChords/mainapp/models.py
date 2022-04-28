from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Singer(models.Model):
    name = models.CharField(max_length=250, help_text='Введите название исполнителя', verbose_name='Исполнитель', null=False)
    #sostav = models.TextField(help_text='Введите состав группы (при наличии)', verbose_name='Состав группы', blank=True, null=True)
    objects = models.Manager() #служебное поле для доступа к объектам в базе данных

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=250, help_text='Введите название альбома', verbose_name="Название альбома", null=False)
    singer = models.ForeignKey('Singer', on_delete=models.CASCADE, help_text='Выберите исполнителя', verbose_name='Исполнитель', null=False)
    #year = models.IntegerField(help_text='Введите год выпуска альбома', verbose_name='Год выпуска альбома', blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return self.title


class Song(models.Model):
    title = models.CharField(max_length=250, help_text='Введите название песни', verbose_name="Название песни", null=False)
    album = models.ForeignKey('Album', on_delete=models.CASCADE, help_text='Выберите альбом', verbose_name='Альбом', null=False)
    objects = models.Manager()

    def __str__(self):
        return self.title


class ContentWithChords(models.Model):
    song = models.ForeignKey('Song', on_delete=models.CASCADE, help_text="Выберите песню", verbose_name='Песня', null=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель', null=False)
    content = models.TextField(help_text='Введите содержание (текст песни с расставленными аккордами', verbose_name='Содержание', null=False)
    chords = models.ManyToManyField('Chord', help_text='Выберите какие аккорды есть в вашем содержании (например Am, C, F).', verbose_name='Аккорды')
    likes = models.IntegerField(default=0, help_text="Введите кол-во лайков", verbose_name="Лайки")
    objects = models.Manager()

    def __str__(self):
        return '%s: %s' % (self.song, self.creator)

    """def get_absolute_url(self):
        return reverse('content', args[str(self.id)])"""


class Chord(models.Model):
    title = models.CharField(max_length=20, help_text='Название аккорда (например Am)', verbose_name="Аккорд", null=False)
    objects = models.Manager()

    def __str__(self):
        return self.title


class ChordVariation(models.Model):
    chord = models.ForeignKey('Chord', on_delete=models.CASCADE, help_text='Выберите аккорд', verbose_name="Аккорд", null=False)
    content = models.TextField(help_text='Описание аккорда, картинка или ссылка', verbose_name='Описание аккорда', null=False)
    objects = models.Manager()

    def __str__(self):
        return '%s' % (self.chord)


class Favourites(models.Model):
    guitarist = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', null=False)
    song = models.ForeignKey(ContentWithChords, on_delete=models.CASCADE, verbose_name='Песня', null=False)
    objects = models.Manager()

