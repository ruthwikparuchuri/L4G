from django import forms
#from django.core.exceptions import ValidationError
from main.models import  Branch, Institution, Country, State, District ,Event, Learner, Learner_Employment, Program
from dashboard.models import Temp_Genai as OL
from datetime import datetime


class LearnerRegistrationForm(forms.Form):
   # Basic Info
   name = forms.CharField(
       max_length=60,
       required=True,
       label='Enter your Name as per Aadhaar',
       widget=forms.TextInput(
           attrs={'class': 'form-control'}))
  
   gender = forms.ChoiceField(
       choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
       required=True,
       widget=forms.Select(attrs={'class': 'form-control'}),
   )
   type = forms.ChoiceField(
       choices=[
           ('student', 'Student'),
           ('faculty', 'Faculty'),
           ('alumni', 'Alumni'),
           ],
       required=True,
       label='Learner Role',
       widget=forms.Select(attrs={'class': 'form-control'}),
   )
   date_of_birth = forms.DateField(
       required=True,
       label='Date of Birth',
       widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
   )
   phone = forms.IntegerField(
       required=True,
       label='Phone number with Whatsapp enabled',
       widget=forms.NumberInput(
           attrs={
               'class': 'form-control',
               'min': '6000000000',
               'max': '9999999999'
               }))
  
   # Academic Info
   college = forms.CharField(
       required=True,
       label='College',
       widget=forms.TextInput(
           attrs={
               'class': 'form-control',
               'id': 'id_student_college'
           }
       ),
   )


   branch = forms.ModelChoiceField( queryset=Branch.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}), )






   rollno = forms.CharField(
       max_length=50,
       required=True,
       label='Rollno',
       widget=forms.TextInput(
           attrs={
               'class': 'form-control',
           }
       ),
   )


   yoj = forms.IntegerField(
       label='Year of Joining',
       required=True,
       widget=forms.NumberInput(
           attrs={
               'class': 'form-control',
               'min': '1980',
               'max': '2027'
           }
       ))
    

   yog = forms.IntegerField(
       label='Year of Graduation',
       required=True,
       widget=forms.NumberInput(
           attrs={
               'class': 'form-control',
               'min': '1980',
               "max": str(datetime.now().year + 4),  # Dynamically set max year
           }
       ))


   #Custom Validation for Roll Number and Email
   # def clean_rollno(self):
   #     rollno = self.cleaned_data.get('rollno')
   #     if le.objects.filter(rollno=rollno).exists():
   #         raise ValidationError("This Roll Number is already registered.")
   #     return rollno
  
   # def clean_email(self):
   #     email = self.cleaned_data.get('email')
   #     if OL.objects.filter(email=email).exists():
   #         raise ValidationError("This Email is already registered.")
   #     return email
  
   # def clean_url(self):
   #     url = self.cleaned_data.get('url')
   #     if OL.objects.filter(url=url).exists():
   #         raise ValidationError("This Email is already registered.")
   #     return url


   #Program Info


   internet = forms.ChoiceField(
       choices=[('yes', 'Yes'), ('no', 'No')],
       required=True,
       label='Do you have access to Internet connectivity and a computer with the latest version of Google Chrome',
       widget=forms.Select(attrs={'class': 'form-control'}),
   )


   account_creation = forms.ChoiceField(
       required=True,
       choices=[('yes', 'Yes, I already have an account'), ('no', 'No, I want to create one')],
       label='Do you have an account on Google Cloud Skills Boost',
       widget=forms.Select(attrs={'class': 'form-control'}),
   )


   email = forms.EmailField(
       required=True,
       label='Cloud Skills Boost linked Email (Gmail)',
       widget=forms.EmailInput(
           attrs={'class': 'form-control'}
       )
   )


   url = forms.URLField(
       required=True,
       label='Cloud Skills Boost Public Profile URL',
       widget=forms.URLInput(
           attrs={'class': 'form-control'}
       )
   )


   feedback = forms.CharField(
       max_length=255,
       #required=True,
       label='Anything that you would like to share with us ?',
       widget=forms.TextInput(attrs={'class': 'form-control'}))


   consent = forms.ChoiceField(
       choices=[('yes', 'I Acknowledge')],
       required=True,
       label='By completing and submitting this form, you declare that the information provided is true and correct to the best of your knowledge',
       widget=forms.Select(attrs={'class': 'form-control'}),
   )


   # Employment Info


   # empid = forms.CharField(
   #     max_length=50,
   #     label='Employee ID',
   #     widget=forms.TextInput(attrs={'class': 'form-control'}),
   # )


   # faculty_college = forms.CharField(
   #     widget=forms.TextInput(
   #         attrs={
   #             'class': 'form-control',
   #             'id': 'id_faculty_college'
   #         }
   #     ),
   # )


   # department = forms.ModelChoiceField(
   #     queryset=Department.objects.all(),
   #     widget=forms.Select(attrs={'class': 'form-control'}),
   # )


   # designation = forms.ModelChoiceField(
   #     queryset=Designation.objects.all(),
   #     widget=forms.Select(attrs={'class': 'form-control'}),
   # )



