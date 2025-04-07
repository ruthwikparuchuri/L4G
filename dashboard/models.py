from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Branch(models.Model):
   name = models.CharField(max_length=150, default='', unique=True)
   short_name = models.CharField(max_length=9, default='', unique=True)
   #code = models.IntegerField()
   #institution_type_code = models.ForeignKey(Type_Of_Institution, on_delete=models.CASCADE)
   #degree_code = models.ForeignKey(Degree, on_delete=models.PROTECT, default=1) #Defaults to B.tech


   def __str__(self):
       return f'{self.id} - {self.name} - {self.short_name}'


class UserProfile(models.Model):
   # ROLE_CHOICES = [
   #     ('all_access', 'All Access'),
   #     ('department', 'Department')
   # ]
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   is_admin = models.BooleanField(default=False)
   college = models.CharField(max_length=225)
   role = models.ForeignKey(Branch, on_delete=models.PROTECT, default=24)
  
   def __str__(self):
       return self.user.username


class Temp_Genai_Institutions(models.Model):
   name = models.CharField(max_length=150, default='')
   enrollments = models.IntegerField(default=0)
   onboarded = models.IntegerField(default=0)
   active = models.IntegerField(default=0)
   pending = models.IntegerField(default=0)
   revoked = models.IntegerField(default=0)
   declined = models.IntegerField(default=0)
   completions = models.IntegerField(default=0)
   beginner_completions = models.IntegerField(default=0)
   intermediate_completions = models.IntegerField(default=0)
   advanced_completions = models.IntegerField(default=0)
   digital_badges = models.IntegerField(default=0)
   completions_ratio = models.IntegerField(default=0)


   def __str__(self):
       return f'{self.name}'
  
class Temp_Genai(models.Model):
   gender_choices = [
       ('M', 'Male'),
       ('F', 'Female'),
       ('O', 'Other')
   ]
   consent_choices = [
       ('Y', 'Yes'),
       ('N', 'No')
   ]
   type_choices = [
       ('student', 'Student'),
       ('faculty', 'Faculty'),
       # ('A', 'Unemployed'),
       # ('E', 'Employed')
   ]
   name = models.CharField(max_length=150, default='')
   type = models.CharField(max_length=15, choices=type_choices, default='student')
   rollno = models.CharField(max_length=21, null=True, blank=True)
   gender = models.CharField(max_length=1, choices=gender_choices, default='O')
   consent = models.CharField(max_length=1, choices=consent_choices, default='Y')
   email = models.EmailField(unique=True, default='')
   aadhaar_number = models.CharField(max_length=15, null=True, blank=True)
   mobile = models.CharField(max_length=15, null=True, blank=True)
   #college_code = models.ForeignKey(Institution, on_delete=models.PROTECT, default=2)
   college = models.CharField(max_length=225, null=True, blank=True)
   branch_code = models.ForeignKey(Branch, on_delete=models.PROTECT, default=17)
   branch_other = models.CharField(max_length=150, null=True, blank=True)
   year_of_joining = models.IntegerField(null=True, blank=True)
   lateral_entry = models.BooleanField(default=False)
   section = models.CharField(max_length=4, null=True, blank=True)
   employee_id = models.CharField(max_length=21, null=True, blank=True)
   department = models.CharField(max_length=150, null=True, blank=True)
   designation_other = models.CharField(max_length=150, null=True, blank=True)
   url = models.URLField(max_length=225, null=True, blank=True)
   timestamp = models.CharField(max_length=24, null=True, blank=True)
   beginner_count = models.IntegerField(default=0)
   beginner_badges = models.CharField(max_length=225, null=True, blank=True)
   beginner_status = models.CharField(max_length=3, null=True, blank=True)
   intermediate_count = models.IntegerField(default=0)
   intermediate_badges = models.CharField(max_length=300, null=True, blank=True)
   intermediate_status = models.CharField(max_length=3, null=True, blank=True)
   advanced_count = models.IntegerField(default=0)
   advanced_badges = models.CharField(max_length=465, null=True, blank=True)
   advanced_status = models.CharField(max_length=3, null=True, blank=True)
   enrollment_status = models.CharField(max_length=15, null=True, blank=True)
   completion_status = models.CharField(max_length=15, null=True, blank=True)
   is_deleted = models.BooleanField(default=False)


   def __str__(self):
       return f'{self.name} - {self.type}'

