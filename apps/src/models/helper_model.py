from django.db import models

class Configuration(models.Model):
    logo = models.CharField(max_length=100, blank=True, null=True)
    loader = models.TextField(blank=True, null=True)
    page_limit = models.IntegerField(blank=True, null=True)
    org_name = models.CharField(max_length=255, blank=True, null=True)
    org_footer_name = models.CharField(max_length=255, blank=True, null=True)
    org_address = models.CharField(max_length=500, blank=True, null=True)
    org_state_name = models.CharField(max_length=100, blank=True, null=True)
    org_state_code = models.CharField(max_length=10, blank=True, null=True)
    org_pan = models.CharField(max_length=10, blank=True, null=True)
    org_bank_account_no = models.CharField(max_length=50, blank=True, null=True)
    org_bank_name = models.CharField(max_length=100, blank=True, null=True)
    org_bank_branch_name = models.CharField(max_length=100, blank=True, null=True)
    org_bank_ifsc = models.CharField(max_length=20, blank=True, null=True)
    org_code = models.CharField(max_length=6, blank=True, null=True)
    org_latitude = models.CharField(max_length=50, blank=True, null=True)
    org_longitude = models.CharField(max_length=50, blank=True, null=True)
    google_app_key = models.CharField(max_length=500, blank=True, null=True)
    order_timing = models.CharField(max_length=50, blank=True, null=True)
    user_tracking_time = models.CharField(max_length=50, blank=True, null=True)
    mark_attendance_time = models.CharField(max_length=22, blank=True, null=True) 
    attendance_periphery = models.CharField(max_length=22, blank=True, null=True) 
    gstin = models.CharField(max_length=20, blank=True, null=True)
    cin = models.CharField(max_length=30, blank=True, null=True)
    fssai = models.CharField(max_length=20, blank=True, null=True)
    sms_api_url = models.TextField(blank=True, null=True)
    sms_user_id = models.CharField(max_length=100, blank=True, null=True)
    sms_password = models.CharField(max_length=100, blank=True, null=True)
    sms_sender_ids = models.CharField(max_length=255, blank=True, null=True)
    firebase_server_key = models.TextField(blank=True, null=True)
    last_update_report_time = models.DateTimeField(null=True)
    refresh_time = models.CharField(max_length=22, blank=True, null=True)
    tentative_order_timing = models.CharField(max_length=50, blank=True, null=True)
    tentative_refresh_time = models.CharField(max_length=22, blank=True, null=True)
    last_update_tentative_report_time = models.DateTimeField(null=True)
    battery_percentage = models.CharField(max_length=22, blank=True, null=True)
    travel_amount = models.IntegerField(blank=True, null=True)
    contact_number = models.CharField(max_length=22, blank=True, null=True)
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'configuration'
            

    
