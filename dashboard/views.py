from django.http import HttpResponseForbidden, HttpResponse
from datetime import datetime as dt
from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Temp_Genai_Institutions as tgi, Branch, UserProfile, Temp_Genai as learners
from main.models import Learner as l, Learner_Education as le, Institution as ins, Learner_Program_Requirement as lpr, Branch as b, Program_Requirement as pr
import csv
from django.utils.timezone import make_aware, is_naive
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from main.models import Learner_Program_Progress,Learner_Module_Progress,Learner_Course_Progress,Learner_Specialization_Progress
from main.models import Learner_Employment, Institution, Program
from django.db.models import Count
from main.models import Institution_Program_Requirement_General as iprg, Institution_Program_Requirement_Specific as iprs
from django.db.models import Sum
from django.db.models import Prefetch



def genai_summer_internship_dashboard(request):
    selected_college = request.GET.get('college')
    selected_branch = request.GET.get('branch')
    selected_year = request.GET.get('year_of_graduation')
    selected_section = request.GET.get('section')
    action = request.GET.get('action')
    learners_data = []
    learner_ids = lpr.objects.filter(program_requirement_code__program_code__id=4).values_list('learner_code_id', flat=True).distinct()

    learners = l.objects.filter(id__in=learner_ids).prefetch_related(
        Prefetch('learner_education_set', to_attr='education_list'),
        Prefetch('learner_program_requirement_set', to_attr='lpr_list')
    )
    if selected_college:
        learners = learners.filter(learner_education__institution_code__name=selected_college)
    if selected_branch:
        learners = learners.filter(learner_education__branch_code__name=selected_branch)
    if selected_year:
        learners = learners.filter(learner_education__year_of_graduation=selected_year)
    if selected_section:
        learners = learners.filter(learner_program_requirement__program_requirement_code__id=29, learner_program_requirement__value=selected_section)

    for learner in learners:
        education = learner.education_list[0] if learner.education_list else None
        lpr_dict = {l.program_requirement_code.id: l.value for l in learner.lpr_list}
        

        learners_data.append({
            'id': learner.id,
            'sno': len(learners_data) + 1,
            'name': learner.name,
            'email': lpr_dict.get(24, learner.email),
            'college': education.institution_code.name if education else 'N/A',
            'branch': education.branch_code.name if education else 'N/A',
            'year_of_graduation': education.year_of_graduation if education else 'N/A',
            'mobile': learner.mobile,
            'section': lpr_dict.get(29, '-'),
            'roll_number': lpr_dict.get(23, '-'),
            'skills_boost_url': lpr_dict.get(28, '-'),
            'developer_url': lpr_dict.get(27, '-'),
            'registration_timestamp': lpr_dict.get(25, '-'),
            'approval_status': lpr_dict.get(32) if lpr_dict.get(32) else 'No',
        })

    registered_count = len(learners_data)

    colleges = sorted(le.objects.filter(learner_code_id__in=learner_ids).values_list('institution_code__name', flat=True).distinct())
    branches = sorted(le.objects.filter(learner_code_id__in=learner_ids).values_list('branch_code__name', flat=True).distinct())
    years_of_graduation = sorted(le.objects.filter(learner_code_id__in=learner_ids).values_list('year_of_graduation', flat=True).distinct())
    sections = sorted(lpr.objects.filter(program_requirement_code__id=29).values_list('value', flat=True).distinct())

    trainer_approved_count = sum(1 for learner in learners_data if learner['approval_status'] == 'Yes')
    if selected_college:
        total_colleges = 1
    else :
        total_colleges = len(colleges)


    context = {
        'learners': learners_data,
        'selected_college': selected_college,
        'selected_branch': selected_branch,
        'selected_year': selected_year,
        'selected_section': selected_section,
        'registered_count': registered_count,
        'trainer_approved_count': trainer_approved_count,
        'total_colleges': total_colleges,
        'colleges': colleges,
        'branches': branches,
        'years_of_graduation': years_of_graduation,
        'sections': sections,
    }

    # CSV Download
    if action == 'download':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Genai_summer_internship_2025_learner_data.csv"'
        writer = csv.writer(response)
        writer.writerow([ 
            'S.No', 'Registration Timestamp', 'Roll Number', 'Student Name', 'Mobile Number', 'Email',
            'Branch', 'Year of Graduation', 'Section', 'College', 'Google Skills Boost URL',
            'Developer Profile Link', 'GenAI Completed'
        ])
        for learner in learners_data:
            writer.writerow([
                learner['sno'], learner['registration_timestamp'], learner['roll_number'],
                learner['name'], learner['mobile'], learner['email'], learner['branch'],
                learner['year_of_graduation'], learner['section'], learner['college'],
                learner['skills_boost_url'], learner['developer_url'],  learner['approval_status']
            ])
        return response

    return render(request, 'dashboard/genai_summer_internship_dashboard.html', context)



###########################################################################################################


def home(request):
   #user_profile = UserProfile.objects.get(user=request.user)


   #if user_profile.college == 'L4G':
      # return redirect('dashboard:genai2025registration')
   #else:
       #return redirect('dashboard:college')
    return redirect('dashboard:genai2025registration')


