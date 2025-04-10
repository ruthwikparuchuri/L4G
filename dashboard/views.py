from django.http import HttpResponseForbidden, HttpResponse
from datetime import datetime as dt
from django.shortcuts import render, redirect
#from django.contrib.auth import authenticate, login
#from django.contrib.auth.decorators import login_required
from .models import Temp_Genai_Institutions as tgi, Branch, UserProfile, Temp_Genai as learners
from main.models import Learner as l, Learner_Education as le, Institution as ins, Learner_Program_Requirement as lpr, Branch as b, Program_Requirement as pr
import csv
from django.utils.timezone import make_aware
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render
from main.models import Learner_Program_Progress,Learner_Module_Progress,Learner_Course_Progress,Learner_Specialization_Progress
from main.models import Learner_Employment




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


#@login_required
def filter_registration_data(request):
  
   learner_data = le.objects.all()  
   final = {}

 
   college = request.GET.get('college')
   branch = request.GET.get('branch')
   gender = request.GET.get('gender')
   yog = request.GET.get('yog')
   start_date = request.GET.get('start_date')
   end_date = request.GET.get('end_date')
   #print(college, branch)
   if college:
        college = ins.objects.get(id=college)
        learner_data = learner_data.filter(institution_code=college)

   if branch:
        branch = b.objects.get(id=branch)
        learner_data = learner_data.filter(branch_code=branch)

   if gender:
        learner_data = learner_data.filter(learner_code__gender=gender)
    
   if yog:  # 🟢 MODIFIED: Apply filter for a single YOG value
        learner_data = learner_data.filter(year_of_graduation=yog)

  
  
   for i in learner_data:
       learner = i.learner_code
       pr3 = pr.objects.get(id=3)
       pr2 = pr.objects.get(id=2)
       pr6 = pr.objects.get(id=6)
       learner_lpr_email = lpr.objects.filter(learner_code = learner).get(program_requirement_code=pr2).value
       learner_lpr_url = lpr.objects.filter(learner_code=learner).get(program_requirement_code=pr3).value
       learner_lpr_timestamp = lpr.objects.filter(learner_code=learner).get(program_requirement_code=pr6).value
       yog = i.year_of_graduation

       if learner_lpr_timestamp:
            try:
                timestamp_date = datetime.strptime(learner_lpr_timestamp, "%d-%m-%Y %H:%M")
                timestamp_date = make_aware(timestamp_date) if timezone.is_naive(timestamp_date) else timestamp_date
            except ValueError:
                continue  # Skip invalid date format

            if start_date:
                start_date_parsed = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
                start_date_parsed = start_date_parsed.replace(hour=0, minute=0)  # Start of day
                if timestamp_date < start_date_parsed:
                    continue  # Skip records before the start date

            if end_date:
                end_date_parsed = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
                end_date_parsed = end_date_parsed.replace(hour=23, minute=59)  # End of day
                if timestamp_date > end_date_parsed:
                    continue  # Skip records after the end date


       #Dictionary of Dictionaries
       final[learner_lpr_email] = { 'name':learner.name, 'rollno': i.rollno, 'college': i.institution_code.name, 'branch': i.branch_code.short_name, 'url': learner_lpr_url, 'timestamp': learner_lpr_timestamp, 'mobile': learner.mobile, 'gender': learner.gender, 'yog': yog}
       
    

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
    completions_count = Learner_Program_Progress.objects.filter(program_code_id=2, completed=True).count()

    beginner = Learner_Course_Progress.objects.filter(course_code_id=1, completed=True).count()
    intermediate = Learner_Course_Progress.objects.filter(course_code_id=2, completed=True).count()
    advanced = Learner_Course_Progress.objects.filter(course_code_id=3, completed=True).count()

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
        completions = progress_qs.filter(completed=True).count()

        beginner = Learner_Course_Progress.objects.filter(
            learner_code__in=learner_ids, course_code_id=1, completed=True).count()
        intermediate = Learner_Course_Progress.objects.filter(
            learner_code__in=learner_ids, course_code_id=2, completed=True).count()
        advanced = Learner_Course_Progress.objects.filter(
            learner_code__in=learner_ids, course_code_id=3, completed=True).count()

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
  
"""






"""

