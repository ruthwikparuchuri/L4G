import csv
from django.core.management.base import BaseCommand
from main.models import Learner, Learner_Program_Requirement, Program_Requirement

CSV_FILE_PATH = "C:/Users/HP/OneDrive/Desktop/L4G Project/venv/myproject/main/management/genai_registration_data_BEC.csv"  # Update with actual path

class Command(BaseCommand):
    help = "Assigns program requirements to learners"

    def handle(self, *args, **kwargs):
        # Read CSV data into a dictionary using email as key
        csv_data = {}
        with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_data[row["Email"]] = {
                    "Email": row.get("Email", ""),
                    "URL": row.get("URL", ""),
                    "Timestamp": row.get("Timestamp", "")
                }

        # Fetch six program requirements ordered by id
        program_requirements = list(Program_Requirement.objects.all().order_by("id")[:6])
        if len(program_requirements) < 6:
            self.stdout.write(self.style.ERROR("Not enough program requirements found!"))
            return

        # Iterate over each learner
        learners = Learner.objects.all()
        for learner in learners:
            learner_email = learner.email
            email_data = csv_data.get(learner_email, {})

            # Iterate through all six program requirements for this learner
            for i, program_req in enumerate(program_requirements):
                if i == 0:
                    value = "yes"
                elif i == 1:
                    value = email_data.get("Email", "")
                elif i == 2:
                    value = email_data.get("URL", "")
                elif i == 3:
                    value = "good"
                elif i == 4:
                    value = "yes"
                elif i == 5:
                    value = email_data.get("Timestamp", "")
                else:
                    value = ""

                # Create or update record for this learner and requirement
                Learner_Program_Requirement.objects.update_or_create(
                    learner_code=learner,
                    program_requirement_code=program_req,
                    defaults={"value": value}
                )

        self.stdout.write(self.style.SUCCESS("Successfully assigned requirements to learners!"))