#@login_required
def download_csv(request):
   if request.GET:
       final = filter_registration_data(request)


       response = HttpResponse(content_type='text/csv')
       response['Content-disposition'] = 'attachment; filename="genai_registration_data.csv"'


       writer = csv.writer(response)
       writer.writerow(['Timestamp', 'Name', 'Gender', 'College','YOG', 'Email', 'URL'])


       for i in final:
           writer.writerow([final[i]['timestamp'], final[i]['name'], final[i]['gender'], final[i]['college'],final[i]['yog'], i, final[i]['url']])
       return response


# @login_required
def filter_registration_data(request):
    learner_data = le.objects.all()
    final = {}

    college = request.GET.get('college')
    branch = request.GET.get('branch')
    gender = request.GET.get('gender')
    yog = request.GET.get('yog')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if college:
        try:
            college = ins.objects.get(id=college)
            learner_data = learner_data.filter(institution_code=college)
        except ins.DoesNotExist:
            pass

    if branch:
        try:
            branch = b.objects.get(id=branch)
            learner_data = learner_data.filter(branch_code=branch)
        except b.DoesNotExist:
            pass

    if gender:
        learner_data = learner_data.filter(learner_code__gender=gender)

    if yog:
        learner_data = learner_data.filter(year_of_graduation=yog)

    try:
        pr3 = pr.objects.get(id=3)  # Google Cloud Skills Boost URL
        pr2 = pr.objects.get(id=2)  # Email
        pr6 = pr.objects.get(id=6)  # Timestamp
    except pr.DoesNotExist:
        return final  # Or handle error gracefully

    for i in learner_data:
        learner = i.learner_code

        # Get program values safely
        email_obj = lpr.objects.filter(learner_code=learner, program_requirement_code=pr2).first()
        url_obj = lpr.objects.filter(learner_code=learner, program_requirement_code=pr3).first()
        timestamp_obj = lpr.objects.filter(learner_code=learner, program_requirement_code=pr6).first()

        learner_lpr_email = email_obj.value if email_obj else "N/A"
        learner_lpr_url = url_obj.value if url_obj else "N/A"
        learner_lpr_timestamp = timestamp_obj.value if timestamp_obj else None
        yog_val = i.year_of_graduation

        # Timestamp filtering
        if learner_lpr_timestamp:
            try:
                timestamp_date = datetime.strptime(learner_lpr_timestamp, "%Y/%m/%d %H:%M:%S")  # Adjust format to your DB
                timestamp_date = make_aware(timestamp_date) if timezone.is_naive(timestamp_date) else timestamp_date
            except ValueError:
                continue  # Skip invalid date format

            if start_date:
                try:
                    start_date_parsed = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
                    start_date_parsed = start_date_parsed.replace(hour=0, minute=0)
                    if timestamp_date < start_date_parsed:
                        continue
                except ValueError:
                    pass

            if end_date:
                try:
                    end_date_parsed = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
                    end_date_parsed = end_date_parsed.replace(hour=23, minute=59)
                    if timestamp_date > end_date_parsed:
                        continue
                except ValueError:
                    pass

        # Dictionary of Dictionaries
        final[learner_lpr_email] = {
            'name': learner.name,
            'rollno': i.rollno,
            'college': i.institution_code.name,
            'branch': i.branch_code.short_name,
            'url': learner_lpr_url,
            'timestamp': learner_lpr_timestamp,
            'mobile': learner.mobile,
            'gender': learner.gender,
            'yog': yog_val
        }

    return final




#@login_required
def genai2025registration(request):
   #user_profile = UserProfile.objects.get(user=request.user)
   #if user_profile.college != 'L4G':
       #return HttpResponseForbidden('You do not have permission to access this page.')
  
   institutions = []
   branches = []
   learner_data = []
   final = {}
   total_students = l.objects.count
   for i in le.objects.all():
       if i.institution_code not in institutions:
           institutions.append(i.institution_code)
       if i.branch_code not in branches:
           branches.append(i.branch_code)

   genders = l.objects.values_list('gender', flat=True).distinct()
   years_of_graduation = le.objects.values_list('year_of_graduation', flat=True).distinct().order_by('year_of_graduation')


   if request.GET:
       final = filter_registration_data(request)
  
   context = {
       'institutions': institutions,
       'branches': branches,
       'final': final,
       'total_students': total_students,
       'genders': genders,
       'years_of_graduation': years_of_graduation
   }
   return render(request, 'dashboard/genai2025registration.html', context)

def filter_l4g_data(request):
    from django.db.models import Q

    # Fetch filter values from request parameters
    institution_name = request.GET.get('institution_name', '')
    onboarded_filter = request.GET.get('onboarded', '')
    completion_filter = request.GET.get('completion', '')
    level_filter = request.GET.get('level', '')

   

    # Start with all institutions except L4G
    institutions = tgi.objects.exclude(name='L4G')

    # Apply filters only if values are provided
    if institution_name:
        institutions = institutions.filter(name__icontains=institution_name)
        

    onboarded_mapping = {"200+": 200, "150+": 150, "100+": 100}
    if onboarded_filter in onboarded_mapping:
        onboarded_value = int(onboarded_mapping[onboarded_filter])
        institutions = institutions.filter(onboarded__gt=onboarded_value)
        

    completion_mapping = {"200+": 200, "150+": 150, "100+": 100}
    if completion_filter in completion_mapping:
        completion_value = int(completion_mapping[completion_filter])
        institutions = institutions.filter(completions__gt=completion_value)
        

    
       

    # If no filters are applied, return all institutions sorted by onboarded count
    institutions = institutions.order_by('-onboarded')

    # Debugging: Print final query
    

    return institutions







