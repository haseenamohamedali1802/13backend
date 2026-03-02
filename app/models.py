from django.db import models

# Create your models here.
class Status(models.Model):
    STATUS_CHOICES=[
        ('Connection Released','Connection Released'),
        ('Approved','Approved'),
        ('Pending','Pending'),
        ('Rejected','Rejected'),
    ]
    Status_Name=models.CharField(max_length=40,choices=STATUS_CHOICES)
    
    def __str__(self):
        return self.Status_Name
    
class Applicant(models.Model):
    GENDER_CHOICES=[
        ('Male','Male'),
        ('Female','Female'),
    ]
    OWNERSHIP_CHOICES=[
        ('Individual','Individual'),
        ('Joint','Joint'),
    ]
    GOVT_ID_CHOICES=[
        ('Aadhar','Aadhar'),
        ('Voter_Id','Voter_Id'),
        ('Pan','Pan'),
        ('Passport','Passport'),
    ]
    CATEGORY_CHOICES=[
        ('Residential','Residential'),
        ('Commercial','Commercial'),
    ]
    
    Applicant_Name=models.CharField(max_length=100)
    Gender=models.CharField(max_length=10,choices=GENDER_CHOICES)
    Districts=models.CharField(max_length=100)
    State=models.CharField(max_length=100)
    Pincode=models.IntegerField()
    Ownership=models.CharField(max_length=10,choices=OWNERSHIP_CHOICES)
    GotId_Type=models.CharField(max_length=20,choices=GOVT_ID_CHOICES)
    Id_Number=models.CharField(max_length=100)
    Category=models.CharField(max_length=20,choices=CATEGORY_CHOICES)
     
    def __str__(self):
         return self.Applicant_Name
     
class Connection(models.Model):
    REVIEWER_COMMENTS_CHOICES=[
        ('Installation pending','Installation pending'),
        ('Documents verification in process','Documents verification in process'),
        ('Installation completed','Installation completed'),
        ('KYC failed','KYC failed'),
    ]
    Applicant=models.ForeignKey(Applicant,on_delete=models.CASCADE)
    Load_Applied=models.IntegerField()
    Date_Of_Application=models.DateField()
    Date_of_Approval=models.DateField(null=True,blank=True)
    Modified_Date=models.DateField(null=True,blank=True)
    Status=models.ForeignKey(Status,on_delete=models.CASCADE)
    Reviewer_Id=models.IntegerField()
    Reviewer_Name=models.CharField(max_length=100)
    Reviewer_Comment=models.CharField(max_length=50,choices=REVIEWER_COMMENTS_CHOICES)
    
    def __str__(self):
        return f"Connection Id: {self.id} - Applicant: {self.Applicant}"
     