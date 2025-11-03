from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ThreadForm(forms.Form):
    title = forms.CharField(max_length=140)
    user_name = forms.CharField(max_length=100)

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("El título es requerido.")
        return title


class PostForm(forms.Form):
    user_name = forms.CharField(max_length=100)
    body = forms.CharField(widget=forms.Textarea)

    def clean_body(self):
        body = self.cleaned_data.get("body", "").strip()
        if not body:
            raise forms.ValidationError("El cuerpo no puede estar vacío.")
        return body


class ReportForm(forms.Form):
    object_type = forms.ChoiceField(choices=(('post', 'post'), ('review', 'review')))
    object_id = forms.IntegerField(min_value=1)
    user_name = forms.CharField(max_length=100)
    reason = forms.CharField(max_length=200)


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
