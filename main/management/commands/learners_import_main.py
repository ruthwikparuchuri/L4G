import csv
import random
import datetime
from django.core.management.base import BaseCommand
from main.models import Learner  # Replace 'your_app' with the actual app name

def generate_random_mobile():
    return str(random.choice([6, 7, 8, 9])) + ''.join(random.choices('0123456789', k=9))

def generate_random_aadhaar():
    return ''.join(random.choices('0123456789', k=12))

def generate_random_dob():
    today = datetime.date.today()
    min_birth_year = today.year - 18  # Ensure age > 18
    random_year = random.randint(1950, min_birth_year)
    random_month = random.randint(1, 12)
    random_day = random.randint(1, 28)
    return datetime.date(random_year, random_month, random_day)

class Command(BaseCommand):
    help = "Import learners from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file_path", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        file_path = kwargs["csv_file_path"]
        
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.get("Name", "").strip()
                email = row.get("Email", "").strip()
                gender = row.get("Gender", "O").strip()

                if not name or not email:
                    self.stdout.write(f"Skipping row due to missing data: {row}")
                    continue  # Skip rows with missing essential data

                learner, created = Learner.objects.get_or_create(
                    email=email,
                    defaults={
                        "name": name,
                        "mobile": generate_random_mobile(),
                        "gender": gender,
                        "date_of_birth": generate_random_dob(),
                        "aadhaar_number": int(generate_random_aadhaar()),
                    },
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Successfully created record for {name} ({email})"))
                else:
                    self.stdout.write(self.style.WARNING(f"Record already exists for {name} ({email}), skipping"))

        self.stdout.write(self.style.SUCCESS("CSV import process completed successfully!"))
