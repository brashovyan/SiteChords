from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ContentWithChords, Singer, Album, Song, Chord, ChordVariation
from .forms import CreateForm, RegForm, Change_profile
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator



def index(request):
    url = True
    if request.method == "POST":
        flag_moder = False

        result = []
        ser = request.POST.get('search')
        ser = ser.strip()
        ser = ser.title()
        song_db = Song.objects.all()
        singer_db = Singer.objects.all()
        album_db = Album.objects.all()

        for song2 in song_db:
            if ser in song2.title:
                for cr in ContentWithChords.objects.filter(song=song2):
                    if cr not in result:
                        result.append(cr)

        if not result:
            for album2 in album_db:
                if ser in album2.title:
                    song_album = Song.objects.filter(album=album2)
                    for song3 in song_album:
                        for cr2 in ContentWithChords.objects.filter(song=song3):
                            if cr2 not in result:
                                result.append(cr2)

        if not result:
            for singer2 in singer_db:
                if ser in singer2.name:
                    singer_album = Album.objects.filter(singer=singer2)
                    for album3 in singer_album:
                        album_song = Song.objects.filter(album=album3)
                        for song4 in album_song:
                            for cr2 in ContentWithChords.objects.filter(song=song4):
                                if cr2 not in result:
                                    result.append(cr2)

        if not result:
            ser = ser.split(' ')

            for ser2 in reversed(ser):
                for song2 in song_db:
                    if ser2 in song2.title:
                        for cr in ContentWithChords.objects.filter(song=song2):
                            if cr not in result:
                                result.append(cr)

                for album2 in album_db:
                    if ser2 in album2.title:
                        song_album = Song.objects.filter(album=album2)
                        for song3 in song_album:
                            for cr2 in ContentWithChords.objects.filter(song=song3):
                                if cr2 not in result:
                                    result.append(cr2)

                for singer2 in singer_db:
                    if ser2 in singer2.name:
                        singer_album = Album.objects.filter(singer=singer2)
                        for album3 in singer_album:
                            album_song = Song.objects.filter(album=album3)
                            for song4 in album_song:
                                for cr2 in ContentWithChords.objects.filter(song=song4):
                                    if cr2 not in result:
                                        result.append(cr2)

        if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists():
            flag_moder = True
        return render(request, 'mainapp/index.html', {"moder": flag_moder, 'result': result, 'url':url})

    else:
        flag_moder = False
        #songs = ContentWithChords.objects.all() #от старых к новым
        songs = ContentWithChords.objects.all().order_by('-id') #от новых к старым
        paginator = Paginator(songs, 10) #мы говорим пагинатору: бери отсюда например по три штучки
                                         #в результате чего он как бы разбивает нашу огромную кучу песен на маленькие кучки по три
        page_number = request.GET.get('page') #после чего получаем из url номер страницы (номера он тоже делает сам в зависимости от кол-ва кучек)
        page_obj = paginator.get_page(page_number) #и на основе номера страницы пагинатор решает какую именно кучку песен надо показать
        #т.е. максимально простыми словами пагинтаор за нас автоматически разбивает огромную кучу на кучки поменьше и отдельно показывает их

        if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists():
            flag_moder = True

        return render(request, 'mainapp/index.html', {"moder":flag_moder, 'page_obj': page_obj, "url":url})

def content(request, id):
    song = ContentWithChords.objects.get(id=id)
    s = song.content
    lines = []
    chords = []

    for chord in song.chords.all():
        for cv in ChordVariation.objects.filter(chord=chord):
            chords.append(cv)

    for line in s.split('\n'):
        line = line.replace(" ", "&nbsp;") #для тупого html заменяем все пробелы на это
        lines.append(line)
    return render(request, 'mainapp/content.html', {"song": song, "lines": lines, 'chords':chords})


