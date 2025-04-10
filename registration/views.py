from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.http import JsonResponse
from .forms import LearnerRegistrationForm, InstitutionForm, GeminiWorkshopRegistrationForm, EventForm, LearnerEmploymentForm
from main.models import Institution as ins, Learner as l, Learner_Education as le, Learner_Program_Requirement as lpr, Program_Requirement as pr, Branch, Learner
from main.models import Program,CollegeVerificationRequest, Country, State, District, Learner_Employment , Learner_Education , Institution, Event
from dashboard.models import Temp_Genai as ol
import re
from datetime import datetime as dt
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.core.files.storage import default_storage
import json
import base64
import requests
from django.utils import timezone





# Create your views here.





def learner_registration(request):
    if request.method == 'POST':
        form = LearnerRegistrationForm(request.POST)
        if form.is_valid():
            # Extract form data
            name = form.cleaned_data['name']
            gender = form.cleaned_data['gender']
            dob = form.cleaned_data['date_of_birth']
            phone = form.cleaned_data['phone']
            college = form.cleaned_data['college']

            branch = form.cleaned_data['branch']
            branch = Branch.objects.get(name=branch)

            rollno = form.cleaned_data['rollno']
            yoj = form.cleaned_data['yoj']
            yog = form.cleaned_data['yog']
            internet = form.cleaned_data['internet']
            email = form.cleaned_data['email']
            url = form.cleaned_data['url']
            feedback = form.cleaned_data['feedback'] if form.cleaned_data['feedback'] else ''
            consent = form.cleaned_data['consent']

            # Check if the user selected "Other" for college
            if college.lower() == "other":
                new_college = request.POST.get("new_college", "").strip()

                # Store data in CollegeVerificationRequest model
                temporary_learner_data = {
                    "name": name,
                    "gender": gender,
                    "date_of_birth": str(dob),
                    "phone": phone,
                    "college": new_college,
                    "branch": branch.name,
                    "rollno": rollno.upper(),
                    "year_of_joining": yoj,
                    "year_of_graduation": yog,
                    "internet": internet,
                    "email": email,
                    "url": url,
                    "feedback": feedback,
                    "consent": consent,
                    "timestamp": dt.now().strftime('%Y/%m/%d %H:%M:%S'),
                    "verified": False  # Mark as unverified
                }

                # Save in CollegeVerificationRequest
                CollegeVerificationRequest.objects.create(
                    data=temporary_learner_data,
                    new_institution=new_college,
                    mobile=phone,
                    approved=False  # Mark as unapproved
                )

                messages.success(request, "Your registration is pending verification.")
                return redirect("registration:registration_success" , status="under_review")

            else:
                # Existing logic when college is NOT "Other"
                
                college = ins.objects.get(name=college)

                learner = l.objects.create(
                email=email,
                name = name,
                mobile = phone,
                gender = gender,
                date_of_birth = dob,
                )
            


                le.objects.create(
                    rollno = str(rollno).upper(),
                    year_of_joining = yoj,
                    year_of_graduation = yog,
                    learner_code = learner,
                    institution_code = college,
                    branch_code = branch
                )


                # program = Program.objects.get(id=2)
                pr1 = pr.objects.get(id=1)
                pr2 = pr.objects.get(id=2)
                pr3 = pr.objects.get(id=3)
                pr4 = pr.objects.get(id=4)
                pr5 = pr.objects.get(id=5)
                pr6 = pr.objects.get(id=6)


                
                lpr.objects.create(
                    learner_code = learner,
                    program_requirement_code = pr1,
                    value = internet
                )
                lpr.objects.create(
                    learner_code = learner,
                    program_requirement_code = pr2,
                    value = email
                )
                lpr.objects.create(
                    learner_code = learner,
                    program_requirement_code = pr3,
                    value = url
                )
                lpr.objects.create(
                    learner_code = learner,
                    program_requirement_code = pr4,
                    value = feedback
                )
                lpr.objects.create(
                    learner_code = learner,
                    program_requirement_code = pr5,
                    value = consent
                )
                timestamp = dt.now()
                #convert datetime object to string in the format '%Y/%m/%d %H:%M:%S'
                timestamp_s = timestamp.strftime('%Y/%m/%d %H:%M:%S')


                lpr.objects.create(
                    learner_code = learner,
                    program_requirement_code = pr6,
                    value = timestamp_s
                )

                return redirect("registration:registration_success" , status="approved")  # Redirect to a success page

        else:
            messages.error(request, "There were errors in your form. Please check and fix them.")
            return render(request, 'registration/genai2025.html', {'form': form})

    else:
        form = LearnerRegistrationForm()

    return render(request, 'registration/genai2025.html', {'form': form})



