import csv
import os
from django.core.management.base import BaseCommand, CommandError
from main.models import (
    Institution, Learner, Learner_Education, Learner_Program_Requirement,
    Program_Requirement, Branch, Learner_Employment, Event, Program, Department,Designation,District
)
from django.db import transaction
from django.utils.dateparse import parse_datetime


class Command(BaseCommand):
    help = 'Import CSV data for learner_employment, events, or program registrations'
    

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help='Action: learner_employment, events, program_data ,import_institutions')
        parser.add_argument('csv_filename', type=str, help='CSV filename located in the same folder as this script')
        parser.add_argument('program_id', type=int, nargs='?', help='Optional program ID for program_data')

    def handle(self, *args, **options):
        action = options['action']
        csv_filename = options['csv_filename']
        program_id = options.get('program_id')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, csv_filename)

        if not os.path.exists(csv_path):
            raise CommandError(f"File not found: {csv_path}")

        if action == "learner_employment":
            self.import_learner_employment(csv_path)
        elif action == "events":
            self.import_events(csv_path)
        elif action == "program_data":
            if not program_id:
                raise CommandError("Program ID is required for 'program_data'")
            self.import_program_data(csv_path, program_id)
        elif action == "import_institutions":
            self.import_institutions(csv_path)
        else:
            raise CommandError("Invalid action. Choose from: learner_employment, events, program_data")

    def import_learner_employment(self, csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with transaction.atomic():
                for row in reader:
                    email = row['Email'].strip()
                    if not email:
                        continue

                    try:
                        learner = Learner.objects.get(email=email)
                    except Learner.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Learner not found: {email}"))
                        continue

                    try:
                        institution = Institution.objects.get(name=row['Institution'].strip())
                    except Institution.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Institution not found: {row['Institution']}"))
                        continue

                    try:
                        department = Department.objects.get(name=row['Department'].strip())
                    except Department.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Department not found: {row['Department']}"))
                        continue

                    try:
                        designation = Designation.objects.get(name=row['Designation'].strip())
                    except Designation.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Designation not found: {row['Designation']}"))
                        continue

                    year_of_joining = row['Year of Joining'].strip()
                    empid = row['Emp ID'].strip()

                    Learner_Employment.objects.update_or_create(
                        learner_code=learner,
                        defaults={
                            'empid': empid,
                            'institution_code': institution,
                            'department_code': department,
                            'designation_code': designation,
                            'year_of_joining': year_of_joining
                        }
                    )
            self.stdout.write(self.style.SUCCESS("Successfully imported learner employment data."))

    def import_events(self, csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with transaction.atomic():
                for row in reader:
                    try:
                        datetime_obj = parse_datetime(row['DateTime'].strip())
                        if not datetime_obj:
                            raise ValueError("Invalid datetime format")
                    except Exception:
                        self.stdout.write(self.style.ERROR(f"Invalid datetime for event: {row['Event Name']}"))
                        continue

                    try:
                        institution = Institution.objects.get(name=row['Institution'].strip())
                    except Institution.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Institution not found: {row['Institution']}"))
                        continue

                    program = None
                    if row.get('Program'):
                        try:
                            program = Program.objects.get(name=row['Program'].strip())
                        except Program.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Program not found: {row['Program']}"))

                    # Try to update or create event based on a unique combo (you can adjust this logic)
                    event, created = Event.objects.update_or_create(
                        event_name=row['Event Name'].strip(),
                        datetime=datetime_obj,
                        institution=institution,
                        defaults={
                            'program_code': program,
                            'duration_minutes': row.get('Duration (min)', '').strip() or None,
                            'event_url': row.get('Event URL', '').strip(),
                            'venue': row.get('Venue', '').strip(),
                            'event_status': row.get('Event Status', 'scheduled').strip().lower(),
                            'event_photo_url': row.get('Event Photo URL', '').strip(),
                            'info': ''
                        }
                    )

                    # Add Trainers
                    trainer_str = row.get('Trainers', '')
                    trainers = trainer_str.split(',') if trainer_str else []
                    for trainer_entry in trainers:
                        trainer_entry = trainer_entry.strip()
                        if not trainer_entry:
                            continue

                        try:
                            name, empid = trainer_entry.rsplit('(', 1)
                            empid = empid.rstrip(')').strip()
                            emp = Learner_Employment.objects.get(empid=empid)
                            event.trainers.add(emp)
                        except Exception:
                            self.stdout.write(self.style.WARNING(f"Trainer not found or invalid: {trainer_entry}"))

        self.stdout.write(self.style.SUCCESS("Successfully imported or updated events data."))

    def import_program_data(self, csv_path, program_id):
        program_requirements = list(
            Program_Requirement.objects.filter(program_code_id=program_id).order_by('id')
        )
        pr_names = [pr_inst.name for pr_inst in program_requirements]
        pr_name_map = {pr_inst.name: pr_inst for pr_inst in program_requirements}

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            header_fields = reader.fieldnames

            for pr_name in pr_names:
                if pr_name not in header_fields:
                    raise CommandError(f"Missing column in CSV: '{pr_name}'")

            with transaction.atomic():
                for row in reader:
                    email = row['Learner Email'].strip()
                    if not email:
                        continue

                    learner, _ = Learner.objects.update_or_create(
                        email=email,
                        defaults={
                            'name': row['Learner Name'].strip(),
                            'gender': row['Gender'].strip(),
                            'date_of_birth': row['DOB'].strip(),
                            'mobile': row['Mobile'].strip(),
                        }
                    )

                    learner.name = row['Learner Name'].strip()
                    learner.gender = row['Gender'].strip()
                    learner.date_of_birth = row['DOB'].strip()
                    learner.mobile = row['Mobile'].strip()
                    learner.save()

                    institution_id = row['Institution Name'].strip()
                    if institution_id:  # Only proceed if not empty
                        edu = Learner_Education.objects.filter(learner_code=learner).first()
                        if not edu:
                            edu = Learner_Education(learner_code=learner)

                        edu.rollno = row['Roll Number'].strip()
                        edu.year_of_joining = row['Year of Joining'].strip()
                        edu.year_of_graduation = row['Year of Graduation'].strip()

                        try:
                            edu.institution_code = Institution.objects.get(id=institution_id)
                        except Institution.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(f"Institution not found: '{institution_id}'")
                            )
                            continue

                        branch_id = row['Branch Name'].strip()
                        try:
                            branch = Branch.objects.get(id=branch_id)
                            edu.branch_code = branch
                        except Branch.DoesNotExist:
                            self.stdout.write(
                                self.style.ERROR(f"Branch not found: '{branch_id}'")
                            )
                            continue

                        edu.save()

                    # Import Program Requirements
                    for pr_name in pr_names:
                        value = row.get(pr_name, '').strip()
                        if value:
                            pr_instance = pr_name_map[pr_name]
                            Learner_Program_Requirement.objects.update_or_create(
                                learner_code=learner,
                                program_requirement_code=pr_instance,
                                defaults={'value': value}
                            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported program registration data for Program {program_id}"
            )
        )

    def import_institutions(self, csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with transaction.atomic():
                for row in reader:
                    name = row.get('Name', '').strip()
                    if not name:
                        self.stdout.write(self.style.ERROR("Skipping row with missing institution name"))
                        continue

                    district_name = row.get('District', '').strip()
                    district = None
                    if district_name:
                        try:
                            district = District.objects.get(name=district_name)
                        except District.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"District not found: {district_name}"))

                    institution = Institution(
                        id=int(row.get('ID', '').strip()),
                        name=name,
                        short_name=row.get('Short Name', '').strip(),
                        aicte_code=row.get('AICTE Code', '').strip() or None,
                        eamcet_code=row.get('EAMCET Code', '').strip(),
                        l4g_code=row.get('L4G Code', '').strip(),
                        l4g_group_code=row.get('L4G Group Code', '').strip(),
                        type1=row.get('Type', '').strip(),
                        address=row.get('Address', '').strip(),
                        website=row.get('Website', '').strip(),
                        latlong=row.get('LatLong', '').strip(),
                        district_code=district
                    )
                    institution.save()
                    self.stdout.write(self.style.SUCCESS(f"Created Institution: {name} (ID={institution.id})"))

                # Reset the sequence after inserting all records
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE sqlite_sequence SET seq=(SELECT MAX(id) FROM main_institution) WHERE name='main_institution';"
                    )

        self.stdout.write(self.style.SUCCESS("Successfully imported institutions data."))