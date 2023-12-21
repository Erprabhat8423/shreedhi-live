from django.db import models

# Create your models here.

class Organizations(models.Model):
    organization_name = models.CharField(max_length = 200)
    landline_country_code = models.CharField(max_length = 3, null=True)
    landline_state_code = models.CharField(max_length = 6, null=True)
    landline_number = models.CharField(max_length = 20, null=True)
    mobile_country_code = models.CharField(max_length = 6, null=True)
    mobile_number = models.CharField(max_length = 10, null=True)
    email = models.CharField(max_length = 50, null=True)
    address = models.CharField(max_length = 500, null=True)
    pincode = models.CharField(max_length = 6, null=True)
    status = models.IntegerField(default='1')
    class Meta:
            db_table = 'sp_organizations'

class Departments(models.Model):
    organization_id = models.IntegerField()
    department_name = models.CharField(max_length = 200)
    landline_country_code = models.CharField(max_length = 3, null=True)
    landline_state_code = models.CharField(max_length = 6, null=True)
    landline_number = models.CharField(max_length = 20, null=True)
    extension_number = models.CharField(max_length = 3, null=True)
    mobile_country_code = models.CharField(max_length = 6, null=True)
    mobile_number = models.CharField(max_length = 10, null=True)
    email = models.CharField(max_length = 50, null=True)
    status = models.IntegerField(default='1')
    class Meta:
            db_table = 'sp_departments'            