def registration_success(request, status):
   return render(request, 'registration/registrationSuccess.html', {"status": status} )
   


def validate_rollno(request):
    rollno = request.GET.get('rollno', '').upper()
    college = request.GET.get('college', '')
    
    # Check if roll number is already taken
    is_taken = le.objects.filter(rollno=rollno).exists() or ol.objects.filter(rollno=rollno).exists()

    # Validate roll number format based on the college
    is_valid_format = get_branch(rollno, college)

    return JsonResponse({
        'is_taken': is_taken,
        'is_valid_format': is_valid_format
    })


def get_branch(rollno, college):
    if college == 'Vasireddy Venkatadri Institute of Technology':
        branches = {'01': 6, '02': 4, '03': 5, '04': 3, '05': 1, '12': 2, '42': 7, '43': 9, '47': 11, '49': 12, '54': 15, '61': 14}
        try:
            if len(rollno) == 10 and rollno[0:2].isnumeric() and rollno[6:8] in branches and rollno[2:4] == 'BQ':
                return True
            else:
                return False
        except:
            return False
    return True  # Default to True for other colleges unless more rules are added


def validate_email(request):
   email = request.GET.get('email', None)
   is_taken = ol.objects.filter(email=str(email).lower()).exists() or l.objects.filter(email=str(email).lower()).exists()
   pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
   if re.fullmatch(pattern, str(email)):
       is_valid = True
   else:
       is_valid = False
   return JsonResponse({'is_taken': is_taken, 'is_valid': is_valid})


def validate_url(request):
   url = request.GET.get('url', None)
   pr_code = pr.objects.get(id=15)
   is_taken = ol.objects.filter(url=url).exists() or lpr.objects.filter(program_requirement_code=pr_code).filter(value=url).exists()
   pattern = r"^https:\/\/www\.cloudskillsboost\.google\/public_profiles\/[a-z0-9\-]{36}$"

   invalid_url = "https://www.cloudskillsboost.google/public_profiles/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"


   if re.fullmatch(pattern, str(url)) and url != invalid_url:
       is_valid = True
   else:
       is_valid = False
   return JsonResponse({'is_taken': is_taken, 'is_valid': is_valid})


def validate_developer_url(request):
    url = request.GET.get('url', None)
    pr_code = pr.objects.get(id=16)  # Program requirement for developer URL

    # Check if the URL already exists
    is_taken = (
        ol.objects.filter(url=url).exists() or
        lpr.objects.filter(program_requirement_code=pr_code).filter(value=url).exists()
    )

    # Regex pattern for Google Developer profile
    pattern = r"^https:\/\/developers\.google\.com\/profile\/u\/\d+$"

    # Specific invalid dummy URL
    invalid_url = "https://developers.google.com/profile/u/xxxxxxxxx"

    # Final validation
    if re.fullmatch(pattern, str(url)) and url != invalid_url:
        is_valid = True
    else:
        is_valid = False

    return JsonResponse({'is_taken': is_taken, 'is_valid': is_valid})



def autocomplete_college(request):
   if 'term' in request.GET:
       query = request.GET.get('term')
       colleges = ins.objects.filter(name__icontains=query).values_list('name', flat=True)
       return JsonResponse(list(colleges), safe=False)
   return JsonResponse([], safe=False)


def validate_college(request):
    query = request.GET.get("term", "").strip()
    exists = ins.objects.filter(name__iexact=query).exists()  # Case-insensitive
    return JsonResponse({"exists": exists})


def test(request):
   #return HttpResponse('Test')
   ctx = {}
   return render(request, 'registration/test.html', ctx)


# '''
# 1. Check and validate rollno, email and url from old learners and new learners. Display error message in form instead of an alert
# 2. Prevent form submission on client side using javascript unless all mandatory fields are entered
# 3. Store all form data into database
# '''


# ^https:\/\/www\.cloudskillsboost\.google\/public_profiles\/[a-z0-9\-]{36}$


