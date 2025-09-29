from django import forms 
from .models import Order, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'address']
        


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подвердите пароль')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data



class LoginForm(AuthenticationForm):
    username = forms.CharField(label='логин')
    password = forms.CharField(widget=forms.PasswordInput, label='пароль')



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Напишите свой отзыв'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }