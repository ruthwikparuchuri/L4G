import csv
from django.core.management.base import BaseCommand
from dashboard.models import Temp_Genai_Institutions

class Command(BaseCommand):
    help = "Import institutions data from CSV"

    def handle(self, *args, **kwargs):
        file_path = "C:/Users/HP/OneDrive/Desktop/L4G Project/venv/myproject/main/management/temp_genai_institutions.csv"


        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            records = []

            for row in reader:
                records.append(
                    Temp_Genai_Institutions(
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
                )

            Temp_Genai_Institutions.objects.bulk_create(records)
            self.stdout.write(self.style.SUCCESS("Successfully imported institutions!"))
