from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ContentWithChords, Singer, Album, Song, Chord, ChordVariation, Favourites
from .forms import CreateForm, RegForm, Change_profile
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator


def index(request):
    return HttpResponseRedirect('home?filter=new_old')


def home(request):
    selected_filter = request.GET.get('filter')

    if selected_filter == None:
        return HttpResponseRedirect("/")

    if selected_filter == "new_old":  # от новых к старым
        songs = ContentWithChords.objects.all().order_by('-id')
    elif selected_filter == "old_new":  # от старых к новым
        songs = ContentWithChords.objects.all()
    else:  # по лайкам
        songs = ContentWithChords.objects.all().order_by('-likes')

    paginator = Paginator(songs, 20) #мы говорим пагинатору: бери отсюда например по три штучки
                                             #в результате чего он как бы разбивает нашу огромную кучу песен на маленькие кучки по три
    page_number = request.GET.get('page') #после чего получаем из url номер страницы (номера он тоже делает сам в зависимости от кол-ва кучек)
    page_obj = paginator.get_page(page_number) #и на основе номера страницы пагинатор решает какую именно кучку песен надо показать
        #т.е. максимально простыми словами пагинтаор за нас автоматически разбивает огромную кучу на кучки поменьше и отдельно показывает их

    flag_moder = check_moder(request)

    return render(request, 'mainapp/index.html', {"moder":flag_moder, 'page_obj': page_obj, 'selected_filter': selected_filter})

def content(request, id):
    song = ContentWithChords.objects.get(id=id)
    s = song.content
    lines = []
    chords = []

    flag_favourite = False

    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        if Favourites.objects.filter(guitarist=user, song=song):
            flag_favourite = True

    for chord in song.chords.all():
        for cv in ChordVariation.objects.filter(chord=chord):
            chords.append(cv)

    for line in s.split('\n'):
        line = line.replace(" ", "&nbsp;") #для тупого html заменяем все пробелы на это
        lines.append(line)

    flag_moder = check_moder(request)

    return render(request, 'mainapp/content.html', {"song": song, "lines": lines, 'chords':chords, 'flag_favourite':flag_favourite, 'moder':flag_moder})


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

                content = request.POST.get('content')
                final_chords = []

                content = content.split('\n')
                for con in content:
                    if '}' in con and '{' not in con:
                        if con.count('}') == 1 and con.index('}') == 0:
                            con2 = con.replace('}', '')
                            con2 = con2.split(' ')
                            for chord in con2:
                                if chord != "":
                                    try:
                                        chord = chord.strip()
                                        chord2 = Chord.objects.get(title=chord)
                                        if chord2 not in final_chords:
                                            final_chords.append(chord2)
                                    except:

                                        flag_moder = check_moder(request)

                                        error = f"При проверке аккордов произошла ошибка! Убедитесь, что они введены правильно. Строка с возможной ошибкой: {con}"
                                        return render(request, 'mainapp/create.html',
                                                      {"form": form, 'error': error, 'moder': flag_moder})
                        else:
                            flag_moder = check_moder(request)

                            error = f"При проверке аккордов произошла ошибка! Убедитесь, что они введены правильно. Строка с возможной ошибкой: {con}"
                            return render(request, 'mainapp/create.html',
                                          {"form": form, 'error': error, 'moder': flag_moder})


                    elif '{' in con and '}' in con and '{}' not in con:
                        if con.count('{') == 1 and con.count('}') == 1 and (con.index('{') < con.index('}')):
                            con2 = con[con.index('{')+1:con.index('}')]
                            con2 = con2.split(' ')
                            k = 0
                            for chord in con2:
                                if chord != "":
                                    try:
                                        chord = chord.strip()
                                        chord2 = Chord.objects.get(title=chord)
                                        if chord2 not in final_chords:
                                            final_chords.append(chord2)
                                    except:
                                        flag_moder = check_moder(request)

                                        error = f"При проверке аккордов произошла ошибка! Убедитесь, что они введены правильно. Строка с возможной ошибкой: {con}"
                                        return render(request, 'mainapp/create.html',
                                                      {"form": form, 'error': error, 'moder': flag_moder})
                                else:
                                    k += 1

                            if k == len(con2):
                                flag_moder = check_moder(request)

                                error = f"При проверке аккордов произошла ошибка! Убедитесь, что они введены правильно. Строка с возможной ошибкой: {con}"
                                return render(request, 'mainapp/create.html',
                                              {"form": form, 'error': error, 'moder': flag_moder})

                        else:
                            flag_moder = check_moder(request)

                            error = f"При проверке аккордов произошла ошибка! Убедитесь, что они введены правильно. Строка с возможной ошибкой: {con}"
                            return render(request, 'mainapp/create.html',
                                          {"form": form, 'error': error, 'moder': flag_moder})


                    elif not('{' not in con and '}' not in con):
                        flag_moder = check_moder(request)
                        error = f"При проверке аккордов произошла ошибка! Убедитесь, что они введены правильно. Строка с возможной ошибкой: {con}"
                        return render(request, 'mainapp/create.html',
                                      {"form": form, 'error': error, 'moder': flag_moder})

                if not final_chords:
                    flag_moder = check_moder(request)

                    error = "Вы не указали аккорды! Прочитайте, пожалуйста, подсказку ниже."
                    return render(request, 'mainapp/create.html',
                                  {"form": form, 'error': error, 'moder': flag_moder})

                else:
                    song_content.save()
                    for chord in final_chords:
                        chord2 = Chord.objects.get(title=chord)
                        song_content.chords.add(chord2)

                return HttpResponseRedirect("/")

            else:
                flag_moder = check_moder(request)
                form = CreateForm(request.POST)
                error = "Некорректно заполненная форма!"
                return render(request, 'mainapp/create.html', {"form": form, 'error': error, 'moder':flag_moder})

        else:
            flag_moder = check_moder(request)

            form = CreateForm()
            return render(request, 'mainapp/create.html', {"form": form, 'moder':flag_moder})
    else:
        return HttpResponseRedirect("/login")


