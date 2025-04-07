import random
import datetime
from django.core.management.base import BaseCommand
from main.models import Learner, Learner_Education, Institution, Branch  # Replace 'your_app' with the actual app name

def generate_random_rollno():
    return str(random.randint(1, 999))  # 1 to 3 digit number

def generate_year_of_joining():
    current_year = datetime.date.today().year
    return random.randint(current_year + 1, current_year + 4)

class Command(BaseCommand):
    help = "Assign learners to the Learner_Education model"

    def handle(self, *args, **kwargs):
        # Fetch learners who are not yet assigned to Learner_Education
        unassigned_learners = Learner.objects.exclude(id__in=Learner_Education.objects.values_list('learner_code_id', flat=True))
        institution = Institution.objects.filter(name="Bapatla Engineering College").first()
        branches = list(Branch.objects.all())

        if not institution:
            self.stdout.write(self.style.ERROR("Institution 'Bapatla Engineering College' not found!"))
            return

        if not branches:
            self.stdout.write(self.style.ERROR("No branches found in the database!"))
            return

        count = 0
        for learner in unassigned_learners:
            year_of_joining = generate_year_of_joining()
            year_of_graduation = year_of_joining + 4
            branch = random.choice(branches)

            Learner_Education.objects.create(
                rollno=generate_random_rollno(),
                year_of_joining=year_of_joining,
                year_of_graduation=year_of_graduation,
                learner_code=learner,
                institution_code=institution,
                branch_code=branch
            )
            count += 1
            self.stdout.write(self.style.SUCCESS(f"Assigned Learner {learner.name} to {institution.name} ({branch.name})"))

        self.stdout.write(self.style.SUCCESS(f"Successfully assigned {count} learners to Learner_Education!"))
