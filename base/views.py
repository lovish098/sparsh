# importing basic modules
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.views.generic import TemplateView  
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import RedirectView
from django.views import View
from django.contrib import messages
from django import forms
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# import essential modules for auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


#import models.py
from base.models import *
# -----------------------------------------------------------------------------------------------------



class RegionalDoctorProfileView(LoginRequiredMixin, DetailView):
    model = DoctorProfile
    template_name = 'dashboard/rdoctor_profile.html'
    context_object_name = 'doctor_profile'

    def get_object(self):
        # Get the doctor's profile based on the URL parameter (primary key)
        return DoctorProfile.objects.get(pk=self.kwargs['pk'])


# -----------------------------------------------------------------------------------------------------

class RegionalPatientProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'dashboard/rpatient_profile.html'
    context_object_name = 'patient_profile'

    def get_object(self):
        # Get the patient's profile based on the URL parameter (primary key)
        return UserProfile.objects.get(pk=self.kwargs['pk'])


# -----------------------------------------------------------------------------------------------------

# dash board for area /regional

class BaseAreaDashboard(LoginRequiredMixin, TemplateView):

    template_name = 'dashboard/rdashboard.html'

    model = AreaProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        area_profile = AreaProfile.objects.filter(user=self.request.user).first()
               
        doctor_profile = DoctorProfile.objects.all()
        user_profile = UserProfile.objects.all()

        # Add to context
        context['area_profile'] = area_profile
        context['doctor_profile'] = doctor_profile
        context['user_profile'] =user_profile

        return context


   


# -----------------------------------------------------------------------------------------------------
#update / add basic details of area
class AreaProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['uname','uaddress','image','opd_type','district']


class BaseAreaUpdateProfile(UpdateView):
    template_name = "profile/ruprofile.html"
    model = AreaProfile
    form_class = AreaProfileForm  
    success_url = reverse_lazy('rprofile') 

    def get_queryset(self):
        return AreaProfile.objects.all()

    def get_object(self, queryset=None):
        username = self.kwargs.get('uname')
        return get_object_or_404(AreaProfile, uname=username)

    def get_initial(self):
        initial = super().get_initial()
        area_profile = self.get_object()
        initial['uname'] = area_profile.uname
        initial['uaddress'] = area_profile.uaddress
        initial['image'] = area_profile.image
        # Set the initially selected opd_types
        initial['opd_types'] = area_profile.opd_types.all()  
        initial['district'] = area_profile.district
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the available OPD types to the context
        context['opd_types'] = OpdType.objects.all()  # Fetch all OPD types
        return context


#Area  profile page
class BaseAreaProfile(DetailView):
    model = AreaProfile
    template_name = "profile/regionalprofile.html"
    context_object_name = 'area_profile'

    def get_object(self, queryset=None):
        return AreaProfile.objects.filter(user=self.request.user).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opd_types'] = OpdType.objects.all()  
        return context    


# -----------------------------------------------------------------------------------------------------


