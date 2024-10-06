# importing basic modules
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.views.generic import TemplateView  
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

# import essential modules for auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import RedirectView

#import models.py




# -----------------------------------------------------------------------------------------------------


#login
class BaseLogin(LoginView):  
    template_name = "base/login.html"  
    fields = ['username', 'password']
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home') 


#logout
class LogoutView(RedirectView):
    url = '/home'  
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)     


#register
class BaseRegister(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(BaseRegister, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super(BaseRegister, self).get(*args, **kwargs)




# --------------------------------------------------------------------------------------------------------
#home page
class BaseHome(TemplateView):
    template_name = "base/home.html"