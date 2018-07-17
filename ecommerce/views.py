from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from .forms import ContactForm,LoginForm,RegistrationForm
from django.contrib.auth import authenticate,login,get_user_model
def home_page(request):
    #print(request.session.get("first_name","unknown"))
    context={
        "title":"This is a  Home Page",
        "content":"Welcome to Home Page"
        
    }
    if request.user.is_authenticated():
        context["premium_content"]="YEAHH"
    return render(request,"home_page.html",context)


def about_page(request):
    context={
        "title":"This is a  About Page",
        "content":"Welcome to About Page"

    }
    return render(request,"home_page.html",context)



def contact_page(request):
    contact_form=ContactForm(request.POST or None)
    context={
        "title":"Enter Your Contact Details",
        "content":"",
        "form":contact_form
        
    }
    if contact_form.is_valid():
        print(contact_form.cleaned_data)
        if request.is_ajax():
            return JsonResponse({"message":"ThankYou For Your Submission"})

    if contact_form.errors:
        errors = contact_form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errors, status=400, content_type='application/json')

    #if request.method=="POST":
       # print(request.POST)
     #   print(request.POST.get('fullname'))
      #  print(request.POST.get('email'))
       # print(request.POST.get('content'))
    return render(request,"contact/view.html",context)




def login_page(request):
    form=LoginForm(request.POST or None)
    context={
        "form":form
    }
    #print("User logged in")
    #print(request.user.is_authenticated())

    if form.is_valid():
        #print(form.cleaned_data)
        username=form.cleaned_data.get("username")
        password=form.cleaned_data.get("password")
        user=authenticate(request,username=username,password=password)
        if user is not None:
            #print(request.user.is_authenticated())
            login(request,user)
            #context['form']=LoginForm()
            return redirect("/")
        else:
            print("Error")

    return render(request,"auth/login.html",context)

User=get_user_model()
def register_page(request):
    form=RegistrationForm(request.POST or None)
    context={
        "form":form
    }
    if form.is_valid():
        print(form.cleaned_data)
        username=form.cleaned_data.get("username")
        email=form.cleaned_data.get("email")
        password=form.cleaned_data.get("password")
        new_user=User.objects.create_user(username,email,password)

        
    return render(request,"auth/register.html",context)        