#Faculty Info eliminated
# <div>
#             <fieldset>
#                 <legend><h3>Faculty Information (optional)</h3></legend>
#                 {{ form.empid.label_tag }} {{ form.empid }}
#                 {{ form.faculty_college.label_tag }} {{ form.faculty_college }}
#                 {{ form.department.label_tag }} {{ form.department }}
#                 {{ form.designation.label_tag }} {{ form.designation }}
#             </fieldset>
#         </div>


# New Institution Adding
def add_institution(request):
    form = InstitutionForm()  

    if request.method == "POST":
        form = InstitutionForm(request.POST)
        if form.is_valid():
            form.save() 
            request.session['show_success'] = True  
            return redirect("registration:add_institution")
        else:
            messages.error(request, "Error adding institution. Please check the details.")

    show_success = request.session.pop('show_success', False)

    return render(
        request,
        "registration/addNewInstitution.html",
        {
            "form": form,
            "countries": Country.objects.all().order_by("name"),
            "success": show_success,
        },
    )


# Load states based on country 
def load_states(request):
    country_id = request.GET.get("country_id")
    states = State.objects.filter(country_code_id=country_id).order_by("name").values("id", "name") 
    return JsonResponse(list(states), safe=False)

# Load districts based on state
def load_districts(request):
    state_id = request.GET.get("state_id")
    districts = District.objects.filter(state_code_id=state_id).order_by("name").values("id", "name")  
    return JsonResponse(list(districts), safe=False)



def temporary_learners(request):
    verification_requests = CollegeVerificationRequest.objects.filter(approved=False)
    institutions = ins.objects.values_list('name', flat=True)  # Get institution names

    return render(request, 'registration/registerTemporaryLearnerToPermanent.html', {
        'verification_requests': verification_requests,
        'institutions': list(institutions),  # Convert to list for JavaScript
    })


def get_approved_students(request):
    students = CollegeVerificationRequest.objects.filter(approved=True)
    student_list = [
        {
            'name': student.data.get('name', 'Unknown'),  
            'phone': student.mobile,
            'college': student.new_institution
        }
        for student in students
    ]
    return JsonResponse({'students': student_list})



def approve_learner(request):
    if request.method == "POST":
        verification_id = request.POST.get("verification_id")
        assigned_college = request.POST.get("assigned_college")

        verification_request = get_object_or_404(CollegeVerificationRequest, id=verification_id)

        if verification_request.approved:
            return JsonResponse({"error": "This request is already approved."}, status=400)

        try:
            college = ins.objects.get(name=assigned_college)
        except ins.DoesNotExist:
            return JsonResponse({"error": "Selected college does not exist."}, status=400)

        # Extract data from JSONField
        data = verification_request.data
        name = data.get("name")
        gender = data.get("gender")
        dob = data.get("date_of_birth")
        phone = data.get("phone")
        branch_name = data.get("branch")
        rollno = str(data.get("rollno")).upper()
        yoj = data.get("year_of_joining")
        yog = data.get("year_of_graduation")
        internet = data.get("internet")
        email = data.get("email")
        url = data.get("url")  
        feedback = data.get("feedback", "")
        consent = data.get("consent")

        try:
            branch = Branch.objects.get(name=branch_name)
        except Branch.DoesNotExist:
            return JsonResponse({"error": "Invalid branch selected."}, status=400)

        # Check for existing records
        existing_learner_email = l.objects.filter(email=email).exists()
        existing_learner_rollno = le.objects.filter(rollno=rollno).exists()
        existing_learner_url = lpr.objects.filter(value=url).exists()

        duplicate_fields = []
        if existing_learner_email:
            duplicate_fields.append("Email")
        if existing_learner_rollno:
            duplicate_fields.append("Roll Number")
        if existing_learner_url:
            duplicate_fields.append("Cloud Skills Boost Public Profile URL")

        if duplicate_fields:
            duplicate_fields_str = ", ".join(duplicate_fields)
            return JsonResponse({
                "error": f"User already exists with the following fields: {duplicate_fields_str}. Please confirm to proceed."
            }, status=400)

        # Create Learner Entry
        learner = l.objects.create(
            email=email,
            name=name,
            mobile=phone,
            gender=gender,
            date_of_birth=dob,
        )

        # Create Learner Education Entry
        le.objects.create(
            rollno=rollno,
            year_of_joining=yoj,
            year_of_graduation=yog,
            learner_code=learner,
            institution_code=college,
            branch_code=branch
        )

        # Assign program requirements
        program_requirements = {
            1: internet,
            2: email,
            3: url,
            4: feedback,
            5: consent,
            6: dt.now().strftime('%Y/%m/%d %H:%M:%S')
        }

        for pr_id, value in program_requirements.items():
            pr_instance = pr.objects.get(id=pr_id)
            lpr.objects.create(learner_code=learner, program_requirement_code=pr_instance, value=value)

        # Mark as approved
        verification_request.approved = True
        verification_request.save()

        return JsonResponse({"success": "Learner has been approved successfully!"})


