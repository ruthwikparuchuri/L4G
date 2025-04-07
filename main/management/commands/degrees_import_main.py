import csv
from django.core.management.base import BaseCommand
from main.models import Degree

class Command(BaseCommand):

    def add_arguments(self, parser): 
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs): 
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            c = 0
            for row in reader:
                name = row['name'].strip()
                short_name = row['short_name'].strip()

                # Ensure no duplicates
                if not Degree.objects.filter(name=name).exists():
                    Degree.objects.create(name=name, short_name=short_name)
                    c += 1
                    self.stdout.write(self.style.SUCCESS(f'{c} - {name} ({short_name}) Imported'))

        self.stdout.write(self.style.SUCCESS(f'{c} Degrees imported!'))