#@method_decorator(never_cache, name='dispatch')
#@login_required
def l4g(request):
    # user_profile = UserProfile.objects.get(user=request.user)
    # if user_profile.college != 'L4G':
    #     return HttpResponseForbidden('You do not have permission to access this page.')

    l4g = tgi.objects.get(name='L4G')
    learners_onboarded = l4g.onboarded
    completions = l4g.completions
    active_learners = l4g.active
    pending_invitations = l4g.pending
    digital_badges = l4g.digital_badges
    learning_hours = (
        l4g.beginner_completions * 8
        + l4g.intermediate_completions * 15
        + l4g.advanced_completions * 19
    )
    colleges = filter_l4g_data(request)
    all_institutions = tgi.objects.all()
    

    context = {
        'learners_onboarded': f'{learners_onboarded:,}',
        'graph_onboarded': learners_onboarded,
        'active_learners': f'{active_learners:,}',
        'graph_active_learners': active_learners,
        'digital_badges': f'{digital_badges:,}',
        'learning_hours': f'{learning_hours:,}',
        'completions': f'{completions:,}',
        'graph_completions': completions,
        'graph_pending_invitations': pending_invitations,
        'colleges': colleges,
        'beginner': f'{l4g.beginner_completions:,}',
        'intermediate': f'{l4g.intermediate_completions}',
        'advanced': f'{l4g.advanced_completions}',
        'all_institutions': all_institutions,
        
    }

    return render(request, 'dashboard\l4g.html', context)



from django.shortcuts import render
from django.http import JsonResponse
from main.models import Learner_Program_Progress, Learner_Course_Progress, Learner_Education as le, Institution as ins




def genai2025(request):
    # Overall counts
    onboarded_count = Learner_Program_Progress.objects.filter(program_code_id=2,is_onboarded=True).count()
    active_count = Learner_Program_Progress.objects.filter(program_code_id=2,is_active=True).count()
    completions_count = Learner_Program_Progress.objects.filter(program_code_id=2, is_completed=True).count()

    beginner = Learner_Course_Progress.objects.filter(course_code_id=1, is_completed=True).count()
    intermediate = Learner_Course_Progress.objects.filter(course_code_id=2, is_completed=True).count()
    advanced = Learner_Course_Progress.objects.filter(course_code_id=3, is_completed=True).count()

    learning_hours = (beginner * 8) + (intermediate * 15) + (advanced * 19)

    institutions = ins.objects.all()
    institution_data = get_filtered_institution_data()

    context = {
        'onboarded_count': onboarded_count,
        'active_count': active_count,
        'completions': completions_count,
        'beginner': beginner,
        'intermediate': intermediate,
        'advanced': advanced,
        'learning_hours': learning_hours,
        'graph_onboarded': onboarded_count,
        'graph_active_learners': active_count,
        'graph_completions': completions_count,
        'data': institution_data,
        'institutions': institutions,
    }

    return render(request, 'dashboard/genai2025.html', context)


def filter_genai2025_data(request):
    institution_name = request.GET.get('institution')
    onboarded_filter = request.GET.get('onboarded')
    completions_filter = request.GET.get('completions')

    try:
        onboarded_filter = int(onboarded_filter) if onboarded_filter else None
    except ValueError:
        onboarded_filter = None

    try:
        completions_filter = int(completions_filter) if completions_filter else None
    except ValueError:
        completions_filter = None

    data = get_filtered_institution_data(
        institution_name=institution_name,
        onboarded_filter=onboarded_filter,
        completions_filter=completions_filter
    )

    return JsonResponse({'data': data})


def get_filtered_institution_data(institution_name=None, onboarded_filter=None, completions_filter=None):
    institutions = ins.objects.all()
    if institution_name:
        institutions = institutions.filter(name=institution_name)

    institution_data = []

    for institution in institutions:
        learner_ids = le.objects.filter(institution_code=institution).values_list('learner_code', flat=True)
        progress_qs = Learner_Program_Progress.objects.filter(learner_code__in=learner_ids)

        onboarded = progress_qs.filter(is_onboarded=True).count()
        active = progress_qs.filter(is_active=True).count()
        completions = progress_qs.filter(is_completed=True).count()

        beginner = Learner_Course_Progress.objects.filter(
            learner_code__in=learner_ids, course_code_id=1, is_completed=True).count()
        intermediate = Learner_Course_Progress.objects.filter(
            learner_code__in=learner_ids, course_code_id=2, is_completed=True).count()
        advanced = Learner_Course_Progress.objects.filter(
            learner_code__in=learner_ids, course_code_id=3, is_completed=True).count()

        # Apply filters
        if onboarded_filter and onboarded < onboarded_filter:
            continue
        if completions_filter and completions < completions_filter:
            continue

        total = onboarded if onboarded else 1
        percent = round((completions / total) * 100)

        institution_data.append({
            'institution': institution.name,
            'onboarded': onboarded,
            'active': active,
            'beginner': beginner,
            'intermediate': intermediate,
            'advanced': advanced,
            'completions': completions,
            'percent': percent,
        })

    return sorted(institution_data, key=lambda x: x['onboarded'], reverse=True)

from django.shortcuts import render
from main.models import Learner_Employment, Event, Learner_Program_Progress

from django.db.models import Q

