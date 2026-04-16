import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import Applicant, Connection, Status


class Command(BaseCommand):
    help = 'Load applicant data from CSV file'

    def handle(self, *args, **options):
        filepath = os.path.join(settings.BASE_DIR, "applicant_data_records.csv")
        
        if not os.path.exists(filepath):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {filepath}'))
            return

        status_list = [
            "Rejected",
            "Connection Released",
            "Pending",
            "Approved"
        ]

        for s in status_list:
            Status.objects.get_or_create(Status_Name=s)

        count = 0
        with open(filepath, 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    applicant, created = Applicant.objects.get_or_create(
                        Applicant_Name=row["Applicant_Name"],
                        Gender=row["Gender"],
                        Districts=row["District"],
                        State=row["State"],
                        Pincode=int(row["Pincode"]),
                        Ownership=row["Ownership"],
                        GotId_Type=row["GovtId_Type"],
                        Id_Number=str(row["ID_Number"]),
                        Category=row["Category"],
                    )

                    status_value = row.get("Status", "Pending") or "Pending"
                    status = Status.objects.get(Status_Name=status_value)

                    Date_Of_Application = datetime.strptime(
                        str(row["Date_Of_Application"]), "%d-%m-%Y"
                    ).strftime("%Y-%m-%d")

                    Date_of_Approval = None
                    if row["Date_of_Approval"] and row["Date_of_Approval"].strip():
                        Date_of_Approval = datetime.strptime(
                            str(row["Date_of_Approval"]), "%d-%m-%Y"
                        ).strftime("%Y-%m-%d")

                    Modified_Date = datetime.strptime(
                        str(row["Modified_Date"]), "%d-%m-%Y"
                    ).strftime("%Y-%m-%d")

                    Connection.objects.get_or_create(
                        Applicant=applicant,
                        Status=status,
                        Load_Applied=row["Load_Applied"],
                        Date_Of_Application=Date_Of_Application,
                        Date_of_Approval=Date_of_Approval,
                        Modified_Date=Modified_Date,
                        Reviewer_Id=row["Reviewer_Id"],
                        Reviewer_Name=row["Reviewer_Name"],
                        Reviewer_Comment=row["Reviewer_Comment"],
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error on row: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} records'))
