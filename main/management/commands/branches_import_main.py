import csv

from django.core.management.base import BaseCommand
from main.models import Branch, Degree

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)

            e = 0
            c = 0
            branch_names = []
            degree = Degree.objects.get(id=1)
            
            for row in reader:
                e += 1
                try:
                    name = row['name'].strip()
                    short_name = row['short_name'].strip()
                except KeyError:
                    self.stdout.write(self.style.ERROR(f'Error processing row {e}: Missing required fields'))
                else:
                    if name not in branch_names:
                        branch_names.append(name)
                        
                        Branch.objects.create(
                            name=name,
                            short_name=short_name,
                            degree_code=degree
                        )

                        c += 1
                        self.stdout.write(self.style.SUCCESS(f'{c} - {name} ({short_name})'))
        
        self.stdout.write(self.style.SUCCESS(f'{c} Branches imported!'))
