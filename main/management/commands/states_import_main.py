import csv

from django.core.management.base import BaseCommand

from main.models import State, Country

class Command (BaseCommand):

    def add_arguments(self, parser): 
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs): 
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='') as file:
            reader =  csv.DictReader(file)

            e=0
            c=0
            codes = []
            country_code = Country.objects.get(id=1)
            for row in reader:
                
                e += 1
                try:
                    code = int(row['state_code'].strip())
                except:
                    self.stdout.write(self.style.SUCCESS(e))
                else:
                    if code not in codes:
                        codes.append(code)
                        
                        name =  row['name'].strip()
                        State.objects.create(
                            name =  name,
                            code = code,
                            country_code = country_code
                        )

                        c +=1
                        self.stdout.write(self.style.SUCCESS(f'{c} - {name} - {code}'))
        self.stdout.write(self.style.SUCCESS(f'{c} States imported!'))

                        









