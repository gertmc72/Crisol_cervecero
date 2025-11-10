from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Review, ReviewPhoto, Beer


class ThreadForm(forms.Form):
    title = forms.CharField(max_length=140, label="Título")
    # Cambiado a campo de texto libre para permitir escritura 100% libre
    beer_name = forms.CharField(
        max_length=120,
        required=False,
        label="Cerveza (opcional)",
        help_text="Escribe el nombre de la cerveza (no es obligatorio)."
    )

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("El título es requerido.")
        return title


class PostForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        label="Respuesta"
    )

    def clean_body(self):
        body = self.cleaned_data.get("body", "").strip()
        if not body:
            raise forms.ValidationError("El cuerpo no puede estar vacío.")
        return body


class ReportForm(forms.Form):
    object_type = forms.ChoiceField(
        choices=(('post', 'post'), ('review', 'review')))
    object_id = forms.IntegerField(min_value=1)
    user_name = forms.CharField(max_length=100)
    reason = forms.CharField(max_length=200)


class ReviewForm(forms.Form):
    user_name = forms.CharField(max_length=100, label="Nombre de usuario")
    # Permitir que el usuario escriba libremente el nombre de la cerveza y el estilo
    beer_name = forms.CharField(
        max_length=120, required=False, label="Nombre de la cerveza")
    style = forms.CharField(max_length=80, required=False, label="Estilo")
    brand = forms.CharField(max_length=120, required=False, label="Marca")
    brewery_name = forms.CharField(
        max_length=120, required=False, label="Cervecería Productora")
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 40}),
        label="Descripción",
        help_text="Máximo 300 palabras"
    )
    aroma = forms.IntegerField(min_value=1, max_value=5, label="Aroma (1-5)")
    sabor = forms.IntegerField(min_value=1, max_value=5, label="Sabor (1-5)")
    cuerpo = forms.IntegerField(min_value=1, max_value=5, label="Cuerpo (1-5)")
    apariencia = forms.IntegerField(
        min_value=1, max_value=5, label="Apariencia (1-5)")
    photo1 = forms.ImageField(required=False, label="Foto 1")
    photo2 = forms.ImageField(required=False, label="Foto 2")
    photo3 = forms.ImageField(required=False, label="Foto 3")

    def clean_comment(self):
        comment = self.cleaned_data.get("comment", "").strip()
        if not comment:
            raise forms.ValidationError("La descripción es requerida.")

        # Contar palabras
        word_count = len(comment.split())
        if word_count > 300:
            raise forms.ValidationError(
                f"La descripción tiene {word_count} palabras. El máximo permitido es 300 palabras."
            )
        return comment

    def clean(self):
        cleaned_data = super().clean()

        # Solo validar fotos si no hay otros errores
        if cleaned_data:
            photo1 = cleaned_data.get("photo1")
            photo2 = cleaned_data.get("photo2")
            photo3 = cleaned_data.get("photo3")

            # Contar cuántas fotos se subieron
            photos = [photo for photo in [photo1, photo2, photo3] if photo]
            photos_count = len(photos)

            if photos_count > 3:
                raise forms.ValidationError(
                    "Solo se pueden subir un máximo de 3 fotos.")

        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={'class': 'form-input', 'placeholder': 'Usuario'}),
        label="Usuario"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-input', 'placeholder': 'Contraseña'}),
        label="Contraseña"
    )


class SignupForm(UserCreationForm):
    """Formulario de registro"""

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Elige un nombre de usuario'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'tu@email.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Repite tu contraseña'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_superuser = False
        user.is_staff = False
        if commit:
            user.save()
        return user


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado de registro que garantiza que los usuarios NO sean superusers"""

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estilizar los campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Elige un nombre de usuario'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'tu@email.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Repite tu contraseña'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        # Asegurar que NUNCA sea superuser
        user.is_superuser = False
        user.is_staff = False
        if commit:
            user.save()
        return user