def create(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CreateForm(request.POST)
            if form.is_valid():
                song_content = ContentWithChords()
                flag_singer = False
                flag_album = False
                flag_song = False

                singer = request.POST.get('singer')
                singer = singer.strip()
                singer = singer.title()
                singer_db = Singer.objects.all()

                for singer2 in singer_db:
                    if singer == singer2.name:
                        singer = singer2
                        flag_singer = True
                        break

                if flag_singer == False:
                    for singer2 in singer_db:
                        if singer in singer2.name:
                            singer = singer2
                            flag_singer = True
                            break

                if flag_singer == False:
                    Singer.objects.create(name=singer)

                album = request.POST.get('album')
                album = album.strip()
                album = album.title()
                album_db = Album.objects.filter(singer=Singer.objects.get(name=singer))

                for album2 in album_db:
                    if album == album2.title:
                        album = album2.title
                        flag_album = True
                        break

                if flag_album == False:
                    for album2 in album_db:
                        if album in album2.title:
                            album = album2.title
                            flag_album = True
                            break

                if flag_album == False:
                    Album.objects.create(title=album, singer=Singer.objects.get(name=singer))

                song = request.POST.get('song')
                song = song.strip()
                song = song.title()
                song_db = Song.objects.filter(album=Album.objects.get(singer=Singer.objects.get(name=singer), title=album))

                for song2 in song_db:
                    if song in song2.title:
                        song = song2.title
                        flag_song = True
                        break

                if flag_song == False:
                    for song2 in song_db:
                        if song in song2.title:
                            song = song2.title
                            flag_song = True
                            break

                if flag_song == False:
                    Song.objects.create(title=song, album=Album.objects.get(singer=Singer.objects.get(name=singer), title=album))

                song_content.song = Song.objects.get(album=Album.objects.get(singer=Singer.objects.get(name=singer), title=album), title=song)
                song_content.creator = User.objects.get(username=request.user.username)
                song_content.content = request.POST.get('content')

                chords = request.POST.get('chords')
                chords = chords.split(',') #сплитим по запятым
                i = 0
                try:
                    for chord in chords:
                        chord = chord.strip() #убираем лишние пробелы
                        chord2 = Chord.objects.get(title=chord)
                        i = i + 1
                except:
                    error = "Вы неправильно ввели аккорды! Пожалуйста, введите аккорды согласно подсказке (так же возмжна ситуация," \
                            " что в нашей базе данных нет таких аккордов. В таком случае пропустите это поле," \
                            " написав любой обычный аккорд (например Am), и обратитесь к модератору)"
                    return render(request, 'mainapp/create.html', {"form": form, 'error': error})

                if i == len(chords):
                    song_content.save()
                    for chord in chords:
                        chord = chord.strip()
                        chord2 = Chord.objects.get(title=chord)
                        song_content.chords.add(chord2)

                return HttpResponseRedirect("/")
            else:
                error = "Некорректно заполненная форма!"
                return render(request, 'mainapp/create.html', {"form": form, 'error': error})

        else:
            form = CreateForm()
            return render(request, 'mainapp/create.html', {"form": form})
    else:
        return HttpResponseRedirect("/login")


def register(request):
    if request.method == "POST":
        form = RegForm(request.POST)
        if form.is_valid():
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                username = request.POST.get('username')
                email = request.POST.get('email')
                try:
                    user = User.objects.create_user(username, email, password1)
                except:
                    error = "Данный логин уже занят. Попробуйте другой."
                    form = RegForm()
                    return render(request, 'mainapp/register.html', {'form': form, 'error': error})
                if request.user.is_authenticated:
                    logout(request)
                login(request, user)

                user2 = User.objects.get(username=request.user.username)
                group = Group.objects.get(name='Guitarist')
                user2.groups.add(group)
                return HttpResponseRedirect("/")
            else:
                error = "Пароли не совпадают!"
                #form = RegisterForm()
                return render(request, 'mainapp/register.html', {'form': form, 'error':error})

        else:
            error = "Вы ввели некорректные данные! Повторите попытку, заполнив все поля по подсказкам."
            form = RegForm()
            return render(request, 'mainapp/register.html', {'form': form, 'error': error})
    else:
        form = RegForm()
        return render(request, 'mainapp/register.html', {'form': form})


def login1(request):
    if request.method == "POST":
        #form = LoginForm(request.POST)

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            error = "Неверный логин или пароль! Проверьте раскладку языка. Также напоминаем, что буквы верхнего и нижнего регистра (строчные и заглавные) отличаются между собой."
            #form = LoginForm()
            return render(request, 'mainapp/login.html', {'error': error})

    else:
        if request.user.is_authenticated:
            logout(request)
        #form = LoginForm()
        return render(request, 'mainapp/login.html')


def logout1(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def about(request):
    return render(request, 'mainapp/about.html',)


def change(request, id):
    if request.user.is_authenticated:
        if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or ContentWithChords.objects.filter(id=id, creator=request.user).exists():
            if request.method == "POST":
                form = CreateForm(request.POST)
                if form.is_valid():
                    song10 = ContentWithChords.objects.get(id=id)
                    singer_old = song10.song.album.singer
                    album_old = song10.song.album
                    song_old = song10.song


                    song_content = ContentWithChords.objects.get(id=id)
                    flag_singer = False
                    flag_album = False
                    flag_song = False

                    singer = request.POST.get('singer')
                    singer = singer.strip()
                    singer = singer.title()
                    singer_db = Singer.objects.all()

                    for singer2 in singer_db:
                        if singer == singer2.name:
                            singer = singer2
                            flag_singer = True
                            break

                    if flag_singer == False:
                        Singer.objects.create(name=singer)

                    album = request.POST.get('album')
                    album = album.strip()
                    album = album.title()
                    album_db = Album.objects.filter(singer=Singer.objects.get(name=singer))
                    for album2 in album_db:
                        if album == album2.title:
                            album = album2.title
                            flag_album = True
                            break

                    if flag_album == False:
                        Album.objects.create(title=album, singer=Singer.objects.get(name=singer))

                    song = request.POST.get('song')
                    song = song.strip()
                    song = song.title()
                    song_db = Song.objects.filter(album=Album.objects.get(singer=Singer.objects.get(name=singer), title=album))
                    for song2 in song_db:
                        if song == song2.title:
                            song = song2.title
                            flag_song = True
                            break

                    if flag_song == False:
                        Song.objects.create(title=song, album=Album.objects.get(singer=Singer.objects.get(name=singer), title=album))

                    song_content.song = Song.objects.get(album=Album.objects.get(singer=Singer.objects.get(name=singer), title=album), title=song)
                    #song_content.creator = User.objects.get(username=request.user.username)
                    song_content.content = request.POST.get('content')

                    chords = request.POST.get('chords')
                    chords = chords.split(',')  # сплитим по запятым
                    i = 0
                    try:
                        for chord in chords:
                            chord = chord.strip()  # убираем лишние пробелы
                            chord2 = Chord.objects.get(title=chord)
                            i = i + 1
                    except:
                        error = "Вы неправильно ввели аккорды! Или, возможно, каких то аккордов нет в базе данных."
                        return render(request, 'mainapp/change.html', {"form": form, 'error': error})

                    if i == len(chords):
                        song_content.chords.clear()
                        song_content.save()
                        for chord in chords:
                            chord = chord.strip()
                            chord2 = Chord.objects.get(title=chord)
                            song_content.chords.add(chord2)

                        #автоочистка.
                        song_old2 = Song.objects.get(album=Album.objects.get(singer=Singer.objects.get(name=singer_old), title=album_old), title=song_old)
                        if not ContentWithChords.objects.filter(song=song_old2): #если у песни нет ни одного контента, то удаляем её
                            song_old2.delete()
                            #print(f'Удалить песню {song_old2.title}')

                            album_old2 = Album.objects.get(singer=Singer.objects.get(name=singer_old), title=album_old)
                            if not Song.objects.filter(album=album_old2): #далее если в альбоме нет ни одной песни, удаляем его
                                album_old2.delete()
                                #print(f'Удалить альбом {album_old2.title}')

                                singer_old2 = Album.objects.filter(singer=Singer.objects.get(name=singer_old)) #
                                if not singer_old2: #если у исполнителя нет ни одного альбома, удаляем его
                                    Singer.objects.get(name=singer_old).delete()

                        return HttpResponseRedirect("/")

                    else:
                        error = "Некорректно заполненная форма!"
                        return render(request, 'mainapp/change.html', {"form": form, 'error': error})
                else:
                    error = "Некорректно заполненная форма!"
                    return render(request, 'mainapp/change.html', {"form": form, 'error': error})

            else:
                song = ContentWithChords.objects.get(id=id)
                s = ""

                for chord in song.chords.all():
                    s = s + chord.title + ', '
                s = s[0:-2]

                form = CreateForm(initial={'singer': song.song.album.singer, 'album':song.song.album, 'song':song.song, 'content':song.content, 'chords':s})

                return render(request, 'mainapp/change.html', {"form": form, 'song': song})
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def delete(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists():
        song = ContentWithChords.objects.get(id=id)
        if request.method == "POST":
            song.delete()

            return HttpResponseRedirect("/")
        else:
            return render(request, 'mainapp/delete.html', {'song': song})
    else:
        return HttpResponseRedirect("/")


def profile(request, id):
    user = User.objects.get(id=id)
    if user == request.user:
        if request.method == 'POST':
            form = Change_profile(request.POST)
            if form.is_valid():
                email = request.POST.get('email')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                if password1 != "" and password2 != "":
                    if password1 == password2:
                        user.set_password(password1)
                        user.save()
                    else:
                        error = 'Пароли не совпадают!'
                        return render(request, 'mainapp/profile.html', {'form': form, 'error': error})
                else:
                    user.save()

                message = 'Изменения успешно сохранены!'
                return render(request, 'mainapp/profile.html', {'form':form, 'message':message})
            else:
                error = 'Вы ввели некорректные данные!'
                return render(request, 'mainapp/profile.html', {'form':form, 'error':error})
        else:
            form = Change_profile(initial={'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name})
            return render(request, 'mainapp/profile.html', {'form':form})
    else:
        return HttpResponseRedirect("/")


def my_songs(request, id):
    if request.user.is_authenticated:
        user = User.objects.get(id=id)
        if user == request.user:
            url = True
            user_songs = ContentWithChords.objects.filter(creator=user).order_by('-id')
            return render(request, 'mainapp/index.html', {'user_songs': user_songs})
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
