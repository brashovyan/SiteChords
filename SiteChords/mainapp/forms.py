from django import forms


class CreateForm(forms.Form):
    singer = forms.CharField(label="Исполнитель", min_length=2, help_text="Введите полное название исполнителя. Например: Король и Шут")
    album = forms.CharField(label="Альбом", min_length=2, help_text="Если у песни нет альбома, то назовите альбом так же, как и песню")
    song = forms.CharField(label="Песня", min_length=2, help_text="Введите полное название песни")
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': '100'}), label="Содержание", help_text="Содержание вместе с аккордами", min_length=1)
    chords = forms.CharField(label="Аккорды", min_length=1, help_text="Введите аккорды из песни через запятую. Например: Am, F, C, G")


class RegForm(forms.Form):
    username = forms.RegexField(regex="^[A-Za-z0-9-_]+$", min_length=3, label="Логин", required=True)
    email = forms.EmailField(label="Эл. почта", required=True)
    password1 = forms.RegexField(widget=forms.PasswordInput(), regex="(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}", min_length=6, label='Пароль', required=True)
    password2 = forms.RegexField(widget=forms.PasswordInput(), regex="(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}", min_length=6, label='Повторите пароль', required=True)


class Change_profile(forms.Form):
    email = forms.EmailField(label="Эл. почта", required=False)
    first_name = forms.CharField(label='Ваше имя', required=False)
    last_name = forms.CharField(label='Ваша фамилия', required=False)
    password1 = forms.RegexField(widget=forms.PasswordInput(), regex="(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}", min_length=6, label='Новый пароль', required=False)
    password2 = forms.RegexField(widget=forms.PasswordInput(), regex="(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}", min_length=6, label='Повторите пароль', required=False)


"""class LoginForm(forms.Form):
    username = forms.RegexField(regex="^\S*$", min_length=3)
    password = forms.RegexField(widget=forms.PasswordInput(), regex="(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}", min_length=6)"""