def eventlist(request):
    trainer_emps = Learner_Employment.objects.all()
    events = []
    selected_trainer_id = request.POST.get('trainer')

    if selected_trainer_id:
        selected_trainer = Learner_Employment.objects.get(id=selected_trainer_id)
        events = Event.objects.filter(trainers=selected_trainer).prefetch_related('program_code')

        for event in events:
            program = event.program_code
            if program:
                # Get learners who are associated with requirements of this program
                learners = l.objects.filter(
                    learner_program_requirement__program_requirement_code__program_code=program
                ).distinct()

                event.learners = learners
            else:
                event.learners = []

    return render(request, 'dashboard/events-list.html', {
        'trainers': trainer_emps,
        'events': events,
        'selected_trainer_id': int(selected_trainer_id) if selected_trainer_id else None,
    })





#@login_required
def college(request):
   user_profile = UserProfile.objects.get(user=request.user)
   if user_profile.college == 'L4G':
       return HttpResponseForbidden('You do not have permission to access this page.')
  
   college = tgi.objects.get(name=user_profile.college)
   college_learners = learners.objects.filter(college=college.name)
   branches = []
   learner_data = []
   for i in college_learners:
       if i.branch_code not in branches:
           branches.append(i.branch_code)
   enrollment_status_options = ['active', 'pending', 'declined', '#N/A']
   completion_status_options = ['Completed', 'Not Completed']
   learners_onboarded = college.onboarded
   # years = [year for year in range(dt.now().year,dt.now().year+5)]
   # branches = Branch.objects.all()


   # selected_college = request.GET.get('college')
   # selected_branch = request.GET.get('branch')
   # selected_year = request.GET.get('year')
   completions = college.completions
   active_learners = college.active
   #pending_invitations = l4g.pending
   digital_badges = college.digital_badges
   learning_hours = college.beginner_completions*8 + college.intermediate_completions*15 + college.advanced_completions*19




   #if request.GET:
   branch = request.GET.get('branch')
   enrollment_status = request.GET.get('enrollment_status')
   completion_status = request.GET.get('completion_status')
   rollno = request.GET.get('rollno')


   if branch and enrollment_status and completion_status:
       learner_data = college_learners.filter(branch_code=branch).filter(enrollment_status=enrollment_status).filter(completion_status=completion_status)
   elif branch and not enrollment_status and not completion_status:
       learner_data = college_learners.filter(branch_code=branch)
   elif not branch and enrollment_status and not completion_status:
       learner_data = college_learners.filter(enrollment_status=enrollment_status)
   elif not branch and not enrollment_status and completion_status:
       learner_data = college_learners.filter(completion_status=completion_status)
   elif branch and enrollment_status and not completion_status:
       learner_data = college_learners.filter(branch_code=branch).filter(enrollment_status=enrollment_status)
   elif branch and not enrollment_status and completion_status:
       learner_data = college_learners.filter(branch_code=branch).filter(completion_status=completion_status)
   elif not branch and enrollment_status and completion_status:
       learner_data = college_learners.filter(enrollment_status=enrollment_status).filter(completion_status=completion_status)
   # else:
   #     learner_data = college_learners
   #style="color:#66e7a9"
  
   if rollno:
       learner_data = college_learners.filter(rollno=rollno.strip().upper())






   context = {
       'learners_onboarded': f'{learners_onboarded:,}',
       'graph_onboarded': learners_onboarded,
       'active_learners': f'{active_learners:,}',
       'graph_active_learners': active_learners,
       'digital_badges': f'{digital_badges:,}',
       'learning_hours': f'{learning_hours:,}',
       'completions': f'{completions:,}',
       'graph_completions': completions,
       'user_college': user_profile.college,
       'beginner': f'{college.beginner_completions:,}',
       'intermediate': f'{college.intermediate_completions}',
       'advanced': f'{college.advanced_completions}',
       'learner_data': learner_data,
       'branches': branches,
       'enrollment_status_options': enrollment_status_options,
       'completion_status_options': completion_status_options,
      
   }
   return render(request, 'college.html', context)


#@login_required
def export_data_csv(request):


   if request.method == 'POST':
       branch = request.POST.get('branch')
       enrollment_status = request.POST.get('enrollment_status')
       completion_status = request.POST.get('completion_status')
       rollno = request.POST.get('rollno')


       user_profile = UserProfile.objects.get(user=request.user)
       college = tgi.objects.get(name=user_profile.college)
       college_learners = learners.objects.filter(college=college.name)
       learner_data = []


       if branch and enrollment_status and completion_status:
           learner_data = college_learners.filter(branch_code=branch).filter(enrollment_status=enrollment_status).filter(completion_status=completion_status)
       elif branch and not enrollment_status and not completion_status:
           learner_data = college_learners.filter(branch_code=branch)
       elif not branch and enrollment_status and not completion_status:
           learner_data = college_learners.filter(enrollment_status=enrollment_status)
       elif not branch and not enrollment_status and completion_status:
           learner_data = college_learners.filter(completion_status=completion_status)
       elif branch and enrollment_status and not completion_status:
           learner_data = college_learners.filter(branch_code=branch).filter(enrollment_status=enrollment_status)
       elif branch and not enrollment_status and completion_status:
           learner_data = college_learners.filter(branch_code=branch).filter(completion_status=completion_status)
       elif not branch and enrollment_status and completion_status:
           learner_data = college_learners.filter(enrollment_status=enrollment_status).filter(completion_status=completion_status)


       if rollno:
           learner_data = college_learners.filter(rollno=rollno.strip().upper())


       # Create the HttpResponse object with CSV headers
       response = HttpResponse(content_type='text/csv')
       response['Content-Disposition'] = 'attachment; filename="students.csv"'


       # Create a CSV writer
       writer = csv.writer(response)


       # Write the header row
       writer.writerow(['Roll No', 'Name', 'Enrollment Status', 'Completion Status', 'Email', 'Profile'])


       # Write data rows for filtered students
       for student in learner_data:
           writer.writerow([
               student.rollno,
               student.name,
               student.enrollment_status,
               student.completion_status,
               student.email,
               student.url,
           ])


       return response
  




