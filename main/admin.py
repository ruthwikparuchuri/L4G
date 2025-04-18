

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(Country)
admin.site.register(State)
admin.site.register(District)
admin.site.register(Institution)
admin.site.register(Degree)
admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Designation)
admin.site.register(Knowledge_Partner)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Specialization)
admin.site.register(Specialization_Course)
admin.site.register(Program)
admin.site.register(Program_Specialization)
admin.site.register(Program_Requirement)
admin.site.register(Learner)
admin.site.register(Learner_Education)
admin.site.register(Learner_Employment)
admin.site.register(Learner_Program_Requirement)
admin.site.register(Learner_Module_Progress)
admin.site.register(Learner_Course_Progress)
admin.site.register(Learner_Specialization_Progress)
admin.site.register(Learner_Program_Progress)
admin.site.register(Event)
admin.site.register(CollegeVerificationRequest)