class BaseDoctorDashboard(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'dashboard/ddashboard.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        # Get the doctor profile of the logged-in user
        doctor_profile = DoctorProfile.objects.get(user=self.request.user)
        
        # Fetch appointments based on doctor's OPD type
        return Appointment.objects.filter(opd_type=doctor_profile.opd_type).select_related('user_profile', 'time_slot')
    
    def get_context_data(self, **kwargs):
        # Add the doctor profile to the context
        context = super().get_context_data(**kwargs)
        context['doctor_profile'] = DoctorProfile.objects.get(user=self.request.user)
        return context


class PatientProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'dashboard/patient_profile.html'
    context_object_name = 'patient_profile'

    def get_object(self):
        # Get the patient's profile based on the URL parameter (primary key)
        return UserProfile.objects.get(pk=self.kwargs['pk'])


class CancelAppointmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
      
        appointment = get_object_or_404(Appointment, pk=pk)
        
        # Check if the logged-in user is the doctor of this appointment's OPD type
        doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
        if appointment.opd_type != doctor_profile.opd_type:
            messages.error(request, "You are not authorized to cancel this appointment.")
            return redirect(reverse('doctor_dashboard'))

        # Mark the appointment as canceled
        appointment.appointment_status = 'C'
        appointment.save()

       
        appointment.delete()

        # # Send an email to the patient informing them of the cancellation
        # if appointment.user_profile.uemail:  # Check if the patient has an email
        #     subject = "Appointment Cancellation Notification"
        #     message = f"Dear {appointment.user_profile.uname},\n\nYour appointment (ID: {appointment.appointment_id}) scheduled for {appointment.time_slot} has been canceled. Please contact us if you need further assistance.\n\nRegards,\nThe Medical Team"
        #     recipient_list = [appointment.user_profile.uemail]
        #     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

        # Show a success message and redirect the doctor back to the dashboard
        messages.success(request, "The appointment has been canceled and the patient has been notified.")
        return redirect('ddashboard')

# -----------------------------------------------------------------------------------------------------


def get_available_slots(request, session):
    # Validate session input
    if session not in ['M', 'E']:  # Assuming 'M' for Morning and 'E' for Evening
        return JsonResponse({'error': 'Invalid session type'}, status=400)

    # Query available slots (pending slots) for the given session
    available_slots = TimeSlot.objects.filter(session=session, status='P')  # Changed to 'P' for Pending
    
    # Prepare the data to send as JSON
    slots_data = []
    for slot in available_slots:
        slots_data.append({
            'id': slot.id,
            'time': slot.time.strftime('%H:%M'),  # Format time as 'HH:MM'
            'status': slot.get_status_display(),
            'session': slot.get_session_display()  # Get human-readable session
        })
    
    # Return the JSON response
    return JsonResponse({'slots': slots_data})



# -----------------------------------------------------------------------------------------------------


class BaseAppointment(TemplateView):
    model = UserProfile
    template_name = "appointment/bookappointment.html"
    context_object_name = 'user_profile'

    # form_class = AppointmentForm
    success_url = reverse_lazy('home') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the UserProfile for the logged-in user
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        context[self.context_object_name] = user_profile

        # Fetch the related AreaProfile
        area_profile = AreaProfile.objects.filter(user=user_profile.user).first() if user_profile else None
        context['area_profile'] = area_profile

        # Fetch all OPD types and pass them to the context
        context['opd_types'] = OpdType.objects.all()

         # Fetch all districts and pass them to the context
        context['district'] = District.objects.all()


        morning_slots = TimeSlot.get_available_slots('M')  
        evening_slots = TimeSlot.get_available_slots('E') 
      
        context['morning_slots'] = morning_slots
        context['evening_slots'] = evening_slots

        return context

    def post(self, request, *args, **kwargs):
       
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        
       
        opd_type_id = request.POST.get('opd')  
        time_slot_id = request.POST.get('time_slot') 
        
        if not user_profile:
            messages.error(request, "User profile not found.")
            return redirect('home')
        
       
        opd_type = OpdType.objects.filter(id=opd_type_id).first()
        time_slot = TimeSlot.objects.filter(id=time_slot_id, status='A').first()  

        if not opd_type:
            messages.error(request, "Invalid OPD type selected.")
            return redirect('home')

        if not time_slot:
            messages.error(request, "Selected time slot is not available.")
            return redirect('home')

      
        appointment = Appointment.objects.create(
            user_profile=user_profile,
            opd_type=opd_type,
            appointment_status='B', 
            time_slot=time_slot
        )

       
        time_slot.status = 'B'
        time_slot.save()

        messages.success(request, "Appointment booked successfully.")
        return redirect('home')


        





# -----------------------------------------------------------------------------------------------------

#Doctor  profile page
class BaseDoctorProfile(DetailView):
    model = DoctorProfile
    template_name = "profile/doctorprofile.html"
    context_object_name = 'doctor_profile'

    def get_object(self, queryset=None):
        return DoctorProfile.objects.filter(user=self.request.user).first()
      
# -----------------------------------------------------------------------------------------------------
#update / add basic details of doctor
class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['uname', 'umobile', 'uemail', 'uaddress', 'gender', 'age', 'date_of_birth', 'uaadhar', 'image', 'area_profile','opd_type','district']

class BaseDoctorUpdateProfile(UpdateView):
    template_name = "profile/duprofile.html"
    model = DoctorProfile
    form_class = DoctorProfileForm  
    success_url = reverse_lazy('dprofile') 

    def get_queryset(self):
        
        return DoctorProfile.objects.all()

    def get_object(self, queryset=None):
        
        username = self.kwargs.get('uname')
       
        return get_object_or_404(DoctorProfile, uname=username)

    def form_valid(self, form):
        
        if form.cleaned_data['gender'] == '':
            form.instance.gender = None  
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        doctor_profile = self.get_object()
        initial['uname'] = doctor_profile.uname
        initial['umobile'] = doctor_profile.umobile
        initial['uemail'] = doctor_profile.uemail
        initial['uaddress'] = doctor_profile.uaddress
        initial['gender'] = doctor_profile.gender
        initial['age'] = doctor_profile.age
        initial['date_of_birth'] =doctor_profile.date_of_birth
        initial['uaadhar'] = doctor_profile.uaadhar
        initial['image'] = doctor_profile.image
        initial['area_profile'] = doctor_profile.area_profile
        initial['opd_type'] = doctor_profile.opd_type
        initial['district'] = doctor_profile.district

        return initial


# -----------------------------------------------------------------------------------------------------
#update / add basic details of user
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['uname', 'umobile', 'uemail', 'uaddress', 'gender', 'age', 'date_of_birth', 'uaadhar', 'image', 'area_profile','district']

class BaseUserUpdateProfile(UpdateView):
    template_name = "profile/uuprofile.html"
    model = UserProfile
    form_class = UserProfileForm  
    success_url = reverse_lazy('uprofile')  

    def get_queryset(self):
       
        return UserProfile.objects.all()

    def get_object(self, queryset=None):
      
        username = self.kwargs.get('uname')
       
        return get_object_or_404(UserProfile, uname=username)

    def form_valid(self, form):
       
        if form.cleaned_data['gender'] == '':
            form.instance.gender = None  
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        user_profile = self.get_object()
        initial['uname'] = user_profile.uname
        initial['umobile'] = user_profile.umobile
        initial['uemail'] = user_profile.uemail
        initial['uaddress'] = user_profile.uaddress
        initial['gender'] = user_profile.gender
        initial['age'] = user_profile.age
        initial['date_of_birth'] = user_profile.date_of_birth
        initial['uaadhar'] = user_profile.uaadhar
        initial['image'] = user_profile.image
        initial['area_profile'] = user_profile.area_profile
        initial['district'] = user_profile.district

        return initial
# -----------------------------------------------------------------------------------------------------

#user profile page
class BaseUserProfile(DetailView):
    model = UserProfile
    template_name = "profile/userprofile.html"
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        return UserProfile.objects.filter(user=self.request.user).first()


# -----------------------------------------------------------------------------------------------------

#contact us  
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

class BaseContactUs(FormView):
    template_name = "base/contactus.html"
    form_class = ContactForm  
    success_url = reverse_lazy('contactus')  

    def form_valid(self, form):
        name = form.cleaned_data['name']
        mobile = form.cleaned_data['mobile']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        full_message = f"name : {name} \n email : {email} \n mobile : {mobile} \n\n message : {message}"

        send_mail(
            subject,
            full_message,
            email,
            ['chamruoraon1403@gmail.com'], 
            fail_silently=False,
        )

        messages.success(self.request, "Message sent successfully.")
        return super().form_valid(form)
   
# -----------------------------------------------------------------------------------------------------

#help us 
class BaseHelp(TemplateView):
    template_name = "base/help.html"

# -----------------------------------------------------------------------------------------------------

#about us page
class BaseAboutus(TemplateView):
    template_name = "base/aboutus.html"

# -----------------------------------------------------------------------------------------------------

# Regional register

class BaseRegionalRegister(TemplateView):
    template_name = 'reguser/regionalregistration.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({}) 

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the passwords
        if password != confirm_password:
            return self.render_to_response({'error': "Passwords do not match."})

        # Create the user
        user = User(username=username)
        user.set_password(password) 
        user.save() 
       
        user_group, created = Group.objects.get_or_create(name='area')
        user.groups.add(user_group)
        
        # Create a UserProfile for new user
        AreaProfile.objects.create(user=user,uname=user) 
        

        messages.success(request, "Registration successful! You can now log in.") 
        return redirect('home') 

        
        
    

# -----------------------------------------------------------------------------------------------------

# #Regional login 
class BaseRegionalLogin(LoginView):
    template_name = "login/regionallogin.html"
    redirect_authenticated_user = False 

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form) 

    def get_success_url(self):
        return reverse_lazy('home')
    