# CollegeVerificationRequestForm
class InstitutionForm(forms.ModelForm):
    
    country_code = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'country-dropdown'})
    )
    
    state_code = forms.ModelChoiceField(
        queryset=State.objects.none(),  
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'state-dropdown'})
    )

    district_code = forms.ModelChoiceField(
        queryset=District.objects.none(), 
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'district-dropdown'})
    )


    class Meta:
        model = Institution
        fields = [
            'name', 'short_name', 'aicte_code', 'eamcet_code', 'l4g_code',
            'l4g_group_code','type', 'address', 'website', 'latlong', 'district_code'
        ] 

    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)
        if 'country_code' in self.data:
            try:
                country_id = int(self.data.get('country_code'))
                self.fields['state_code'].queryset = State.objects.filter(country_code=country_id)
            except (ValueError, TypeError):
                pass
        if 'state_code' in self.data:
            try:
                state_id = int(self.data.get('state_code'))
                self.fields['district_code'].queryset = District.objects.filter(state_code=state_id)
            except (ValueError, TypeError):
                pass




SECTION_CHOICES = [('', 'Select Section')] + [(chr(i), chr(i)) for i in range(ord('A'), ord('K'))]  # A to J


class GeminiWorkshopRegistrationForm(forms.Form):
    # Basic Info
    name = forms.CharField(
        max_length=60,
        required=True,
        label='Enter your Name as per Aadhaar',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    date_of_birth = forms.DateField(
        required=True,
        label='Date of Birth',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    phone = forms.IntegerField(
        required=True,
        label='Phone number ',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '6000000000', 'max': '9999999999'})
    )

    # Academic Info
    college = forms.CharField(
        required=True,
        label='College',
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_student_college'}),
    )

    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    rollno = forms.CharField(
        max_length=50,
        required=True,
        label='Roll Number',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    section = forms.ChoiceField(
        choices=SECTION_CHOICES,
        required=True,
        label="Section",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    yoj = forms.IntegerField(
        label='Year of Joining',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1980', 'max': '2027'})
    )

    yog = forms.IntegerField(
        label='Year of Graduation',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1980', "max": "2030"})  # Dynamically set max
    )

    # Program Info
    internet = forms.ChoiceField(
        choices=[('yes', 'Yes'), ('no', 'No')],
        required=True,
        label='Do you have access to Internet and a computer with the latest version of Google Chrome?',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    email = forms.EmailField(
        required=True,
        label='Email (in the format xxxxxxx.ai@gmail.com) ',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )


    consent = forms.ChoiceField(
        choices=[('yes', 'I Acknowledge')],
        required=True,
        label='By submitting this form, you confirm that the information provided is correct.',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    url = forms.URLField(
       required=False,
       label='Cloud Skills Boost Public Profile URL',
       widget=forms.URLInput(
           attrs={'class': 'form-control'}
       )
   )
    developer_url = forms.URLField(
       required=True,
       label='Google Developer Public Profile URL',
       widget=forms.URLInput(
           attrs={'class': 'form-control'}
       )
   )
    event = forms.ModelChoiceField(
        queryset=Event.objects.none(),  
        required=True,
        label='Select Event',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_event'}),
    )

    def clean_college(self):
        """Convert institution name to Institution instance before saving."""
        college_name = self.cleaned_data.get("college").strip()
        college = Institution.objects.get(name=college_name)

        if not college:
            raise forms.ValidationError("No college found with this name.")

        return college 

    def __init__(self, *args, **kwargs):
        college_name = kwargs.pop("college_name", None)  
        super().__init__(*args, **kwargs)

        if college_name:  
            institution = Institution.objects.filter(name=college_name).first()
            if institution:
                self.fields["event"].queryset = Event.objects.filter(institution=institution, event_status="Ongoing")

    def clean_event(self):
        """Validate event based on event ID."""
        event = self.cleaned_data.get("event")

        if not event:
            raise forms.ValidationError("Invalid event selected.")

        return event
    
    def __init__(self, *args, **kwargs):
        college_name = kwargs.pop('college_name', None)  
        super().__init__(*args, **kwargs)

        if college_name:
            self.fields['event'].queryset = Event.objects.filter(institution__name=college_name)


    
    


class EventForm(forms.ModelForm):
    trainers = forms.ModelMultipleChoiceField(
        queryset=Learner_Employment.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Trainers (Learner Employment)",
    )
    institution= forms.CharField(
        required=True,
        label='Institution',
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_institution'})
    )

    
    class Meta:
        model = Event
        fields = ['event_name', 'datetime', 'event_url', 'institution', 'venue', 'trainers', 'info']
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Name'}),
            'datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'event_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Event URL'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue'}),
            'info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Event Information'}),
        }
    
    def clean_institution(self):
        """Convert institution name to Institution instance before saving."""
        institution_name = self.cleaned_data.get("institution").strip()
        institution = Institution.objects.get(name=institution_name)

        if not institution:
            raise forms.ValidationError("No institution found with this name.")

        return institution 
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.program_code = Program.objects.get(id=3) # Actual program code to be used
        if commit:
            instance.save()
            self.save_m2m()
        return instance



