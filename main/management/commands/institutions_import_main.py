import csv

from django.core.management.base import BaseCommand

from main.models import District, Institution

class Command (BaseCommand):

    def add_arguments(self, parser): 
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs): 
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='') as file:
            reader =  csv.DictReader(file)

            c=0
            codes=[]
            names=[]
            e=[]
            for row in reader:
                name= row['CollegeName'].strip()
                code = row['L4G College Code'].strip()
                district_code = row['district_code'].strip()
                eamcet_code = row['EAMCET-Code'].strip()
                website = row['Website'].strip()

                if name not in names and code not in codes:
                    names.append(name)
                    codes.append(code)

                    # Ensure the district exists
                    try:
                        district = District.objects.get(code=district_code)
                    except District.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Skipping: {name} (District Code {district_code} not found)"))
                        continue

                    # Create institution **without specifying type**
                    Institution.objects.create(
                        name=name,
                        l4g_code=code,
                        eamcet_code=eamcet_code if eamcet_code else None,
                        website=website if website else None,
                        district_code=district
                    )

                    c += 1
                    self.stdout.write(self.style.SUCCESS(f'{c} - {name} - {code} (District: {district.name})'))

            self.stdout.write(self.style.SUCCESS(f'{c} Institutions imported!'))