def update_approval_status(request, request_id):
    if request.method == "POST":
        verification_request = get_object_or_404(CollegeVerificationRequest, id=request_id)
        verification_request.approved = True
        verification_request.save()
        return JsonResponse({"message": "Approval status updated successfully.", "approved": verification_request.approved})
    
    return JsonResponse({"error": "Invalid request method."}, status=400)



def gemini_workshop_registration(request):
    program_title = "L4G Gemini Workshop 2025"  # fallback in case program not found
    try:
        program = Program.objects.get(id=3)
        program_title = program.name
    except Program.DoesNotExist:
        pass
    college_name = request.POST.get("college", "").strip()
    if request.method == 'POST':
        form = GeminiWorkshopRegistrationForm(request.POST, college_name=college_name)
        if form.is_valid():
            name = form.cleaned_data['name']
            gender = form.cleaned_data['gender']
            dob = form.cleaned_data['date_of_birth']
            phone = form.cleaned_data['phone']
            branch = form.cleaned_data['branch']
            branch = Branch.objects.get(name=branch)

            rollno = form.cleaned_data['rollno'].upper()
            section = form.cleaned_data['section']
            yoj = form.cleaned_data['yoj']
            yog = form.cleaned_data['yog']
            internet = form.cleaned_data['internet']
            email = form.cleaned_data['email']
            consent = form.cleaned_data['consent']
            url = form.cleaned_data['url'] or ''
            developer_url = form.cleaned_data['developer_url']

            event_instance = form.cleaned_data["event"] 


            email_exists = lpr.objects.filter(program_requirement_code__id=13, value=email).exists()
            rollno_exists = lpr.objects.filter(program_requirement_code__id=8, value=rollno).exists()

            if email_exists:
                messages.error(request, "You have already registered with this Email.")
                return render(request, 'registration/geminiworkshop2025.html', {'form': form, 'program_title': program_title})


            if rollno_exists:
                messages.error(request, "You have already registered with this Roll Number.")
                return render(request, 'registration/geminiworkshop2025.html', {'form': form, 'program_title': program_title})



            if isinstance(college_name, str) and college_name.lower() == "other" :
                new_college = request.POST.get("new_college", "").strip()

                temporary_learner_data = {
                    "name": name,
                    "gender": gender,
                    "date_of_birth": str(dob),
                    "phone": phone,
                    "college": new_college,
                    "branch": branch.name,
                    "rollno": rollno,
                    "section": section,
                    "year_of_joining": yoj,
                    "year_of_graduation": yog,
                    "internet": internet,
                    "email": email,
                    "feedback": None,
                    "consent": consent,
                    "url": url ,
                    "developer_url": developer_url,
                    "timestamp": dt.now().strftime('%Y/%m/%d %H:%M:%S'),
                    "verified": False  
                }

                CollegeVerificationRequest.objects.create(
                    data=temporary_learner_data,
                    new_institution=new_college,
                    mobile=phone,
                    approved=False  
                )

                messages.success(request, "Your registration is pending verification.")
                return redirect(reverse("registration:registration_success", args=["under_review"]))

            else:
                college = ins.objects.get(name=college_name)

                education = le.objects.filter(rollno=rollno).first()

                if education:
                    learner = education.learner_code
                else:
                    # Roll number does not exist; create learner if not exists
                    learner = l.objects.filter(email=email).first()
                    if not learner:
                        learner = l.objects.create(
                            email=email,
                            name=name,
                            mobile=phone,
                            gender=gender,
                            date_of_birth=dob,
                        )

                    # Create education
                    education = le.objects.create(
                        rollno=rollno,
                        year_of_joining=yoj,
                        year_of_graduation=yog,
                        learner_code=learner,
                        institution_code=college,
                        branch_code=branch
                    )



                # Program requirement mapping
                timestamp_s = dt.now().strftime('%Y/%m/%d %H:%M:%S')

                program_requirements = {
                    7: internet, # Internet Access
                    8: rollno, # Roll Number
                    9: '',  # Screenshot 
                    10: '', # Feedback
                    11: consent, # Consent
                    12: timestamp_s, # Timestamp
                    13: email, # Email
                    14: event_instance, # Event Instance
                    15: url, # Google Skills Boost URL
                    16: developer_url, # Google Developer URL
                    17: section # Section
                }

                # Function to create program requirements
                def create_program_requirement(learner_code, program_requirement_id, value):
                    if value is not None:  
                        pr_instance = pr.objects.get(id=program_requirement_id)
                        if not lpr.objects.filter(learner_code=learner_code, program_requirement_code=pr_instance).exists():
                            lpr.objects.create(learner_code=learner_code, program_requirement_code=pr_instance, value=value if value is not None else "")

                
                for pr_id, value in program_requirements.items():
                    create_program_requirement(learner, pr_id, value)




                return redirect(reverse("registration:registration_success", args=["approved"]))  

        else:
            messages.error(request, "There were errors in your form. Please check and fix them.")
            return render(request, 'registration/geminiworkshop2025.html', {'form': form, 'program_title': program_title})


    else:
        form = GeminiWorkshopRegistrationForm()

    return render(request, 'registration/geminiworkshop2025.html', {'form': form, 'program_title': program_title})




