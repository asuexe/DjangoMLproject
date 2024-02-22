from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from joblib import load
from sklearn.calibration import LabelEncoder
from macromolecularapp import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token


model = load('./savedmodels/model.joblib')

def home(request):
    return render(request, "authentication/index.html")


def signup(request):
    if request.method=="POST":
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']

        if User.objects.filter(username=username):
            messages.error(request,"Username already exixts")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request,"Email already exixts")
            return redirect('home')  

        if len(username)>15:
            messages.error(request,"Username must be under 15 characters")  

        if password != repassword:
            messages.error(request,"Password does not match")

        if not username.isalnum():
            messages.error(request,"User name must be contain Aplphabet and numericals")
            return redirect('home')        

        myuser = User.objects.create_user(username, email, password)
        myuser.name=name
        myuser.is_active = False

        myuser.save()
        messages.success(request,"Your Account Has Been Succcessfully Created.")
        #welcome email

        subject = "Welcome to our service"
        message = "hello "  +  myuser.name + " !!\n" + "welcome to our service \n Thank you for visiting our website \n We have also sent you a confirmation email \n please confirm your email address in order to active your account. \n\n Thanking You\n Meet Vaghani\nVivek Vaghela"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)
        #email adress confirmation email

        current_site = get_current_site(request)
        email_subject = "Confirm your email @ meetv349@gmail!!!"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin.html')

    return render(request, "authentication/signup.html")

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin.html')
    else:
        return render(request,'activation_failed.html')    


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username,password=password)

        if user is not None:
            login(request, user)
            name = user.first_name
            return render(request, "authentication/index.html",{'name': name})    

        else:
            messages.error(request,"Bad Credentials!")
            return redirect('home')
           
    return render(request, "authentication/signin.html")

def signout(request):
   
   logout(request)
   messages.success(request,"Logged out successfully!")
   return redirect("home")



def predict(request):
    if request.method=="POST":
        sequence = request.POST['sequence']
        residue_count = request.POST['residue_count']

        # Create LabelEncoders for sequence and residue_count
        sequence_encoder = LabelEncoder()
        residue_count_encoder = LabelEncoder()

        # Fit and transform the data using the encoders
        sequencef = sequence_encoder.fit_transform([sequence])
        residue_countf = residue_count_encoder.fit_transform([residue_count])

        # Now you can use the transformed data for prediction
        y_pred = model.predict([[sequencef[0], int(residue_count)]])
        # predicted_label = sequence_encoder.inverse_transform(y_pred)
        return render(request, 'model.html',{'result' : y_pred})
    return render(request, 'model.html')