@login_required
def login_success(request):
    return render(request, 'dashboard/login_success.html')


###########################################################################################################

@login_required
def college_dashboard_redirect(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.college.strip().upper() == "L4G":
        institutions = Institution.objects.annotate(
            learner_count=Count('learner_education__learner_code', distinct=True)
        ).filter(learner_count__gt=0).order_by('name')

        total_learners = sum(c.learner_count for c in institutions)
        total_colleges = institutions.count()

        # Total unique programs
        total_programs = iprg.objects.values('program_code').distinct().count()

        # Attach program details to each institution
        for institution in institutions:
            specific_reqs = iprs.objects.filter(
                institution_code=institution
            ).select_related('institution_program_requirement_general_code__program_code')

            unique_programs = set()
            for req in specific_reqs:
                program = req.institution_program_requirement_general_code.program_code
                unique_programs.add(program)

            institution.program_count = len(unique_programs)
            institution.program_names = sorted(p.name for p in unique_programs)

        return render(request, 'dashboard/all_college_dashboard.html', {
            'institutions': institutions,
            'total_learners': total_learners,
            'total_colleges': total_colleges,
            'total_programs': total_programs,
        })

    try:
        college_obj = Institution.objects.get(name=user_profile.college)
        return redirect('dashboard:college_dashboard', l4g_code=college_obj.l4g_code)
    except Institution.DoesNotExist:
        return redirect('dashboard:login')  # Change to production login URL

@login_required
def college_redirect_by_l4gcode(request):
    l4g_code = request.GET.get('l4g_code')
    return redirect('dashboard:college_dashboard', l4g_code=l4g_code)

    
def get_programs_for_institution(institution):
    specific_reqs = iprs.objects.filter(
        institution_code=institution
    ).select_related('institution_program_requirement_general_code__program_code')

    unique_programs = set()
    for req in specific_reqs:
        program = req.institution_program_requirement_general_code.program_code
        unique_programs.add(program)

    return sorted(unique_programs, key=lambda p: p.name)

@login_required
def college_dashboard_view(request, l4g_code):
    college_obj = get_object_or_404(Institution, l4g_code=l4g_code)
    program_id = request.GET.get('program')

    if program_id == '4':
        return redirect('dashboard:genai_internship_dashboard_2025', l4g_code=college_obj.l4g_code)
    elif program_id == '3':
        return redirect('dashboard:geminiworkshop_2025', l4g_code=college_obj.l4g_code)
    elif program_id == '2':
        return redirect('dashboard:genai_dashboard_2025', l4g_code=college_obj.l4g_code)

    total_learners = le.objects.filter(institution_code=college_obj).count()

    available_programs = get_programs_for_institution(college_obj)

    return render(request, 'dashboard/college_dashboard.html', {
        'college': college_obj,
        'programs': available_programs,
        'total_learners': total_learners,
        'selected_program_id': program_id,
        'program_count': len(available_programs),
        'program_names': [p.name for p in available_programs],
        'error': 'Please select a program to continue.'
    })




@login_required
def genai_internship_dashboard_2025(request, l4g_code):
    selected_branch = request.GET.get('branch')
    selected_year = request.GET.get('year_of_graduation')
    selected_section = request.GET.get('section')
    program_id = request.GET.get('program')
    action = request.GET.get('action')

    user_profile = get_object_or_404(UserProfile, user=request.user)
    college_obj = get_object_or_404(Institution, l4g_code=l4g_code)

    if program_id == '3':
        return redirect('dashboard:geminiworkshop_2025', l4g_code=college_obj.l4g_code)
    elif program_id == '2':
        return redirect('dashboard:genai_dashboard_2025', l4g_code=college_obj.l4g_code)

    program_id = '4'  # GenAI Summer Internship program

    filters_applied = bool(selected_branch or selected_year or selected_section)

    learners_data = []
    if filters_applied or action == 'download':
        learner_ids = lpr.objects.filter(
            program_requirement_code__program_code__id=program_id
        ).values_list('learner_code_id', flat=True).distinct()

        learners = l.objects.filter(
            id__in=learner_ids,
            learner_education__institution_code=college_obj
        ).prefetch_related(
            Prefetch('learner_education_set', to_attr='education_list'),
            Prefetch('learner_program_requirement_set', to_attr='lpr_list')
        )

        if selected_branch:
            learners = learners.filter(learner_education__branch_code__name=selected_branch)
        if selected_year:
            learners = learners.filter(learner_education__year_of_graduation=selected_year)
        if selected_section:
            learners = learners.filter(
                learner_program_requirement__program_requirement_code__id=29,
                learner_program_requirement__value=selected_section
            )

        for learner in learners:
            education = learner.education_list[0] if learner.education_list else None
            lpr_dict = {lpr.program_requirement_code.id: lpr.value for lpr in learner.lpr_list}

            learners_data.append({
                'id': learner.id,
                'sno': len(learners_data) + 1,
                'name': learner.name,
                'email': lpr_dict.get(24, learner.email),
                'college': education.institution_code.name if education else 'N/A',
                'branch': education.branch_code.name if education else 'N/A',
                'year_of_graduation': education.year_of_graduation if education else 'N/A',
                'mobile': learner.mobile,
                'section': lpr_dict.get(29, '-'),
                'roll_number': lpr_dict.get(23, '-'),
                'skills_boost_url': lpr_dict.get(28, '-'),
                'developer_url': lpr_dict.get(27, '-'),
                'registration_timestamp': lpr_dict.get(25, '-'),
                'approval_status': lpr_dict.get(32, 'No'),
            })

    registered_count = len(learners_data)

    # For filters dropdowns
    learner_ids_all = lpr.objects.filter(
        program_requirement_code__program_code__id=program_id
    ).values_list('learner_code_id', flat=True).distinct()

    branches = sorted(le.objects.filter(
        learner_code_id__in=learner_ids_all
    ).values_list('branch_code__name', flat=True).distinct())

    years_of_graduation = sorted(le.objects.filter(
        learner_code_id__in=learner_ids_all
    ).values_list('year_of_graduation', flat=True).distinct())

    sections = sorted(lpr.objects.filter(
        program_requirement_code__id=29
    ).values_list('value', flat=True).distinct())

    # Metrics
    general_reqs = iprg.objects.filter(program_code__id=program_id)
    label_map = {
        'onboarded': 'onboarded_count',
        'active': 'active_count',
        'completion': 'program_completions',
        'beginner': 'beginner_completions',
        'intermediate': 'intermediate_completions',
        'advanced': 'advanced_completions',
    }

    metric_counts = {
        'onboarded_count': 0,
        'active_count': 0,
        'program_completions': 0,
        'beginner_completions': 0,
        'intermediate_completions': 0,
        'advanced_completions': 0,
    }

    for req in general_reqs:
        name = req.name.lower()
        for keyword, label in label_map.items():
            if keyword in name:
                value = iprs.objects.filter(
                    institution_code=college_obj,
                    institution_program_requirement_general_code=req
                ).values_list('value', flat=True).first()
                try:
                    metric_counts[label] = int(value)
                except:
                    metric_counts[label] = 0

    learning_hours = (
        metric_counts['beginner_completions'] * 8 +
        metric_counts['intermediate_completions'] * 15 +
        metric_counts['advanced_completions'] * 19
    )

    # CSV download
    if action == 'download':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Genai_summer_internship_2025_learner_data.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'S.No', 'Registration Timestamp', 'Roll Number', 'Student Name', 'Mobile Number',
            'Email', 'Branch', 'Year of Graduation', 'Section', 'College',
            'Google Skills Boost URL', 'Developer Profile Link', 'GenAI Completed'
        ])
        for learner in learners_data:
            writer.writerow([
                learner['sno'], learner['registration_timestamp'], learner['roll_number'],
                learner['name'], learner['mobile'], learner['email'], learner['branch'],
                learner['year_of_graduation'], learner['section'], learner['college'],
                learner['skills_boost_url'], learner['developer_url'], learner['approval_status']
            ])
        return response

    available_programs = get_programs_for_institution(college_obj)

    context = {
        'learners': learners_data,
        'filters_applied': filters_applied,
        'selected_branch': selected_branch,
        'selected_year': selected_year,
        'selected_section': selected_section,
        'registered_count': registered_count,
        'branches': branches,
        'years_of_graduation': years_of_graduation,
        'sections': sections,
        'program_id': str(program_id),
        'programs': available_programs,
        'college': college_obj,
        'onboarded_count': metric_counts['onboarded_count'],
        'active_count': metric_counts['active_count'],
        'program_completions': metric_counts['program_completions'],
        'beginner_completions': metric_counts['beginner_completions'],
        'intermediate_completions': metric_counts['intermediate_completions'],
        'advanced_completions': metric_counts['advanced_completions'],
        'learning_hours': learning_hours,
    }

    return render(request, 'dashboard/genai_internship_dashboard_2025.html', context)