def check_pr2(request):
    email = request.GET.get('email', None)
    
    if email:
        has_pr2 = lpr.objects.filter(
                learner_code__email=email, 
                program_requirement_code=2,  # Assuming 2 is the ID for the email program requirement
            ).exists()

        return JsonResponse({"has_pr2": has_pr2})

    return JsonResponse({"has_pr2": False})


def fetch_events(request):
    college_name = request.GET.get("college", "").strip()
    institution = Institution.objects.filter(name=college_name).first()

    if institution:
        events = Event.objects.filter(institution=institution, event_status="ongoing").values("id", "event_name") 
        # events = Event.objects.filter(institution=institution, event_status="Scheduled").values("id", "event_name") 
        return JsonResponse({"events": list(events)})

    return JsonResponse({"events": []})


def validate_ai_email(request):
    email = request.GET.get('email', "").strip().lower()

    is_taken = ol.objects.filter(email=email).exists() or l.objects.filter(email=email).exists()

    pattern = r'^[a-zA-Z0-9._%+-]+\.ai@gmail.com$'

    is_valid = bool(re.fullmatch(pattern, email))

    return JsonResponse({'is_taken': is_taken, 'is_valid': is_valid})




def check_rollnumber(request):
    rollno = request.GET.get('rollno', '').strip()
    email = request.GET.get('email', '').strip()

    is_rollno_registered = lpr.objects.filter(
        program_requirement_code__id=8, 
        value=rollno
    ).exists()

    is_email_registered = lpr.objects.filter(
        program_requirement_code__id=13, 
        value=email
    ).exists()

    return JsonResponse({
        "is_rollno_registered": is_rollno_registered,
        "is_email_registered": is_email_registered
    })




def add_event(request):
    errors = {}
    form = None
    show_form = request.session.get('is_authenticated', False)

    if request.method == 'POST':
        # First login attempt
        auth_email = request.POST.get('auth_email')
        auth_password = request.POST.get('auth_password')

        if not show_form and auth_email is not None and auth_password is not None:
            if auth_email == "srikanth@l4g.in" and auth_password == "srikanth@l4g.in":
                request.session['is_authenticated'] = True
                show_form = True
                form = EventForm()
            else:
                errors['auth'] = ['Invalid email or password.']
        else:
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.institution = form.cleaned_data['institution']
                event.save()
                form.save_m2m()
                messages.success(request, "Event added successfully!")
                return redirect('registration:add_event')  
            else:
                errors = form.errors

    elif show_form:
        form = EventForm()

    return render(request, 'registration/add_event.html', {
        'form': form,
        'errors': errors,
        'show_form': show_form
    })


