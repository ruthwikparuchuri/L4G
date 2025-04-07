import csv
from django.core.management.base import BaseCommand
from dashboard.models import Branch  # Import the correct model

class Command(BaseCommand):
    help = "Import branches from a CSV file into the Branch model"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                e = 0  # Count total processed rows
                c = 0  # Count successfully added branches
                branch_names = []

                for row in reader:
                    e += 1
                    try:
                        name = row['name'].strip()
                        short_name = row['short_name'].strip()
                    except KeyError:
                        self.stdout.write(self.style.ERROR(f'❌ Error in row {e}: Missing required fields'))
                        continue

                    if name not in branch_names:
                        branch_names.append(name)

                        # Create and save the Branch object
                        Branch.objects.create(
                            name=name,
                            short_name=short_name
                        )

                        c += 1
                        self.stdout.write(self.style.SUCCESS(f'✅ {c} - {name} ({short_name})'))

            self.stdout.write(self.style.SUCCESS(f'🎉 {c} Branches successfully imported!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ File not found: {csv_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Unexpected error: {e}"))
