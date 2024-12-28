# myapp/management/commands/import_csv.py
import csv

from django.core.management.base import BaseCommand

from detection.models import Lesion


class Command(BaseCommand):
    help = 'Import data from a CSV file into Lesion model'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file to be imported')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    age = float(row['age']) if row['age'] else None
                    age = int(age) if age is not None else None
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Invalid age value: {row['age']}"))
                    continue

                Lesion.objects.create(
                    lesion_id=row['lesion_id'],
                    image_id=row['image_id'],
                    dx=row['dx'],
                    dx_type=row['dx_type'],
                    age=age,
                    sex=row['sex'] if row['sex'] in ['male', 'female'] else None,
                    localization=row['localization']
                )
        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))