def register(request):
    if request.method == "POST":
        form = RegForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
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
                form = RegForm()
                return render(request, 'mainapp/register.html', {'form': form, 'error':error})

        else:
            error = "Вы ввели некорректные данные! Повторите попытку, заполнив все поля по подсказкам."
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
    return HttpResponseRedirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    #flag_moder = check_moder(request)

    #return render(request, 'mainapp/about.html', {'moder':flag_moder})


def change(request, id):
    if request.user.is_authenticated:
        if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or ContentWithChords.objects.filter(id=id, creator=request.user).exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
            if request.method == "POST":
                form = CreateForm(request.POST)
                if form.is_valid():
                    song_content = ContentWithChords.objects.get(id=id)
                    singer_old = song_content.song.album.singer
                    album_old = song_content.song.album
                    song_old = song_content.song
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
                        flag_moder = check_moder(request)

                        error = "Вы неправильно ввели аккорды! Или, возможно, каких то аккордов нет в базе данных."
                        return render(request, 'mainapp/change.html', {"form": form, 'error': error, 'moder':flag_moder})

                    if i == len(chords):
                        song_content.chords.clear()
                        song_content.save()
                        for chord in chords:
                            chord = chord.strip()
                            chord2 = Chord.objects.get(title=chord)
                            song_content.chords.add(chord2)

                        #автоочистка.
                        if not ContentWithChords.objects.filter(song=song_old):  # если у песни нет ни одного контента, то удаляем её
                            song_old.delete()

                            if not Song.objects.filter(album=album_old):  # далее если в альбоме нет ни одной песни, удаляем его
                                album_old.delete()

                                if not Album.objects.filter(singer=singer_old):  # если у исполнителя нет ни одного альбома, удаляем его
                                    singer_old.delete()

                        return HttpResponseRedirect("/")

                    else:
                        flag_moder = check_moder(request)

                        error = "Некорректно заполненная форма!"
                        return render(request, 'mainapp/change.html', {"form": form, 'error': error, 'moder':flag_moder})
                else:
                    flag_moder = check_moder(request)

                    error = "Некорректно заполненная форма!"
                    return render(request, 'mainapp/change.html', {"form": form, 'error': error, 'moder':flag_moder})

            else:

                flag_moder = check_moder(request)

                song = ContentWithChords.objects.get(id=id)
                s = ""

                for chord in song.chords.all():
                    s = s + chord.title + ', '
                s = s[0:-2]

                form = CreateForm(initial={'singer': song.song.album.singer, 'album':song.song.album, 'song':song.song, 'content':song.content, 'chords':s})

                return render(request, 'mainapp/change.html', {"form": form, 'song': song, 'moder':flag_moder})
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def delete(request, id):
    if request.user.is_authenticated:
        if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or ContentWithChords.objects.filter(id=id, creator=request.user).exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
            cwc = ContentWithChords.objects.get(id=id)
            if request.method == "POST":
                singer_old = cwc.song.album.singer
                album_old = cwc.song.album
                song_old = cwc.song
                cwc.delete()

                # автоочистка.
                if not ContentWithChords.objects.filter(song=song_old):  # если у песни нет ни одного контента, то удаляем её
                    song_old.delete()

                    if not Song.objects.filter(album=album_old):  # далее если в альбоме нет ни одной песни, удаляем его
                        album_old.delete()

                        if not Album.objects.filter(singer=singer_old):  # если у исполнителя нет ни одного альбома, удаляем его
                            singer_old.delete()

                return HttpResponseRedirect("/")
            else:
                flag_moder = check_moder(request)

                return render(request, 'mainapp/delete.html', {'song': cwc, 'moder':flag_moder})
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def profile(request, id):
    user = User.objects.get(id=id)
    if user == request.user or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
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

                flag_moder = check_moder(request)

                if password1 != "" and password2 != "":
                    if password1 == password2:
                        user.set_password(password1)
                        user.save()
                    else:
                        error = 'Пароли не совпадают!'
                        return render(request, 'mainapp/profile.html', {'form': form, 'error': error, 'moder':flag_moder, 'name':user.username})
                elif password1 != "" or password2 != "":
                    error = 'Пароли не совпадают!'
                    return render(request, 'mainapp/profile.html', {'form': form, 'error': error, 'moder': flag_moder, 'name': user.username})
                else:
                    user.save()

                message = 'Изменения успешно сохранены!'
                return render(request, 'mainapp/profile.html', {'form':form, 'message':message, 'moder':flag_moder, 'name':user.username})
            else:
                flag_moder = check_moder(request)

                error = 'Вы ввели некорректные данные!'
                return render(request, 'mainapp/profile.html', {'form':form, 'error':error, 'moder':flag_moder, 'name':user.username})
        else:
            flag_moder = check_moder(request)

            form = Change_profile(initial={'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name})
            return render(request, 'mainapp/profile.html', {'form':form, 'name':user.username, 'moder':flag_moder})
    else:
        return HttpResponseRedirect("/")


def my_songs(request, id):
    if request.user.is_authenticated:

        user = User.objects.get(id=id)
        if user == request.user or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
            user_songs = ContentWithChords.objects.filter(creator=user).order_by('-id')
            flag_moder = check_moder(request)
            return render(request, 'mainapp/index.html', {'user_songs': user_songs, 'moder':flag_moder})
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def search(request):
    ser = request.GET.get('search_str')

    if ser == None:
        return HttpResponseRedirect("/")

    result = []

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

    flag_moder = check_moder(request)
    return render(request, 'mainapp/index.html', {"moder": flag_moder, 'result': result})

def favourites(request, id):
    if request.user.is_authenticated:
        fav = Favourites()
        user = User.objects.get(id=request.user.id)
        song = ContentWithChords.objects.get(id=id)
        if not Favourites.objects.filter(guitarist=user, song=song):
            fav.guitarist = user
            fav.song = song
            fav.save()
            song.likes += 1
            song.save()
            return HttpResponseRedirect(f"/content/{id}")
        else:
            Favourites.objects.get(guitarist=user, song=song).delete()
            song.likes -= 1
            song.save()
            return HttpResponseRedirect(f"/content/{id}")
    else:
        return HttpResponseRedirect("/")


def my_favourites(request, id):
    if request.user.is_authenticated:
        user = User.objects.get(id=id)
        if user == request.user:
            flag_moder = check_moder(request)
            user_favourites = Favourites.objects.filter(guitarist=user).order_by('-id')
            return render(request, 'mainapp/index.html', {'user_favourites': user_favourites, 'moder':flag_moder})
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def admin(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        if User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
            flag_admin = True
        else:
            flag_admin = False

        return render(request, 'mainapp/admin.html', {'moder':flag_moder, 'admin':flag_admin})
    else:
        return HttpResponseRedirect("/")


def admin_users(request):
    if User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        users = User.objects.all()
        users_in_group = Group.objects.get(name="Moderator").user_set.all()
        if request.method == 'POST':
            ser = request.POST.get('search')
            ser = ser.strip()
            ser = ser.title()
            result = []
            for u in users:
                if ser in u.username.title():
                    result.append(u)

            flag_moder = check_moder(request)

            return render(request, 'mainapp/admin_users.html', {'ser': result, 'group_moder': users_in_group, 'moder':flag_moder})

        else:
            flag_moder = check_moder(request)

            return render(request, 'mainapp/admin_users.html', {'users':users, 'group_moder':users_in_group, 'moder':flag_moder})
    else:
        return HttpResponseRedirect("/")


def admin_users_delete(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        user = User.objects.get(id=id)
        if user.id != 1: #главный админ с айдишником 1 не может быть удалён
            user.delete()
        return HttpResponseRedirect("/admin/users")
    else:
        return HttpResponseRedirect("/")


def admin_users_deletemoder(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        user = User.objects.get(id=id)
        group = Group.objects.get(name='Moderator')
        user.groups.remove(group)
        return HttpResponseRedirect("/admin/users/moder_list")
    else:
        return HttpResponseRedirect("/")


def admin_users_givemoder(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        user = User.objects.get(id=id)
        group = Group.objects.get(name='Moderator')
        user.groups.add(group)
        return HttpResponseRedirect("/admin/users")
    else:
        return HttpResponseRedirect("/")


def admin_users_moderlist(request):
    if User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = check_moder(request)
        hide_search = True
        users_in_group = Group.objects.get(name="Moderator").user_set.all()
        return render(request, 'mainapp/admin_users.html', {'moderators': users_in_group, 'group_moder': users_in_group, 'moder':flag_moder, 'hide_search':hide_search})
    else:
        return HttpResponseRedirect("/")


def admin_singers(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        singers = Singer.objects.all()
        if request.method == 'POST':
            ser = request.POST.get('search')
            ser = ser.strip()
            ser = ser.title()
            result = []
            for u in singers:
                if ser in u.name:
                    result.append(u)
            return render(request, 'mainapp/admin_singers.html', {'ser': result, 'moder': flag_moder})

        else:


            return render(request, 'mainapp/admin_singers.html', {'moder':flag_moder, 'singers':singers})
    else:
        return HttpResponseRedirect("/")


def admin_singers_change(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        singer = Singer.objects.get(id=id)
        albums = Album.objects.filter(singer=singer)

        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '':
                name = name.strip()
                name = name.title()
                singer.name = name
                singer.save()

                return HttpResponseRedirect("/admin/singers")

            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_singers_change.html', {'moder': flag_moder, 'singer': singer, 'albums':albums, 'error':error})
        else:
            return render(request, 'mainapp/admin_singers_change.html', {'moder':flag_moder, 'singer':singer, 'albums':albums})
    else:
        return HttpResponseRedirect("/")


def admin_singers_delete(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        singer = Singer.objects.get(id=id)
        singer.delete()
        return HttpResponseRedirect("/admin/singers")
    else:
        return HttpResponseRedirect("/")


def admin_singers_create(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '':
                name = name.strip()
                name = name.title()
                Singer.objects.create(name=name)

                return HttpResponseRedirect("/admin/singers")
            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_singers_create.html', {'moder': flag_moder, 'error':error})
        else:
            return render(request, 'mainapp/admin_singers_create.html', {'moder':flag_moder})
    else:
        return HttpResponseRedirect("/")


def admin_albums(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        albums = Album.objects.all()
        if request.method == 'POST':
            ser = request.POST.get('search')
            ser = ser.strip()
            ser = ser.title()
            result = []
            for u in albums:
                if ser in u.title:
                    result.append(u)
            return render(request, 'mainapp/admin_albums.html', {'ser': result, 'moder': flag_moder})

        else:

            return render(request, 'mainapp/admin_albums.html', {'moder':flag_moder, 'albums':albums})
    else:
        return HttpResponseRedirect("/")


def admin_albums_change(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        album = Album.objects.get(id=id)
        singers = Singer.objects.all()
        songs = Song.objects.filter(album=album)

        if request.method == 'POST':
            title = request.POST.get('title')
            if title != '':
                title = title.strip()
                title = title.title()
                album.title = title

                singer_id = request.POST['selected_singer']
                album.singer = Singer.objects.get(id=singer_id)

                album.save()

                return HttpResponseRedirect("/admin/albums")

            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_albums_change.html', {'moder': flag_moder, 'album': album, 'singers':singers, 'songs':songs, 'error': error})
        else:
            return render(request, 'mainapp/admin_albums_change.html', {'moder': flag_moder, 'album': album, 'singers':singers, 'songs':songs})
    else:
        return HttpResponseRedirect("/")


def admin_albums_delete(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        album = Album.objects.get(id=id)
        album.delete()
        return HttpResponseRedirect("/admin/albums")
    else:
        return HttpResponseRedirect("/")


def admin_albums_create(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        singers = Singer.objects.all()
        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '':
                name = name.strip()
                name = name.title()
                singer_id = request.POST['selected_singer']
                Album.objects.create(title=name, singer=Singer.objects.get(id=singer_id))

                return HttpResponseRedirect("/admin/albums")
            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_albums_create.html', {'moder': flag_moder, 'error':error, 'singers':singers})
        else:
            return render(request, 'mainapp/admin_albums_create.html', {'moder':flag_moder, 'singers':singers})
    else:
        return HttpResponseRedirect("/")


def admin_songs(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        songs = Song.objects.all()
        if request.method == 'POST':
            ser = request.POST.get('search')
            ser = ser.strip()
            ser = ser.title()
            result = []
            for u in songs:
                if ser in u.title:
                    result.append(u)
            return render(request, 'mainapp/admin_songs.html', {'ser': result, 'moder': flag_moder})

        else:

            return render(request, 'mainapp/admin_songs.html', {'moder':flag_moder, 'songs':songs})
    else:
        return HttpResponseRedirect("/")


def admin_songs_change(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        song = Song.objects.get(id=id)
        albums = Album.objects.all()
        cwc = ContentWithChords.objects.filter(song=song)
        cwc = cwc.count()

        if request.method == 'POST':
            title = request.POST.get('title')
            if title != '':
                title = title.strip()
                title = title.title()
                song.title = title

                album_id = request.POST['selected_album']
                song.album = Album.objects.get(id=album_id)

                song.save()

                return HttpResponseRedirect("/admin/songs")

            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_songs_change.html', {'moder': flag_moder, 'albums': albums, 'song':song, 'cwc':cwc, 'error':error})
        else:
            return render(request, 'mainapp/admin_songs_change.html', {'moder': flag_moder, 'albums': albums, 'song':song, 'cwc':cwc})
    else:
        return HttpResponseRedirect("/")


def admin_songs_delete(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        song = Song.objects.get(id=id)
        song.delete()
        return HttpResponseRedirect("/admin/songs")
    else:
        return HttpResponseRedirect("/")


def admin_songs_create(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        albums = Album.objects.all()
        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '':
                name = name.strip()
                name = name.title()
                album_id = request.POST['selected_album']
                Song.objects.create(title=name, album=Album.objects.get(id=album_id))

                return HttpResponseRedirect("/admin/songs")
            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_songs_create.html', {'moder': flag_moder, 'error':error, 'albums':albums})
        else:
            return render(request, 'mainapp/admin_songs_create.html', {'moder':flag_moder, 'albums':albums})
    else:
        return HttpResponseRedirect("/")


def check_moder(request):
    flag_moder = False
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True

    return flag_moder


def admin_chords(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        chords = Chord.objects.all()
        if request.method == 'POST':
            ser = request.POST.get('search')
            ser = ser.strip()
            result = []
            for u in chords:
                if ser in u.title:
                    result.append(u)
            return render(request, 'mainapp/admin_chords.html', {'ser': result, 'moder': flag_moder})

        else:

            return render(request, 'mainapp/admin_chords.html', {'moder': flag_moder, 'chords': chords})
    else:
        return HttpResponseRedirect("/")


def admin_chords_change(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        chord = Chord.objects.get(id=id)

        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '':
                name = name.strip()
                chord.title = name
                chord.save()

                return HttpResponseRedirect("/admin/chords")

            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_chords_change.html', {'moder': flag_moder, 'chord': chord, 'error':error})
        else:
            return render(request, 'mainapp/admin_chords_change.html', {'moder':flag_moder, 'chord':chord})
    else:
        return HttpResponseRedirect("/")


def admin_chords_delete(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        chord = Chord.objects.get(id=id)
        chord.delete()
        return HttpResponseRedirect("/admin/chords")
    else:
        return HttpResponseRedirect("/")


def admin_chords_create(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '':
                name = name.strip()
                Chord.objects.create(title=name)

                return HttpResponseRedirect("/admin/chords")
            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_chords_create.html', {'moder': flag_moder, 'error':error})
        else:
            return render(request, 'mainapp/admin_chords_create.html', {'moder':flag_moder})
    else:
        return HttpResponseRedirect("/")


def admin_chordvars(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        chordvars = ChordVariation.objects.all()
        if request.method == 'POST':
            ser = request.POST.get('search')
            ser = ser.strip()
            result = []
            for u in chordvars:
                if ser in u.chord.title:
                    result.append(u)
            return render(request, 'mainapp/admin_chordvars.html', {'ser': result, 'moder': flag_moder})

        else:

            return render(request, 'mainapp/admin_chordvars.html', {'moder': flag_moder, 'chordvars': chordvars})
    else:
        return HttpResponseRedirect("/")


def admin_chordvars_change(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        chordvar = ChordVariation.objects.get(id=id)
        chords = Chord.objects.all()

        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '':
                name = name.strip()
                chord_id = request.POST['selected_chord']
                chordvar.chord = Chord.objects.get(id=chord_id)
                chordvar.content = name
                chordvar.save()

                return HttpResponseRedirect("/admin/chordvars")

            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_chordvars_change.html', {'moder': flag_moder, 'chords': chords, 'chordvar':chordvar, 'error':error})
        else:
            return render(request, 'mainapp/admin_chordvars_change.html', {'moder':flag_moder, 'chords':chords, 'chordvar':chordvar})
    else:
        return HttpResponseRedirect("/")

def admin_chordvars_delete(request, id):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        chordvar = ChordVariation.objects.get(id=id)
        chordvar.delete()
        return HttpResponseRedirect("/admin/chordvars")
    else:
        return HttpResponseRedirect("/")


def admin_chordvars_create(request):
    if User.objects.filter(pk=request.user.id, groups__name='Moderator').exists() or User.objects.filter(pk=request.user.id, groups__name='Admin').exists():
        flag_moder = True
        chords = Chord.objects.all()
        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '':
                name = name.strip()
                chord_id = request.POST['selected_chord']
                ChordVariation.objects.create(chord=Chord.objects.get(id=chord_id), content=name)

                return HttpResponseRedirect("/admin/chordvars")
            else:
                error = "Пустое поле!"
                return render(request, 'mainapp/admin_chordvars_create.html', {'moder': flag_moder, 'chords':chords, 'error':error})
        else:
            return render(request, 'mainapp/admin_chordvars_create.html', {'moder':flag_moder, 'chords':chords})
    else:
        return HttpResponseRedirect("/")