# -----------------------------------------------------------------------------------------------------

# Doctor register

class BaseDoctorRegister(TemplateView):
    template_name = 'reguser/doctorregistration.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({}) 

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the passwords
        if password != confirm_password:
            return self.render_to_response({'error': "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists in database.")
            return redirect('dregister')    

        # Create the user
        user = User(username=username)
        user.set_password(password) 
        user.save() 
       
        user_group, created = Group.objects.get_or_create(name='doctor')
        user.groups.add(user_group)
        
        # Create a UserProfile for new user
        DoctorProfile.objects.create(user=user,uname=user) 

        messages.success(request, "Registration successful! You can now log in.")        
        return redirect('home') 
        
    

# -----------------------------------------------------------------------------------------------------

# #Doctor login 
class BaseDoctorLogin(LoginView):
    template_name = "login/doctorlogin.html"
    redirect_authenticated_user = False 

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form) 

    def get_success_url(self):
        return reverse_lazy('home')
    

# -----------------------------------------------------------------------------------------------------

# user register

class BaseUserRegister(TemplateView):
    template_name = 'reguser/userregistration.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({}) 

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the passwords
        if password != confirm_password:
            return self.render_to_response({'error': "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists in database.")
            return redirect('uregister')    

        # Create the user
        user = User(username=username)
        user.set_password(password) 
        user.save() 
       
        user_group, created = Group.objects.get_or_create(name='user')
        user.groups.add(user_group)
        
        # Create a UserProfile for new user
        UserProfile.objects.create(user=user,uname=user)

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('home')
        
    

# -----------------------------------------------------------------------------------------------------

#user login 
class BaseUserLogin(LoginView):
    template_name = "login/userlogin.html"
    redirect_authenticated_user = False 

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form) 

    def get_success_url(self):
        return reverse_lazy('home')
    
# -----------------------------------------------------------------------------------------------------


#logout for all user 
class LogoutView(RedirectView):
    url = '/home'  
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)     


# --------------------------------------------------------------------------------------------------------
#home 
class BaseHome(TemplateView):
    template_name = "base/home.html"