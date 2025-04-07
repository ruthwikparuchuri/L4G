import csv

from django.core.management.base import BaseCommand

from main.models import Module, Course

class Command (BaseCommand):

    def add_arguments (self, parser): 
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs): 
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='') as file: 
            reader=csv.DictReader(file)

            c=0

            for row in reader:
                c1=Course.objects.get(id=int(row['course_code'].strip()))
                Module.objects.create( 
                    name = row['module_name'].strip(),
                    info=row['module_description'].strip(),
                    module_sequence_number = int(row['course_module_sequence'].strip()),
                    theory_practical = row['theory_practical'].strip().upper(),

                    duration_minutes = int(row['duration_hours'].strip()) * 60 + int(row['duration_minutes'].strip()),
                    course_code = c1
                )

                self.stdout.write(self.style.SUCCESS(row['module_name'].strip() + ' - Done'))

                c += 1

            self.stdout.write(self.style.SUCCESS(f'{c} Modules imported !'))

