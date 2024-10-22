from django.contrib import admin
from .models import UserProfile , DoctorProfile , AreaProfile , OpdType , District , Appointment , TimeSlot
admin.site.register(UserProfile)
admin.site.register(DoctorProfile)
admin.site.register(AreaProfile)
admin.site.register(OpdType)
admin.site.register(District)
admin.site.register(Appointment)
admin.site.register(TimeSlot)