@login_required
def geminiworkshop_2025(request, l4g_code):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    college_obj = get_object_or_404(Institution, l4g_code=l4g_code)

    action = request.GET.get('action')
    search_triggered = request.GET.get('search')

    selected_college = request.GET.get('college')
    selected_branch = request.GET.get('branch')
    selected_year = request.GET.get('year_of_graduation')
    selected_section = request.GET.get('section')

    program_id = request.GET.get('program')

    if program_id == '4':
        return redirect('dashboard:genai_internship_dashboard_2025', l4g_code=college_obj.l4g_code)
    elif program_id == '2':
        return redirect('dashboard:genai_dashboard_2025', l4g_code=college_obj.l4g_code)

    program_id = '3'
    context = {}

    all_events = Event.objects.filter(institution=college_obj).order_by('-datetime')
    context['events'] = all_events

    raw_learners_data = []

    for event in all_events:
        learners = l.objects.filter(
            learner_program_requirement__program_requirement_code__id=14,
            learner_program_requirement__value=event,
            learner_education__institution_code=college_obj
        ).distinct().prefetch_related(
            Prefetch('learner_education_set', to_attr='education_list'),
            Prefetch('learner_program_requirement_set', to_attr='lpr_list')
        )

        for learner in learners:
            education = learner.education_list[0] if learner.education_list else None
            lpr_dict = {pr.program_requirement_code.id: pr.value for pr in learner.lpr_list}

            raw_learners_data.append({
                'event_name': event.event_name,
                'roll_number': lpr_dict.get(8, '-'),
                'name': learner.name,
                'mobile': learner.mobile,
                'skills_boost_url': lpr_dict.get(15, '-'),
                'developer_url': lpr_dict.get(16, '-'),
                'college': education.institution_code.name if education else 'N/A',
                'branch': education.branch_code.name if education else 'N/A',
                'year_of_graduation': education.year_of_graduation if education else 'N/A',
                'section': lpr_dict.get(17, '-'),
                'screenshot': lpr_dict.get(9, 'Not Uploaded'),
                'flash_completed': 'Yes' if lpr_dict.get(19) else 'No',
            })

    # Dynamically count Worklog Submitted and Trainer Approved using sum of 'value'
    general_reqs = iprg.objects.filter(program_code__id=program_id)

    label_map = {
        'worklog submitted': 'worklog_submitted_count',
        'trainer approved': 'trainer_approved_count',
    }

    metric_counts = {
        'worklog_submitted_count': 0,
        'trainer_approved_count': 0,
    }

    for req in general_reqs:
        name = req.name.lower()
        for keyword, label in label_map.items():
            if keyword in name:
                value = iprs.objects.filter(
                    institution_code=college_obj,
                    institution_program_requirement_general_code=req
                ).aggregate(total=Sum('value'))['total'] or 0
                metric_counts[label] = value

    # Derived values
    registered_count = len(raw_learners_data)
    worklog_submitted_count = metric_counts['worklog_submitted_count']
    trainer_approved_count = metric_counts['trainer_approved_count']
    worklog_not_submitted_count = registered_count - worklog_submitted_count
    trainer_not_approved_count = worklog_submitted_count - trainer_approved_count

    # Update context
    context.update({
        'registered_count': registered_count,
        'flash_completed_count': sum(1 for l in raw_learners_data if l['flash_completed'] == 'Yes'),
        'worklog_submitted_count': worklog_submitted_count,
        'worklog_not_submitted_count': worklog_not_submitted_count,
        'trainer_approved_count': trainer_approved_count,
        'trainer_not_approved_count': trainer_not_approved_count,
    })

    # Apply filters
    filtered_learners = []
    for i, learner in enumerate(raw_learners_data, start=1):
        if selected_branch and selected_branch != learner['branch']:
            continue
        if selected_year and selected_year != str(learner['year_of_graduation']):
            continue
        if selected_section and selected_section != learner['section']:
            continue
        learner['sno'] = i
        filtered_learners.append(learner)

    context['learners'] = filtered_learners if search_triggered else raw_learners_data

    available_programs = get_programs_for_institution(college_obj)

    # Filter dropdowns
    context.update({
        'branches': sorted(le.objects.filter(institution_code=college_obj).values_list('branch_code__name', flat=True).distinct()),
        'years_of_graduation': sorted(le.objects.filter(institution_code=college_obj).values_list('year_of_graduation', flat=True).distinct()),
        'sections': sorted(lpr.objects.filter(program_requirement_code__id=17).values_list('value', flat=True).distinct()),

        'selected_branch': selected_branch,
        'selected_year': selected_year,
        'selected_section': selected_section,
        'total_events': Event.objects.filter(institution=college_obj).count(),

        'program_id': str(program_id),
        'programs': available_programs,
        "college" : college_obj,
    })

    # CSV Download
    if action == 'download':
        response = HttpResponse(content_type='text/csv')
        filename = selected_college or "gemini_summary"
        response['Content-Disposition'] = f'attachment; filename="{filename}_summary.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'S.No', 'Event Name', 'Roll Number', 'Student Name', 'Mobile Number', 'College',
            'Branch', 'Year of Graduation', 'Section', 'Google Skills Boost URL',
            'Developer Profile Link', 'Worklog Screenshot', 'Flash Completed'
        ])
        for i, learner in enumerate(context['learners'], start=1):
            writer.writerow([
                i, learner['event_name'], learner['roll_number'], learner['name'], learner['mobile'],
                learner['college'], learner['branch'], learner['year_of_graduation'], learner['section'],
                learner['skills_boost_url'], learner['developer_url'], learner['screenshot'], learner['flash_completed']
            ])
        return response

    return render(request, 'dashboard/geminiworkshop_2025.html', context)





