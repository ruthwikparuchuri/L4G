import csv
import random
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from dashboard.models import UserProfile, Temp_Genai_Institutions, Temp_Genai, Branch
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Imports data from CSV files into the database"

    def handle(self, *args, **kwargs):
        # Load available branch IDs
        branch_list = list(Branch.objects.values_list('id', flat=True))

        # Import Temp_Genai_Institutions
        with open("main/management/temp_genai_institutions.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                Temp_Genai_Institutions.objects.create(
                    name=row["name"],
                    enrollments=int(row["enrollments"]),
                    onboarded=int(row["onboarded"]),
                    active=int(row["active"]),
                    pending=int(row["pending"]),
                    revoked=int(row["revoked"]),
                    declined=int(row["declined"]),
                    completions=int(row["completions"]),
                    beginner_completions=int(row["beginner_completions"]),
                    intermediate_completions=int(row["intermediate_completions"]),
                    advanced_completions=int(row["advanced_completions"]),
                    digital_badges=int(row["digital_badges"]),
                    completions_ratio=int(row["completions_ratio"]),
                )

        # Import Temp_Genai
        with open("main/management/temp_genai.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    branch_id = int(row["branch_code_id"]) if row["branch_code_id"].isdigit() else None
                    if branch_id not in branch_list:
                        branch_id = random.choice(branch_list)

                    branch = Branch.objects.get(id=branch_id)

                    Temp_Genai.objects.create(
                        name=row["name"],
                        type=row["type"],
                        rollno=row["rollno"] or None,
                        gender=row["gender"],
                        consent=row["consent"],
                        email=row["email"],
                        aadhaar_number=row["aadhaar_number"] or None,
                        mobile=row["mobile"] or None,
                        college=row["college"],
                        branch_code=branch,
                        branch_other=row["branch_other"] or None,
                        year_of_joining=int(row["year_of_joining"]) if row["year_of_joining"].isdigit() else None,
                        lateral_entry=row["lateral_entry"].lower() == "true",
                        section=row["section"] or None,
                        employee_id=row["employee_id"] or None,
                        department=row["department"] or None,
                        designation_other=row["designation_other"] or None,
                        url=row["url"] or None,
                        timestamp=row["timestamp"] or None,
                        beginner_count=int(row["beginner_count"]),
                        beginner_badges=row["beginner_badges"] or None,
                        beginner_status=row["beginner_status"] or None,
                        intermediate_count=int(row["intermediate_count"]),
                        intermediate_badges=row["intermediate_badges"] or None,
                        intermediate_status=row["intermediate_status"] or None,
                        advanced_count=int(row["advanced_count"]),
                        advanced_badges=row["advanced_badges"] or None,
                        advanced_status=row["advanced_status"] or None,
                        enrollment_status=row["enrollment_status"] or None,
                        completion_status=row["completion_status"] or None,
                        is_deleted=row["is_deleted"].lower() == "true",
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing row: {row}. Error: {e}"))

        # Import UserProfile
        with open("main/management/user_profile.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    user = User.objects.get(id=row["user_id"])
                    role_id = int(row["role_id"]) if row["role_id"].isdigit() else None
                    role = Branch.objects.get(id=role_id) if role_id in branch_list else random.choice(branch_list)

                    UserProfile.objects.create(
                        user=user,
                        is_admin=row["is_admin"].lower() == "true",
                        college=row["college"],
                        role=role,
                    )
                except ObjectDoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Skipping UserProfile entry: No user with ID {row['user_id']}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing UserProfile row: {row}. Error: {e}"))

        self.stdout.write(self.style.SUCCESS("Data import completed successfully."))