from django.shortcuts import render, redirect
from django.views import View
from .forms import RegisterationForm, LoginForm, ProfileChangeForm, User

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.views import View
from django.contrib.auth import login
from .forms import RegisterationForm, LoginForm, ProfileChangeForm
from django.urls import reverse_lazy
import re

from .token import account_activation_token

from pprint import pprint
from faker import Faker
from myapp.models import Comment


  
class Home(View):
  def get(self, request):
    # url = 'https://jsonplaceholder.typicode.com/comments'
    # res = requests.get(url)
    # data = json.loads(res.text)
    # pprint(data)
    # Create User
    fk = Faker()
    # for i in range(1, 501):
    #   user = User.objects.create_user(f"user{i}", password= "Dera@123")
    #   user.save()
    # translator = Translator()
    # for i in data:
    #   user = User.objects.get(id=i.get('userId'))
    #   title = translator.translate(i.get('title')).text
    #   desc = translator.translate(i.get('body')).text
    #   Blog.objects.create(title=title, description=desc, userId=user)
      # name = fk.name()
      # email = fk.email()
      # print(i, fk.text(), '\n')
      # commentId = Comment.objects.get(commentId=i)
      # commentId.comment = fk.text()
      # commentId.name = name
      # commentId.email = email
      # commentId.save()
    return render(request, 'myapp/home.html')
  
class Docs(View):
  def get(self, request):
    data = dict(url=request.build_absolute_uri("/"))
    return render(request, 'myapp/docs.html', data)
  
def activateEmail(request, user, to_email):
  mail_subject = 'Activate your user account.'
  message = render_to_string('myapp/activate_account.html', {
    'user': user.username,
    'domain': get_current_site(request).domain,
    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    'token': account_activation_token.make_token(user),
    'protocol': 'https' if request.is_secure() else 'http'
  })
  email = EmailMessage(mail_subject, message, to=[to_email])
  try:
    if email.send():
      messages.success(request, f'Dear <strong>{user}</strong>, please go to your email (<strong>{to_email}</strong>) inbox and click on \
          received activation link to confirm and complete the registration. <strong>Note:</strong> Check your spam folder.')
    else:
      messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')
  except:
    messages.error(request, "Something went wront or Email id not valid.")

def register(request):
    if request.method == "POST":
        form = RegisterationForm(request.POST)
        if form.is_valid():
          user = form.save(commit=False)
          user.is_active = False
          user.save()
          activateEmail(request, user, form.cleaned_data.get('email'))
          return redirect('login')
        else:
          return render(request=request, template_name="myapp/register.html", context={"form": form})
    else:
      form = RegisterationForm()
    return render(request=request, template_name="myapp/register.html", context={"form": form})

def activate(request, uidb64, token):
  User = get_user_model()
  try:
      uid = force_str(urlsafe_base64_decode(uidb64))
      user = User.objects.get(pk=uid)
  except(TypeError, ValueError, OverflowError, User.DoesNotExist):
      user = None
  if user is not None and account_activation_token.check_token(user, token):
    user.is_active = True
    user.save()
    messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
    return redirect('login')
  else:
    messages.error(request, 'Activation link is invalid!')
  return redirect('login')


class MyLoginView(LoginView):
  form_class = LoginForm
  authentication_form = None
  template_name = "myapp/login.html"
  redirect_authenticated_user = True
  extra_context = None 


class RegisterView(FormView):
  template_name = 'myapp/register.html'
  form_class = RegisterationForm
  redirect_authenticated_user = True
  success_url = reverse_lazy('login')
  
  def form_valid(self, form):
    user = form.save()
    if user:
      login(self.request, user)
    
    return super(RegisterView, self).form_valid(form)

@method_decorator(login_required, name='dispatch')  
class ProfileView(View):
  # def get(self, request):
  #   return render(request, 'myapp/profile.html')  
  def get(self, request):
    user = User.objects.get(id=request.user.id)
    return render(request, 'myapp/profile.html', dict(user=user))
  
  def post(self, request):
    form = ProfileChangeForm(request.POST, instance=request.user)
    if form.is_valid():
      form.save()
      messages.success(request, "Profile Updated Successfully")
      return redirect("profile")
    else:
      return render(request, 'myapp/profile.html', dict(form=form)) 
  

@method_decorator(login_required, name='dispatch')
class EditProfileView(View):
  def get(self, request):
    form = ProfileChangeForm(instance=request.user)
    return render(request, 'myapp/edit-profile.html', dict(form=form))
  
  def post(self, request):
    form = ProfileChangeForm(request.POST, instance=request.user)
    if form.is_valid():
      form.save()
      messages.success(request, "Profile Updated Successfully")
      return redirect("profile")
    else:
      return render(request, 'myapp/edit-profile.html', dict(form=form))
    
class JWTDocs(View):
  def get(self, request):
    data = dict(url=request.build_absolute_uri("/"))
    return render(request, 'myapp/jwtdocs.html', data)
  
def error_404_view(request, exception):
  return render(request, 'myapp/error.html')
