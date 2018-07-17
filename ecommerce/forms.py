from django import forms
from django.contrib.auth import get_user_model

User=get_user_model()

class ContactForm(forms.Form):
    fullname=forms.CharField(widget=forms.TextInput(attrs={
        "class":"form-control",
        "placeholder":"Your full Name"
    }))
    email=forms.CharField(widget=forms.EmailInput(attrs={
        "class":"form-control",
        "placeholder":"Enter your email"
    }))
    content=forms.CharField(widget=forms.Textarea(
        {
            "class":"form-control",
            "placeholder":"Your message"
        }
    ))

    def clean_email(self):
       email=self.cleaned_data.get("email")
       if not "gmail.com" in email:
           raise forms.ValidationError("Email Must Be a Gmail.com")
       return email   

    #def clean_content(self):
     # raise forms.ValidationError("Content Is Wrong")
         



class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)        




class RegistrationForm(forms.Form):
    username=forms.CharField()
    email=forms.EmailField()
    password=forms.CharField(widget=forms.PasswordInput)
    password2=forms.CharField(label='confirm password',widget=forms.PasswordInput)



    def clean(self):
        data=self.cleaned_data
        password=self.cleaned_data.get('password')
        password2=self.cleaned_data.get('password2')
        if password2!=password:
            raise forms.ValidationError("Passwords must Match")
        return data


    def clean_username(self):
        username=self.cleaned_data.get('username') 
        qs=User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("Username is taken")
        return username                       


    def clean_email(self):
        email=self.cleaned_data.get('email') 
        qs=User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Email is taken")
        return email                           