@login_required
def genai_dashboard_2025(request, l4g_code):
    # GET filters
    selected_branch = request.GET.get('branch')
    selected_year = request.GET.get('year_of_graduation')
    selected_section = request.GET.get('section')
    selected_college = request.GET.get('college')
    selected_gender = request.GET.get('gender')
    action = request.GET.get('action')
    


    program_id = request.GET.get('program')
    if program_id == '4':
        return redirect('dashboard:genai_internship_dashboard_2025', l4g_code=l4g_code)
    elif program_id == '3':
        return redirect('dashboard:geminiworkshop_2025', l4g_code=l4g_code)

    program_id = 2
    # Core setup
    user_profile = get_object_or_404(UserProfile, user=request.user)
    college_obj = get_object_or_404(Institution, l4g_code=l4g_code)

    learner_ids = lpr.objects.filter(program_requirement_code__program_code__id=program_id).values_list('learner_code_id', flat=True).distinct()
    learners = l.objects.filter(id__in=learner_ids, learner_education__institution_code=college_obj).prefetch_related(
        Prefetch('learner_education_set', to_attr='education_list'),
        Prefetch('learner_program_requirement_set', to_attr='lpr_list')
    )

    # Additional filtering
    if selected_branch:
        learners = learners.filter(learner_education__branch_code__name=selected_branch)
    if selected_year:
        learners = learners.filter(learner_education__year_of_graduation=selected_year)
    if selected_section:
        learners = learners.filter(
            learner_program_requirement__program_requirement_code__id=29,
            learner_program_requirement__value=selected_section
        )
    if selected_gender:
        learners = learners.filter(gender=selected_gender)

    # Preparing data
    learners_data = []
    for learner in learners:
        education = learner.education_list[0] if learner.education_list else None
        lpr_dict = {l.program_requirement_code.id: l.value for l in learner.lpr_list}

        timestamp_raw = lpr_dict.get(6)
        try:
            timestamp_parsed = datetime.strptime(timestamp_raw, "%Y/%m/%d %H:%M:%S") if timestamp_raw else None
            if timestamp_parsed and is_naive(timestamp_parsed):
                timestamp_parsed = make_aware(timestamp_parsed)
        except:
            timestamp_parsed = None

       

        learners_data.append({
            'id': learner.id,
            'sno': len(learners_data) + 1,
            'name': learner.name,
            'email': lpr_dict.get(2, learner.email),
            'college': education.institution_code.name if education else 'N/A',
            'branch': education.branch_code.name if education else 'N/A',
            'year_of_graduation': education.year_of_graduation if education else 'N/A',
            'mobile': learner.mobile,
            'roll_number': education.rollno if education else 'N/A',
            'skills_boost_url': lpr_dict.get(3, '-'),
            'registration_timestamp': lpr_dict.get(6, '-'),
            'gender': learner.gender
        })

    # Download CSV
    if action == 'download':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Genai_2025_collegewise_registrations.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'S.No', 'Timestamp', 'Roll Number', 'Student Name', 'Gender', 'Mobile', 'Email',
            'Branch', 'YOG', 'Section', 'College', 'Google Skills Boost URL'
        ])
        for learner in learners_data:
            writer.writerow([
                learner['sno'], learner['registration_timestamp'], learner['roll_number'],
                learner['name'], learner['gender'], learner['mobile'], learner['email'], learner['branch'],
                learner['year_of_graduation'], learner['section'], learner['college'],
                learner['skills_boost_url']
            ])
        return response

    # Dropdown context data
    branches = sorted(le.objects.filter(learner_code_id__in=learner_ids).values_list('branch_code__name', flat=True).distinct())
    years_of_graduation = sorted(le.objects.filter(learner_code_id__in=learner_ids).values_list('year_of_graduation', flat=True).distinct())
    sections = sorted(lpr.objects.filter(program_requirement_code__id=29).values_list('value', flat=True).distinct())
    genders = l.objects.values_list('gender', flat=True).distinct()
    institutions = ins.objects.all()

        # Dynamically fetch general requirements for this program
    general_reqs = iprg.objects.filter(program_code__id=program_id)

    # Create a dynamic label-to-id map (based on name keywords)
    label_map = {
        'onboarded': 'onboarded_count',
        'active': 'active_count',
        'completion': 'program_completions',
        'beginner': 'beginner_completions',
        'intermediate': 'intermediate_completions',
        'advanced': 'advanced_completions',
    }

    metric_counts = {
        'onboarded_count': 0,
        'active_count': 0,
        'program_completions': 0,
        'beginner_completions': 0,
        'intermediate_completions': 0,
        'advanced_completions': 0,
    }

    for req in general_reqs:
        name = req.name.lower()
        for keyword, label in label_map.items():
            if keyword in name:
                value = iprs.objects.filter(
                    institution_code=college_obj,
                    institution_program_requirement_general_code=req
                ).values_list('value', flat=True).first()
                try:
                    metric_counts[label] = int(value)
                except:
                    metric_counts[label] = 0

    learning_hours = (metric_counts.get('beginner_completions', 0) * 8) + (metric_counts.get('intermediate_completions', 0) * 15) + ( metric_counts.get('advanced_completions', 0) * 19)

    available_programs = get_programs_for_institution(college_obj)
    
    return render(request, 'dashboard/collegewise_genai2025registration.html', {
        'learners': learners_data,
        'selected_branch': selected_branch,
        'selected_year': selected_year,
        'selected_section': selected_section,
        'selected_gender': selected_gender,
        'registered_count': len(learners_data),
        'branches': branches,
        'years_of_graduation': years_of_graduation,
        'sections': sections,
        'genders': genders,
        'institutions': institutions,
        'program_id': str(program_id),
        'programs': available_programs,
        "college" : college_obj,

        'onboarded_count': metric_counts.get('onboarded_count', 0),
        'active_count': metric_counts.get('active_count', 0),
        'program_completions': metric_counts.get('program_completions', 0),
        'beginner_completions': metric_counts.get('beginner_completions', 0),
        'intermediate_completions': metric_counts.get('intermediate_completions', 0),
        'advanced_completions': metric_counts.get('advanced_completions', 0),
        'learning_hours': learning_hours,
    })