def search_trainers(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        query = request.GET.get("q", "")
        results = []

        if query:
            trainers = Learner_Employment.objects.filter(
                Q(learner_code__name__icontains=query) | Q(learner_code__email__icontains=query)
            )[:20]

            results = [
                {"id": trainer.id, "text": f"{trainer.learner_code.name} ({trainer.learner_code.email})"}
                for trainer in trainers
            ]

        return JsonResponse({"results": results})
    return JsonResponse({"results": []}, status=400)




def autocomplete_learner(request):
    """Returns learners based on selected institution."""
    if 'term' in request.GET and 'institution' in request.GET:
        term = request.GET.get('term', '')
        institution_name = request.GET.get('institution', '')

        institution = Institution.objects.filter(name__icontains=institution_name).first()
        if not institution:
            return JsonResponse([], safe=False)

        learners = Learner_Education.objects.filter(
            institution_code=institution,
            learner_code__email__icontains=term
        ).select_related('learner_code')

        results = [
            {
                'label': f"{l.learner_code.name} ({l.learner_code.email})",
                'value': l.learner_code.email  
            }
            for l in learners
        ]
        return JsonResponse(results, safe=False)

    return JsonResponse([], safe=False)




def add_trainer(request):
    if request.method == 'POST':
        form = LearnerEmploymentForm(request.POST)

        if form.is_valid():
            empid = form.cleaned_data['empid']
            institution = form.cleaned_data['institution_code']
            learner = form.cleaned_data['learner_code']

            existing_trainer = Learner_Employment.objects.filter(empid=empid, institution_code=institution).exists()
            if existing_trainer:
                messages.error(request, "Trainer with this Employee ID and Institution already exists!")
            
            elif Learner_Employment.objects.filter(learner_code=learner).exists():
                messages.error(request, f"Trainer with Learner ID {learner.email} already exists!")

            else:
                trainer = form.save(commit=False)
                trainer.save()
                messages.success(request, "Trainer added successfully!")
                return redirect('registration:add_trainer')

        else:
            messages.error(request, "Form validation failed. Please check the fields.")

    else:
        form = LearnerEmploymentForm()

    return render(request, 'registration/add_trainer.html', {'form': form})


def upload_image_to_api(file):
    try:
        image_data = base64.b64encode(file.read()).decode('utf-8')
        response = requests.post("https://your-s3-upload-api.com/upload", json={"image_base64": image_data})
        response.raise_for_status()
        return response.json().get("public_url")
    except Exception as e:
        return None

def workshop_feedback(request):
    aspects = [
        "Content Clarity", 
        "Pacing of the Workshop", 
        "Trainer's Responsiveness to Questions"
    ]
    levels = ["Poor", "Fair", "Good", "Excellent"]

    if request.method == "POST":
        rollno = request.POST.get("rollno", "").strip().upper()
        email = request.POST.get("email", "").strip().lower()
        screenshot = request.FILES.get("screenshot")

        # Validate required fields
        if not rollno or not email or not screenshot:
            messages.error(request, "Please fill all required fields and upload a screenshot.")
            return redirect("registration:workshop_feedback")

        learner_program_obj = lpr.objects.filter(
            program_requirement_code=8, value=rollno
        ).first()

        if not learner_program_obj:
            messages.error(request, "You are not registered for the workshop.")
            return redirect("registration:workshop_feedback")

        # Upload screenshot


        
        if screenshot:
            try:
                screenshot_content = screenshot.read()
                screenshot_base64 = base64.b64encode(screenshot_content).decode('utf-8')

                payload = {
                    "image": screenshot_base64,
                    "is_base64": True,
                    "bucket_name": "certificates-db",
                    "email_id": email,
                    "roll_number": rollno,
                    "folder_name": "worklog"  
                }

                response = requests.post(
                    "https://4rwv31m778.execute-api.ap-south-1.amazonaws.com/v1/screenshot",
                    json=payload
                )

                if response.status_code == 200:
                    response_data = response.json()
                    public_url = response_data.get("public_url")

                    lpr.objects.filter(
                        learner_code=learner_program_obj.learner_code,
                        program_requirement_code=9
                    ).update(value=public_url)

                else:
                    messages.error(request, "Screenshot upload failed. Please try again.")
                    return redirect("registration:workshop_feedback")

            except Exception as e:
                messages.error(request, f"Error uploading screenshot: {str(e)}")
                return redirect("registration:workshop_feedback")


        event_requirement_obj = lpr.objects.filter(
            learner_code=learner_program_obj.learner_code,
            program_requirement_code=14
        ).first()

        workshop_date = timezone.now()

        if event_requirement_obj:
            try:
                parts = event_requirement_obj.value.split(" - ")
                if len(parts) >= 2:
                    date_str = parts[1].strip()
                    workshop_date = dt.strptime(date_str, "%Y-%m-%d %H:%M").date()

                else:
                    print("Date not found. Using current date.")
            except Exception as e:
                print("Error parsing workshop date:", e)

        # Construct feedback JSON
        feedback_data = {
            "workshop_date": workshop_date.strftime("%Y-%m-%d"),
            "overall_quality": request.POST.get("overall_quality"),
            "content_relevance": request.POST.get("content_relevance"),
            "useful_aspects": request.POST.getlist("useful_aspects"),
            "trainer_satisfaction": request.POST.get("trainer_satisfaction"),
            "future_interest": request.POST.get("future_interest"),
            "future_topics": request.POST.get("future_topics"),
            "aspects_ratings": {
                "content_clarity": request.POST.get("content-clarity"),
                "pacing_of_the_workshop": request.POST.get("pacing-of-the-workshop"),
                "trainer_responsiveness_to_questions": request.POST.get("trainers-responsiveness-to-questions"),
            },
            
            "additional_feedback": request.POST.get("feedback")
        }

        # Save feedback JSON to program_requirement_code 10
        lpr.objects.filter(
            learner_code=learner_program_obj.learner_code,
            program_requirement_code=10,
        ).update(value=feedback_data)


        messages.success(request, "Feedback submitted successfully.")
        return redirect("registration:workshop_feedback")

    return render(request, "registration/screenshot_feedback.html", {
        "aspects": [
            "Content Clarity",
            "Pacing of the Workshop",
            "Trainer's Responsiveness to Questions"
        ],
        "levels": ["Poor", "Fair", "Good", "Excellent"]
    })






EVENT_STATUS_CHOICES = ['scheduled', 'ongoing', 'completed', 'cancelled']



def event_status_manage(request):
    events = []
    trainer_found = False
    email = request.GET.get('email', '').strip()
    rollno = request.GET.get('rollno', '').strip()
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    status_choices = [(s, s.capitalize()) for s in EVENT_STATUS_CHOICES]

    if email and rollno:
        try:
            learner = Learner.objects.get(email=email)
            if not learner:
                raise ValueError("Learner not found.")


            if not Learner_Education.objects.filter(learner_code=learner, rollno=rollno).exists():
                raise ValueError("Roll number does not match the learner.")

            trainer = Learner_Employment.objects.get(learner_code=learner)
            trainer_found = True

            events = Event.objects.filter(trainers=trainer)

            if search:
                events = events.filter(event_name__icontains=search)

            if status:
                events = events.filter(event_status=status)

            if request.method == 'POST':
                for event in events:
                    event_key = f"update_event_{event.id}"
                    if event_key in request.POST:
                        # Update status
                        new_status = request.POST.get(f"status_{event.id}")
                        if new_status in EVENT_STATUS_CHOICES:
                            event.event_status = new_status

                        # Upload photo if provided
                        uploaded_file = request.FILES.get(f"photo_{event.id}")
                        if uploaded_file:
                            # Convert to base64
                            image_data = base64.b64encode(uploaded_file.read()).decode('utf-8')

                            # Prepare request
                            payload = {
                                "image": image_data,
                                "is_base64": True,
                                "bucket_name": "certificates-db",
                                "email_id": email,
                                "roll_number": rollno,
                                "folder_name": "events"
                            }

                            try:
                                res = requests.post(
                                    "https://4rwv31m778.execute-api.ap-south-1.amazonaws.com/v1/screenshot",
                                    json=payload,
                                    timeout=10
                                )
                                if res.status_code == 200:
                                    data = res.json()
                                    event.event_photo_url = data.get('public_url')
                                    messages.success(request, f"Image uploaded for event '{event.event_name}'")
                                else:
                                    messages.error(request, f"Image upload failed for '{event.event_name}'")

                            except Exception as e:
                                messages.error(request, f"Error uploading image: {str(e)}")

                        event.save()
                        messages.success(request, f"Updated event: {event.event_name}")
                        return redirect(request.get_full_path())

        except (Learner.DoesNotExist, Learner_Employment.DoesNotExist, ValueError) as e:
            messages.error(request, "Enter the valid email and roll number.")
            trainer_found = False

    return render(request, 'registration/event_status_manage_photo_upload.html', {
        'events': events,
        'trainer_found': trainer_found,
        'status_choices': status_choices,
        'email': email,
        'rollno': rollno,
        'search': search,
        'selected_status': status
    })