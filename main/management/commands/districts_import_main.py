import csv

from django.core.management.base import BaseCommand

from main.models import State, District

class Command (BaseCommand):

    def add_arguments(self, parser): 
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs): 
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='') as file:
            reader =  csv.DictReader(file)

            c=0
            e=0
            codes = []
            for row in reader:
                e += 1

                try:
                    district_code = int(row['district_code'].strip())
                    state_code = int(row['state_code'].strip())
                except:
                    self.stdout.write(self.style.SUCCESS(e))
                else:
                    if district_code not in codes:
                        codes.append(district_code)

                        try:
                            state = State.objects.get(code=state_code)  
                        except State.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f"Skipping row {e}: State with code {state_code} not found"))
                            continue

                        name = row['name'].strip()
                        District.objects.create(
                            name=name,
                            code=district_code,
                            state_code=state
                        )

                        c += 1
                        self.stdout.write(self.style.SUCCESS(f'{c} - {name} - {district_code} (State: {state.name})'))

        self.stdout.write(self.style.SUCCESS(f'{c} Districts imported!'))