class LearnerEmploymentForm(forms.ModelForm):
    learner_code = forms.CharField(
        required=True,
        label='Learner',
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_learner'})
    )

    institution_code = forms.CharField(
        required=True,
        label='Institution',
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_institution'})
    )

    class Meta:
        model = Learner_Employment
        fields = ['empid', 'year_of_joining', 'learner_code', 'institution_code', 'department_code', 'designation_code']

        widgets = {
            'empid': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_emp_id', 'placeholder': 'Enter Employee ID'}),
            'year_of_joining': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_year_of_joining'}),
            'department_code': forms.Select(attrs={'class': 'form-control', 'id': 'id_department_code'}),
            'designation_code': forms.Select(attrs={'class': 'form-control', 'id': 'id_designation_code'}),
        }

    def clean_learner_code(self):
        """Convert email to Learner instance before saving."""
        email = self.cleaned_data.get("learner_code").strip()
        learner = Learner.objects.get(email=email)

        if not learner:
            raise forms.ValidationError("No learner found with this email.")

        return learner 

    def clean_institution_code(self):
        """Convert institution name to Institution instance before saving."""
        institution_name = self.cleaned_data.get("institution_code").strip()
        institution = Institution.objects.get(name=institution_name)

        if not institution:
            raise forms.ValidationError("No institution found with this name.")

        return institution 