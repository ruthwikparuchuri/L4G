from django.contrib import admin
from .models import (
    Country, State, District, Institution, Degree, Branch, Department, Designation,
    Knowledge_Partner, Course, Module, Specialization, Specialization_Course,
    Program, Program_Specialization, Program_Requirement, Learner, 
    Learner_Education, Learner_Employment, Learner_Program_Requirement,CollegeVerificationRequest, 
    Event, Learner_Module_Progress,Learner_Course_Progress,Learner_Specialization_Progress, Learner_Program_Progress,
    Institution_Program_Requirement_General,Institution_Program_Requirement_Specific
)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country_code')
    list_filter = ('country_code',)
    search_fields = ('name', 'code')

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state_code')
    list_filter = ('state_code',)
    search_fields = ('name', 'code')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name', 'l4g_code','type','l4g_group_code','aicte_code', 'eamcet_code', 'district_code' )
    list_filter = ('district_code',)
    search_fields = ('name', 'short_name', 'aicte_code', 'eamcet_code')

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name')
    search_fields = ('name', 'short_name')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name', 'degree_code')
    list_filter = ('degree_code',)
    search_fields = ('name', 'short_name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type')
    search_fields = ('name',)

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'priority')
    search_fields = ('name',)

@admin.register(Knowledge_Partner)
class KnowledgePartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'website')
    search_fields = ('name', 'address')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'knowledge_partner_code')
    list_filter = ('knowledge_partner_code',)
    search_fields = ('name',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'course_code')
    list_filter = ('course_code',)
    search_fields = ('name',)

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'knowledge_partner_code')
    search_fields = ('name',)

@admin.register(Specialization_Course)
class SpecializationCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_code', 'specialization_code')
    list_filter = ('course_code', 'specialization_code')
    search_fields = ('course_code__name', 'specialization_code__name')

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'knowledge_partner_code')
    list_filter = ('knowledge_partner_code',)
    search_fields = ('name',)

@admin.register(Program_Specialization)
class ProgramSpecializationAdmin(admin.ModelAdmin):
    list_display = ('id', 'program_code', 'specialization_code')
    list_filter = ('program_code', 'specialization_code')
    search_fields = ('program_code__name', 'specialization_code__name')

@admin.register(Program_Requirement)
class ProgramRequirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'program_code')
    list_display_links = ('id', 'name')
    list_filter = ('program_code',)
    search_fields = ('name',)

@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'mobile', 'gender')
    search_fields = ('name', 'email', 'mobile')

@admin.register(Learner_Education)
class LearnerEducationAdmin(admin.ModelAdmin):
    list_display = ('id', 'rollno', 'learner_code', 'institution_code', 'branch_code')
    list_filter = ('institution_code', 'branch_code')
    search_fields = ('rollno', 'learner_code__name', 'institution_code__name', 'branch_code__name')

@admin.register(Learner_Employment)
class LearnerEmploymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'empid', 'learner_code', 'institution_code', 'department_code', 'designation_code')
    list_filter = ('institution_code', 'department_code', 'designation_code')
    search_fields = ('empid', 'learner_code__name', 'institution_code__name', 'department_code__name', 'designation_code__name')

@admin.register(Learner_Program_Requirement)
class LearnerProgramRequirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'learner_code', 'program_requirement_code', 'value')
    list_filter = ('program_requirement_code',)
    search_fields = ('learner_code__name', 'program_requirement_code__name','value')

@admin.register(Learner_Module_Progress)
class LearnerModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'learner_code', 'module_code', 'is_completed', 'duration', 'score')
    list_display_links = ('id', 'learner_code')
    list_filter = ('module_code', 'is_completed')
    search_fields = ('learner_code_name', 'module_code_name')

@admin.register(Learner_Course_Progress)
class LearnerCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'learner_code', 'course_code', 'is_completed', 'duration', 'score')
    list_display_links = ('id', 'learner_code')
    list_filter = ('course_code', 'is_completed')
    search_fields = ('learner_code_name', 'course_code_name')

@admin.register(Learner_Specialization_Progress)
class LearnerSpecializationProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'learner_code', 'specialization_code', 'is_completed', 'duration', 'score')
    list_display_links = ('id', 'learner_code')
    list_filter = ('specialization_code', 'is_completed')
    search_fields = ('learner_code_name', 'specialization_code_name')

@admin.register(Learner_Program_Progress)
class LearnerProgramProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'learner_code', 'program_code', 'is_enrolled', 'is_onboarded', 'is_active', 'is_completed', 'duration_hrs')
    list_display_links = ('id', 'learner_code')
    list_filter = ('program_code', 'is_enrolled', 'is_onboarded', 'is_active', 'is_completed')
    search_fields = ('learner_code_name', 'program_code_name')

@admin.register(Institution_Program_Requirement_General)
class InstitutionProgramRequirementGeneralAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_mandatory', 'program_code')
    list_display_links = ('id', 'name')
    list_filter = ('program_code', 'is_mandatory')
    search_fields = ('name', 'program_code__name')

@admin.register(Institution_Program_Requirement_Specific)
class InstitutionProgramRequirementSpecificAdmin(admin.ModelAdmin):
    list_display = ('id', 'institution_code', 'institution_program_requirement_general_code', 'value')
    list_display_links = ('id', 'institution_code')
    list_filter = ('institution_code', 'institution_program_requirement_general_code')
    search_fields = ('institution_code_name', 'institution_program_requirement_general_code_name', 'value')


@admin.register(CollegeVerificationRequest)
class CollegeVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ("data","new_institution", "mobile", "approved")
    list_filter = ("approved","new_institution")
    search_fields = ("data","new_institution", "mobile")
    actions = ["approve_college","disapprove_college"]

    def approve_college(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected verification requests approved.")

    def disapprove_college(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, "Selected verification requests disapproved.")

    approve_college.short_description = "Approve selected verification requests"
    disapprove_college.short_description = "Disapprove selected verification requests"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name','event_status', 'program_code', 'datetime', 'institution', 'venue', 'get_trainers')
    search_fields = ('event_name', 'institution__name', 'venue')

    def get_trainers(self, obj):
        return ", ".join([f"{trainer.empid} - {trainer.learner_code.name} ({trainer.learner_code.email})" for trainer in obj.trainers.all()])

    get_trainers.short_description = "Trainers"

    actions = ["set_status_ongoing","set_status_completed","set_status_scheduled","set_status_cancelled"]

    def set_status_ongoing(self, request, queryset):
        queryset.update(event_status="ongoing")
        self.message_user(request, "Selected Events status changed to Ongoing")

    def set_status_completed(self, request, queryset):
        queryset.update(event_status="completed")
        self.message_user(request, "Selected Events status changed to Completed")
    
    def set_status_scheduled(self, request, queryset):
        queryset.update(event_status="scheduled")
        self.message_user(request, "Selected Events status changed to Scheduled")

    def set_status_cancelled(self, request, queryset):
        queryset.update(event_status="cancelled")
        self.message_user(request, "Selected Events status changed to Cancelled")

    set_status_ongoing.short_description = "Set status Ongoing"
    set_status_completed.short_description = "Set status Completed"
    set_status_scheduled.short_description = "Set status Scheduled"
    set_status_cancelled.short_description = "Set status Cancelled"





# @admin.register(Trainer)
# class TrainerAdmin(admin.ModelAdmin):
#     list_display = ('l4g_id','learner', 'name', 'email', 'phone_no')
#     search_fields = ('l4g_id', 'name', 'email')