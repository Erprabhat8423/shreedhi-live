from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'

class SpActivityLogs(models.Model):
    module = models.CharField(max_length=100, blank=True, null=True)
    sub_module = models.CharField(max_length=100, blank=True, null=True)
    heading = models.TextField()
    activity = models.TextField()
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=150)
    icon = models.CharField(max_length=100, blank=True, null=True)
    platform = models.CharField(max_length=50)
    platform_icon = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        managed = False
        db_table = 'sp_activity_logs'



class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, on_delete=models.CASCADE)
    permission = models.ForeignKey('AuthPermission', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.CASCADE)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    group = models.ForeignKey(AuthGroup, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    permission = models.ForeignKey(AuthPermission, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

class SpAddresses(models.Model):
    user = models.OneToOneField('SpUsers', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=250, blank=True, null=True)
    country = models.ForeignKey('SpCountries', on_delete=models.CASCADE)
    country_name = models.CharField(max_length=100)
    state = models.ForeignKey('SpStates', on_delete=models.CASCADE)
    state_name = models.CharField(max_length=100)
    city = models.ForeignKey('SpCities', on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100)
    pincode = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        managed = False
        db_table = 'sp_addresses'


class SpAttendanceConfigs(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    attendance_image_1 = models.CharField(max_length=255)
    attendance_image_2 = models.CharField(max_length=255)
    attendance_image_3 = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_attendance_configs'

class SpGst(models.Model):
    gst = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_gst'


class SpBasicDetails(models.Model):
    user_id = models.IntegerField()
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    marriage_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=25, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_nubmer = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    cin = models.CharField(max_length=20, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    fssai = models.CharField(max_length=20, blank=True, null=True)
    working_shift_id = models.IntegerField(blank=True, null=True)
    working_shift_name = models.CharField(max_length=50, blank=True, null=True)
    order_timing = models.CharField(max_length=50, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    gumasta_number = models.CharField(max_length=14, blank=True, null=True)
    gumasta_expiry_date = models.DateField(blank=True, null=True)
    fssai_expiry_Date = models.DateField(blank=True, null=True)
    personal_email = models.CharField(max_length=50, blank=True, null=True)
    outlet_owned = models.CharField(max_length=50, blank=True, null=True)
    outstanding_amount = models.FloatField(blank=True, null=True)
    security_amount = models.FloatField(blank=True, null=True)
    opening_crates = models.IntegerField(blank=True, null=True)
    production_unit_id = models.CharField(max_length=11, blank=True, null=True)
    tcs_applicable = models.IntegerField(default= 0)
    tcs_value = models.FloatField(blank=True, null=True)
    per_crate_incentive = models.IntegerField(blank=True, null=True)
    leave_count = models.IntegerField(blank=True, null=True)
    week_of_day = models.CharField(max_length=22, blank=True, null=True)
    vehicle_id = models.IntegerField(blank=True, null=True)
    vehilcle_number = models.CharField(max_length=10, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_basic_details'
        
# class SpUserLedger(models.Model):
#     user_id = models.IntegerField()
#     particulars = models.TextField()
#     payment_note = models.TextField(blank=True, null=True)
#     payment_receipt = models.CharField(max_length=255, blank=True, null=True)
#     credit = models.DecimalField(max_digits=10, decimal_places=2)
#     debit = models.DecimalField(max_digits=10, decimal_places=2)
#     balance = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_mode = models.CharField(max_length=255, blank=True, null=True)
#     collector_type = models.IntegerField()
#     credited_by = models.IntegerField()
#     created_at = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'sp_user_ledger'
class SpUserLedger(models.Model):
    user_id = models.IntegerField()
    order_id = models.BigIntegerField()
    invoice_no = models.CharField(max_length=100)
    particulars = models.TextField()
    payment_note = models.TextField(blank=True, null=True)
    payment_mode_id = models.IntegerField(blank=True, null=True)
    organization_id = models.IntegerField()
    bank_id = models.IntegerField(blank=True, null=True)
    note_type = models.IntegerField(blank=True, null=True)
    payment_receipt = models.CharField(max_length=255, blank=True, null=True)
    credit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    debit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.IntegerField()
    order_date = models.DateField()
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_ledger'
 
        
class SpBulkpackSchemeBifurcation(models.Model):
    bulkpack_scheme_id = models.IntegerField()
    above_upto_quantity = models.IntegerField()
    incentive_amount = models.FloatField()

    class Meta:
        managed = False
        db_table = 'sp_bulkpack_scheme_bifurcation'


class SpBulkpackSchemes(models.Model):
    name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=100)
    route_id = models.CharField(max_length=100)
    town_id = models.CharField(max_length=100)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(blank=True, null=True)
    unit_id = models.IntegerField()
    unit_name = models.CharField(max_length=50)
    product_class_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_bulkpack_schemes'


class SpCities(models.Model):
    state = models.ForeignKey('SpStates', on_delete=models.CASCADE)
    state_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_cities'

class Sp_Mode_Of_Payments(models.Model):
    mode_of_payment = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_mode_of_payments'        

class SpColorCodes(models.Model):
    color = models.CharField(max_length=50)
    code = models.CharField(max_length=15)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_color_codes'

class SpContactNumbers(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    country_code = models.CharField(max_length=10)
    contact_type = models.CharField(max_length=50)
    contact_type_name = models.CharField(max_length=25, blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    is_primary = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_contact_numbers'


class SpContactPersons(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    contact_person_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_contact_persons'


class SpContactTypes(models.Model):
    contact_type = models.CharField(max_length=100)
    status = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_contact_types'


class SpCountries(models.Model):
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_countries'

class SpContainers(models.Model):
    container = models.CharField(max_length=100)
    is_returnable = models.IntegerField(null=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_containers'

class SpPackagingType(models.Model):
    packaging_type = models.CharField(max_length=100)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_packaging_type'

class SpMainRoutes(models.Model):
    main_route = models.CharField(max_length=255)
    main_route_code = models.CharField(max_length=222,blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    sub_route = models.CharField(max_length=100,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_main_routes'
        
class SpDepartments(models.Model):
    organization = models.ForeignKey('SpOrganizations', on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=150)
    department_name = models.CharField(max_length=100)
    landline_country_code = models.CharField(max_length=10)
    landline_state_code = models.CharField(max_length=10)
    landline_number = models.CharField(max_length=15)
    extension_number = models.CharField(max_length=10)
    mobile_country_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_departments'


class SpDistributorAreaAllocations(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    zone = models.ForeignKey('SpZones', on_delete=models.CASCADE)
    zone_name = models.CharField(max_length=100)
    town = models.ForeignKey('SpTowns', on_delete=models.CASCADE)
    town_name = models.CharField(max_length=100, null=True)
    route_id = models.IntegerField()
    route_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_distributor_area_allocations'


class SpDistributorProducts(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    sku_code = models.CharField(max_length=50)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=100)
    product_variant_id = models.CharField(max_length=50)
    product_mrp = models.FloatField()
    product_sale_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_distributor_products'


class SpDriverAddresses(models.Model):
    user_id = models.IntegerField()
    type = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=250, blank=True, null=True)
    country_id = models.IntegerField()
    country_name = models.CharField(max_length=100)
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    city_id = models.IntegerField()
    city_name = models.CharField(max_length=100)
    pincode = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_driver_addresses'


class SpDriverBasicDetails(models.Model):
    driver_id = models.IntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=25, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_nubmer = models.CharField(max_length=15, blank=True, null=True)
    aadhaar_document = models.CharField(max_length=255, blank=True, null=True)
    dl_number = models.CharField(max_length=50, blank=True, null=True)
    dl_document = models.CharField(max_length=255, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    personal_email = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_driver_basic_details'


class SpDriverContactNumbers(models.Model):
    user_id = models.IntegerField()
    country_code = models.CharField(max_length=10)
    contact_type = models.IntegerField()
    contact_type_name = models.CharField(max_length=25, blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    is_primary = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_driver_contact_numbers'


class SpDrivers(models.Model):
    salutation = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    primary_contact_number = models.CharField(max_length=25)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    device_id = models.CharField(max_length=50, blank=True, null=True)
    firebase_token = models.CharField(max_length=255, blank=True, null=True)
    web_auth_token = models.CharField(max_length=255, blank=True, null=True)
    auth_otp = models.CharField(max_length=10, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    last_ip = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    production_unit_id = models.IntegerField()
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_drivers'

class SpFavorites(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    favorite = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_favorites'

class SpFinancialYears(models.Model):
    financial_year = models.CharField(max_length=100)
    start_month = models.IntegerField()
    start_month_name = models.CharField(max_length=50)
    start_year = models.IntegerField()
    end_month = models.IntegerField()
    end_month_name = models.CharField(max_length=50)
    end_year = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_financial_years'

class SpFlatSchemes(models.Model):
    name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=100)
    is_route = models.IntegerField(blank=True, null=True)
    main_route_id = models.CharField(max_length=500,blank=True, null=True)
    route_id = models.CharField(max_length=500,blank=True, null=True)
    zone_id = models.CharField(max_length=500,blank=True, null=True)
    town_id = models.CharField(max_length=500,blank=True, null=True)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(blank=True, null=True)
    incentive_amount = models.FloatField()
    unit_id = models.IntegerField()
    unit_name = models.CharField(max_length=50)
    product_class_id = models.CharField(max_length=50, blank=True, null=True)
    applied_on_variant_id = models.IntegerField(blank=True, null=True)
    applied_on_variant_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_flat_schemes'



class SpFuelType(models.Model):
    fuel_type = models.CharField(max_length=100)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_fuel_type'

class SpHoReport(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    product_variant_id = models.IntegerField()
    quantity = models.BigIntegerField(blank=True, null=True)
    foc_pouch = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_ho_report'


class SpHoReportHistory(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    product_variant_id = models.IntegerField()
    quantity = models.BigIntegerField(blank=True, null=True)
    foc_pouch = models.BigIntegerField(blank=True, null=True)
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_ho_report_history'

class SpHolidayTypes(models.Model):
    holiday_type = models.CharField(max_length=100)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_holiday_types'


class SpHolidays(models.Model):
    holiday_type_id = models.IntegerField()
    holiday_type = models.CharField(max_length=100)
    holiday = models.CharField(max_length=100)
    start_date = models.DateField()
    start_time = models.CharField(max_length=10, blank=True, null=True)
    end_date = models.DateField()
    end_time = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    holiday_status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_holidays'

class SpInsuranceCoverage(models.Model):
    insurance_coverage = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'sp_insurance_coverage'


class SpLicenseCategory(models.Model):
    license_category = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'sp_license_category'

class SpModulePermissions(models.Model):
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    workflow = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_module_permissions'

class SpModules(models.Model):
    module_name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_modules'

class SpNotifications(models.Model):
    row_id = models.IntegerField(blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    module = models.CharField(max_length=100, blank=True, null=True)
    sub_module = models.CharField(max_length=100, blank=True, null=True)
    heading = models.TextField()
    activity = models.TextField()
    activity_image = models.CharField(max_length=255, blank=True, null=True)
    from_user_id = models.IntegerField()
    from_user_name = models.CharField(max_length=150)
    to_user_id = models.IntegerField()
    to_user_type = models.IntegerField(default=1,null=True)
    to_user_name = models.CharField(max_length=150)
    icon = models.CharField(max_length=100, blank=True, null=True)
    platform = models.CharField(max_length=50)
    platform_icon = models.CharField(max_length=100)
    read_status = models.IntegerField(default=1)
    notification_type = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_notifications'
        
class SpOdoMeter(models.Model):
    driver_id = models.IntegerField()
    vehicle_id = models.IntegerField()
    odo_meter_pic = models.CharField(max_length=150, blank=True, null=True)
    odo_meter_reading = models.IntegerField()
    fuel_quantity_ltrs = models.FloatField()
    fuel_status = models.CharField(max_length=20)
    card_no = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    date_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_odo_meter'

class SpOrderCrateApproval(models.Model):
    order_id = models.IntegerField(blank=True, null=True)
    transporter_id = models.IntegerField()
    driver_id = models.IntegerField()
    driver_name = models.CharField(max_length=222)
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=222)
    delivered_normal = models.IntegerField(blank=True, null=True)
    delivered_jumbo = models.IntegerField(blank=True, null=True)
    received_normal = models.IntegerField(blank=True, null=True)
    received_jumbo = models.IntegerField(blank=True, null=True)
    status = models.IntegerField()
    updated_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_order_crate_approval'
        
class SpOrderDetails(models.Model):
    order_id = models.IntegerField()
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    product_variant_id = models.IntegerField()
    product_variant_name = models.CharField(max_length=255)
    product_variant_size = models.CharField(max_length=255)
    product_no_of_pouch = models.IntegerField()
    product_container_size = models.CharField(max_length=100)
    product_container_type = models.CharField(max_length=50)
    product_packaging_type_name = models.CharField(max_length=100, null=True)
    quantity = models.FloatField()
    rate = models.FloatField()
    amount = models.FloatField()
    quantity_in_pouch = models.IntegerField(null=True)
    quantity_in_ltr = models.FloatField(blank=True, null=True)
    packaging_type = models.CharField(max_length=50)
    is_allow = models.IntegerField(null=True)
    tally_export_type = models.IntegerField(default=0,null=True)
    order_date = models.DateTimeField()
    gst = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_order_details'
        unique_together = ["order_id", "product_variant_id"]

class SpUserModulePermissions(models.Model):
    user_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    workflow = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_module_permissions'

class SpOrderSchemes(models.Model):
    order_id = models.IntegerField()
    scheme_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()
    scheme_type = models.CharField(max_length=50)
    variant_id = models.IntegerField(blank=True, null=True)
    on_order_of = models.IntegerField(blank=True, null=True)
    free_variant_id = models.IntegerField(blank=True, null=True)
    free_variant_container_type = models.CharField(max_length=50, blank=True, null=True)
    free_variant_packaging_type = models.CharField(max_length=100, blank=True, null=True)
    free_variant_container_size = models.CharField(max_length=100, blank=True, null=True)
    container_quantity = models.IntegerField(blank=True, null=True)
    pouch_quantity = models.IntegerField(blank=True, null=True)
    quantity_in_ltr = models.FloatField(blank=True, null=True)
    incentive_amount = models.FloatField(blank=True, null=True)
    unit_id = models.IntegerField(blank=True, null=True)
    unit_name = models.CharField(max_length=50, blank=True, null=True)
    product_id = models.IntegerField(blank=True, null=True)
    product_class_id = models.CharField(max_length=50, blank=True, null=True)
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_order_schemes'


class SpOrders(models.Model):
    order_code = models.CharField(max_length=255)
    user_id = models.IntegerField()
    user_sap_id = models.CharField(max_length=10)
    user_name = models.CharField(max_length=150)
    user_type = models.CharField(max_length=50)
    town_id = models.IntegerField()
    town_name = models.CharField(max_length=100)
    route_id = models.IntegerField()
    route_name = models.CharField(max_length=100)
    transporter_name = models.CharField(max_length=200)
    transporter_details = models.CharField(max_length=800)
    vehicle_no = models.CharField(max_length=20)
    order_date = models.DateTimeField()
    order_status = models.IntegerField(default=1)
    order_shift_id = models.IntegerField()
    order_shift_name = models.CharField(max_length=255)
    order_scheme_id = models.IntegerField(null=True)
    order_total_amount = models.FloatField()
    order_items_count = models.IntegerField()
    mode_of_payment = models.CharField(max_length=100)
    amount_to_be_paid = models.FloatField()
    revised_amount = models.FloatField(blank=True, null=True)
    outstanding_amount = models.FloatField(blank=True, null=True)
    production_unit_id = models.IntegerField(blank=True, null=True)
    production_unit_name = models.CharField(max_length=222,blank=True, null=True)
    platform_updated = models.CharField(max_length=45,blank=True, null=True)
    platfrom_created = models.CharField(max_length=45,blank=True, null=True)
    indent_status = models.IntegerField(default=0)
    block_unblock = models.IntegerField()
    dispatch_order_status = models.IntegerField(default=0, null=True)
    tcs_value = models.FloatField(blank=True, null=True)
    updated_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_orders'

class SpOrderOtp(models.Model):
    vehicle_id = models.IntegerField()
    order_id = models.IntegerField()
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_order_otp'

class SpChallans(models.Model):
    production_unit_id = models.IntegerField(blank=True, null=True)
    organization_id    = models.IntegerField(blank=True, null=True)
    invoice_no = models.CharField(max_length=100)
    user_id = models.IntegerField()
    vehicle_id = models.IntegerField()
    invoice_type = models.CharField(max_length=100)
    invoice_path = models.CharField(max_length=500)
    created_date = models.DateTimeField()
    status = models.IntegerField()
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_challans'        
class SpInvoices(models.Model):
    production_unit_id = models.IntegerField(blank=True, null=True)
    organization_id = models.IntegerField(blank=True, null=True)
    invoice_no = models.CharField(max_length=100, blank=True, null=True)
    user_id = models.IntegerField()
    route_id = models.IntegerField(blank=True, null=True)
    invoice_type = models.CharField(max_length=100)
    invoice_path = models.CharField(max_length=500)
    invoice_amount = models.FloatField()
    taxable_amount = models.FloatField(blank=True, null=True)
    final_amount = models.FloatField()
    cgst = models.FloatField(blank=True, null=True)
    sgst = models.FloatField(blank=True, null=True)
    created_date = models.DateField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_invoices'  

class SpUserAttendance(models.Model):
    user_id = models.IntegerField()
    attendance_date_time = models.DateTimeField()
    start_time = models.CharField(max_length=50, blank=True, null=True)
    end_time = models.CharField(max_length=50, blank=True, null=True)
    dis_ss_id = models.IntegerField(blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_attendance'
        
class SpTimeSlots(models.Model):
    start_timing = models.TimeField(null=True)
    end_timing = models.TimeField(null=True)
    timing_order = models.IntegerField(null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_time_slots'        

class SpOrganizations(models.Model):
    organization_name = models.CharField(max_length=150)
    invoice_serial_no = models.CharField(max_length=50,blank=True, null=True)
    landline_country_code = models.CharField(max_length=10)
    landline_state_code = models.CharField(max_length=10)
    landline_number = models.CharField(max_length=15)
    mobile_country_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=8, blank=True, null=True)
    is_sister_concern = models.IntegerField(default=0,null=True)
    is_primary_company = models.IntegerField(default=0,null=True)
    org_bank_account_no = models.CharField(max_length=50, blank=True, null=True)
    org_bank_name = models.CharField(max_length=100, blank=True, null=True)
    org_bank_branch_name = models.CharField(max_length=100, blank=True, null=True)
    org_bank_ifsc = models.CharField(max_length=20, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_organizations'

class SpPasswordResets(models.Model):
    email = models.CharField(max_length=100,blank=True, null=True)
    auth_token = models.CharField(max_length=100,blank=True, null=True)
    mobile = models.CharField(max_length=10,blank=True, null=True)
    otp = models.IntegerField(blank=True, null=True)
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_password_resets'
        
class SpPermissionWorkflowRoles(models.Model):
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    level_id = models.IntegerField()
    workflow_level_dept_id = models.IntegerField(blank=True, null=True)
    workflow_level_dept_name = models.CharField(max_length=100, blank=True, null=True)
    workflow_level_role_id = models.IntegerField()
    workflow_level_role_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'sp_permission_workflow_roles'

class SpPlantCrateLedger(models.Model):
    plant_user_id = models.IntegerField()
    transporter_id = models.IntegerField()
    driver_id = models.IntegerField()
    driver_name = models.CharField(max_length=222)
    user_id = models.IntegerField()
    normal_credit = models.IntegerField()
    normal_debit = models.IntegerField()
    normal_balance = models.IntegerField()
    jumbo_credit = models.IntegerField()
    jumbo_debit = models.IntegerField()
    jumbo_balance = models.IntegerField()
    is_route = models.IntegerField()
    updated_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_plant_crate_ledger'
        
class SpPermissionWorkflows(models.Model):
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_permission_workflows'

class SpPermissions(models.Model):
    permission = models.CharField(max_length=100)
    slug = models.CharField(max_length=150)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_permissions'

class SpProductClass(models.Model):
    product_class = models.CharField(max_length=50)
    product_hsn = models.CharField(max_length=50, blank=True, null=True)
    order_of = models.IntegerField(null=True)
    unit = models.CharField(max_length=10, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_product_class'

class SpProductUnits(models.Model):
    unit = models.CharField(max_length=100)
    largest_unit = models.CharField(max_length=50)
    conversion_value = models.FloatField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_product_units'

class SpProductVariantImages(models.Model):
    product_variant = models.ForeignKey('SpProductVariants', models.DO_NOTHING)
    image_url = models.CharField(max_length=255)
    thumbnail_url = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_product_variant_images'


class SpProductVariants(models.Model):
    product = models.ForeignKey('SpProducts', models.DO_NOTHING)
    product_name = models.CharField(max_length=50)
    product_class_id = models.IntegerField()
    container = models.ForeignKey(SpContainers, models.DO_NOTHING)
    container_name = models.CharField(max_length=50)
    packaging_type = models.ForeignKey(SpPackagingType, models.DO_NOTHING)
    packaging_type_name = models.CharField(max_length=50)
    item_sku_code = models.CharField(max_length=25)
    variant_quantity = models.IntegerField()
    variant_unit_id = models.IntegerField()
    variant_unit_name = models.CharField(max_length=25)
    largest_unit_name = models.CharField(max_length=50)
    variant_name = models.CharField(max_length=255)
    order_of = models.IntegerField(null=True)
    variant_size = models.CharField(max_length=255)
    no_of_pouch = models.IntegerField()
    container_size = models.CharField(max_length=100)
    is_bulk_pack = models.IntegerField()
    included_in_scheme = models.IntegerField(null=True)
    mrp = models.FloatField()
    container_mrp = models.FloatField()
    sp_distributor = models.FloatField()
    container_sp_distributor = models.FloatField()
    sp_superstockist = models.FloatField()
    container_sp_superstockist = models.FloatField()
    sp_employee = models.FloatField()
    container_sp_employee = models.FloatField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    production_unit_id = models.CharField(max_length=11,null=True)
    gst = models.IntegerField()
    is_allow_in_packaging = models.IntegerField(default=0,null=True)
    sales_leger = models.CharField(max_length=100,null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_product_variants'

class SpProductVariantsHistory(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    product_variant_id = models.IntegerField()
    mrp = models.FloatField()
    container_mrp = models.FloatField()
    sp_distributor = models.FloatField()
    container_sp_distributor = models.FloatField()
    sp_superstockist = models.FloatField()
    container_sp_superstockist = models.FloatField()
    sp_employee = models.FloatField()
    container_sp_employee = models.FloatField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    description = models.TextField(blank=True, null=True)
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_product_variants_history'

class SpProducts(models.Model):
    product_class = models.ForeignKey(SpProductClass, models.DO_NOTHING)
    product_class_name = models.CharField(max_length=50)
    product_hsn = models.CharField(max_length=50, blank=True, null=True)
    product_name = models.CharField(max_length=100)
    product_color_code = models.CharField(max_length=15)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    order_of = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_products'

class SpRolePermissions(models.Model):
    role = models.ForeignKey('SpRoles', on_delete=models.CASCADE)
    module = models.ForeignKey(SpModules, on_delete=models.CASCADE, blank=True, null=True)
    sub_module = models.ForeignKey('SpSubModules', on_delete=models.CASCADE, blank=True, null=True)
    permission = models.ForeignKey(SpPermissions, on_delete=models.CASCADE, blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_role_permissions'


class SpRoleWorkflowPermissions(models.Model):
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    workflow_level_dept_id = models.IntegerField(null=True)
    workflow_level_role_id = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_role_workflow_permissions'


class SpRoles(models.Model):
    organization = models.ForeignKey(SpOrganizations, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100)
    department = models.ForeignKey(SpDepartments, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=100)
    role_name = models.CharField(max_length=100)
    reporting_department_id = models.IntegerField(null=True)
    reporting_department_name = models.CharField(max_length=100,null=True)
    reporting_role_id = models.IntegerField(null=True)
    reporting_role_name = models.CharField(max_length=100,null=True)
    responsibilities = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_roles'

class SpSchemes(models.Model):
    name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=100)
    is_route = models.IntegerField(blank=True, null=True)
    main_route_id = models.CharField(max_length=500,blank=True, null=True)
    route_id = models.CharField(max_length=500,blank=True, null=True)
    zone_id = models.CharField(max_length=500,blank=True, null=True)
    town_id = models.CharField(max_length=500,blank=True, null=True)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(null=True)
    scheme_type = models.IntegerField()
    applied_on_variant_id = models.IntegerField(blank=True, null=True)
    applied_on_variant_name = models.CharField(max_length=255, blank=True, null=True)
    minimum_order_quantity = models.IntegerField(blank=True, null=True)
    packaging_type = models.IntegerField(blank=True, null=True)
    order_container_id = models.IntegerField(blank=True, null=True)
    order_container_name = models.CharField(max_length=100, blank=True, null=True)
    order_packaging_id = models.IntegerField(blank=True, null=True)
    order_packaging_name = models.CharField(max_length=100, blank=True, null=True)
    free_variant_id = models.IntegerField()
    free_variant_name = models.CharField(max_length=255)
    container_quantity = models.IntegerField()
    pouch_quantity = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_schemes'

class SpProductionUnit(models.Model):
    production_unit_name = models.CharField(max_length=255)
    production_unit_code = models.CharField(max_length=222,blank=True, null=True)
    production_unit_address = models.CharField(max_length=255,blank=True, null=True)
    invoice_serial_no = models.CharField(max_length=50,blank=True, null=True)
    organization_id = models.CharField(max_length=100)
    # state_id = models.IntegerField(blank=True, null=True)
    # state_name = models.CharField(max_length=100,blank=True, null=True)
    # state_code = models.CharField(max_length=10,blank=True, null=True)
    # gstin_no = models.CharField(max_length=50,blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_production_unit'
        
class SpRoutes(models.Model):
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    route = models.CharField(max_length=255)
    route_code = models.CharField(max_length=222,blank=True, null=True)
    production_unit_id = models.IntegerField()
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_routes'

class SpRoutesTown(models.Model):
    route_id = models.IntegerField()
    route_name = models.CharField(max_length=222)
    town_id = models.IntegerField()
    town_name = models.CharField(max_length=255)
    order_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_routes_town'

class SpSalesPlanDetails(models.Model):
    sales_plan_id = models.IntegerField(blank=True, null=True)
    town_id = models.IntegerField(blank=True, null=True)
    month = models.IntegerField()
    quantity = models.BigIntegerField(blank=True, null=True)
    total = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_sales_plan_details'


class SpSalesPlans(models.Model):
    session = models.CharField(max_length=100)
    financial_year_id = models.IntegerField()
    financial_year = models.CharField(max_length=100)
    plan_interval = models.CharField(max_length=100)
    product_class_id = models.IntegerField()
    product_class_name = models.CharField(max_length=100)
    revised_count = models.IntegerField()
    sales_plan_status = models.IntegerField()
    status = models.IntegerField()
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_sales_plans'
        
class SpStates(models.Model):
    country = models.ForeignKey(SpCountries, on_delete=models.CASCADE)
    country_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    inter_state = models.IntegerField(blank=True, null=True)
    state_code = models.CharField(max_length=10,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_states'


class SpSubModules(models.Model):
    module = models.ForeignKey(SpModules, on_delete=models.CASCADE)
    module_name = models.CharField(max_length=100)
    sub_module_name = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_sub_modules'

class SpSubmodulePermissionWorkflows(models.Model):
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_submodule_permission_workflows'

class SpTowns(models.Model):
    zone_id = models.CharField(max_length=255, blank=True, null=True)
    zone_name = models.CharField(max_length=255, blank=True, null=True)
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    town = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_towns'


class SpUserAreaAllocations(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    state_id = models.IntegerField(blank=True, null=True)
    state_name = models.CharField(max_length=50, blank=True, null=True)
    zone = models.ForeignKey('SpZones', on_delete=models.CASCADE)
    zone_name = models.CharField(max_length=100, null=True)
    town = models.ForeignKey('SpTowns', on_delete=models.CASCADE)
    town_name = models.CharField(max_length=100,null=True)
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_area_allocations'

class SpTransporterCrateLedger(models.Model):
    transporter_id = models.IntegerField()
    driver_id = models.IntegerField()
    driver_name = models.CharField(max_length=222)
    plant_user_id = models.IntegerField(null=True)
    user_id = models.IntegerField()
    normal_credit = models.IntegerField()
    normal_debit = models.IntegerField()
    normal_balance = models.IntegerField()
    jumbo_credit = models.IntegerField()
    jumbo_debit = models.IntegerField()
    jumbo_balance = models.IntegerField()
    is_route = models.IntegerField()
    updated_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_transporter_crate_ledger'
        
class SpUserAttendanceLocations(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    attendance_config_id = models.IntegerField()
    distributor_ss_id = models.IntegerField()
    distributor_ss_name = models.CharField(max_length=255)
    periphery = models.IntegerField()
    timing = models.CharField(max_length=100)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_attendance_locations'

class SpUserBulkpackSchemeBifurcation(models.Model):
    user_id = models.IntegerField()
    bulkpack_scheme_id = models.IntegerField()
    above_upto_quantity = models.IntegerField()
    incentive_amount = models.FloatField()

    class Meta:
        managed = False
        db_table = 'sp_user_bulkpack_scheme_bifurcation'


class SpUserBulkpackSchemes(models.Model):
    user_id = models.IntegerField()
    scheme_id = models.IntegerField()
    scheme_name = models.CharField(max_length=255)
    state_id = models.IntegerField()
    route_id = models.CharField(max_length=100)
    town_id = models.CharField(max_length=100)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(blank=True, null=True)
    unit_id = models.IntegerField()
    unit_name = models.CharField(max_length=50)
    product_class_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_bulkpack_schemes'

class SpUserCrateLedger(models.Model):
    user_id = models.IntegerField()
    transporter_id = models.IntegerField(blank=True, null=True)
    driver_id = models.IntegerField(blank=True, null=True)
    driver_name = models.CharField(max_length=222, blank=True, null=True)
    normal_credit = models.IntegerField()
    normal_debit = models.IntegerField()
    normal_balance = models.IntegerField()
    jumbo_credit = models.IntegerField()
    jumbo_debit = models.IntegerField()
    jumbo_balance = models.IntegerField()
    updated_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_crate_ledger'

class SpUserDocuments(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    aadhaar_card = models.CharField(max_length=255, blank=True, null=True)
    pan_card = models.CharField(max_length=255, blank=True, null=True)
    cin = models.CharField(max_length=255, blank=True, null=True)
    gstin = models.CharField(max_length=255, blank=True, null=True)
    fssai = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_documents'

class SpApprovalStatus(models.Model):
    row_id = models.IntegerField()
    model_name = models.CharField(max_length=100)
    initiated_by_id = models.IntegerField()
    initiated_by_name = models.CharField(max_length=255)
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    role_id = models.IntegerField()
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=25)
    level_id = models.IntegerField()
    level = models.CharField(max_length=25)
    status = models.IntegerField()
    final_status_user_id = models.IntegerField(null=True)
    final_status_user_name = models.CharField(max_length=255, null=True)
    final_update_date_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_approval_status'

class SpUserFlatSchemes(models.Model):
    user_id = models.IntegerField()
    scheme_id = models.IntegerField()
    scheme_name = models.CharField(max_length=255)
    state_id = models.IntegerField()
    is_route = models.IntegerField(blank=True, null=True)
    main_route_id = models.CharField(max_length=500,blank=True, null=True)
    route_id = models.CharField(max_length=500,blank=True, null=True)
    zone_id = models.CharField(max_length=500,blank=True, null=True)
    town_id = models.CharField(max_length=500,blank=True, null=True)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(blank=True, null=True)
    incentive_amount = models.FloatField()
    unit_id = models.IntegerField()
    unit_name = models.CharField(max_length=50)
    product_class_id = models.CharField(max_length=50, blank=True, null=True)
    applied_on_variant_id = models.IntegerField(blank=True, null=True)
    applied_on_variant_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_flat_schemes'


class SpUserNotifications(models.Model):
    row_id = models.IntegerField()
    user_id = models.IntegerField()
    model_name = models.CharField(max_length=50)
    notification = models.TextField()
    is_read = models.IntegerField()
    created_by_user_id = models.IntegerField()
    created_by_user_name = models.CharField(max_length=225)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_notifications'

class SpUserProductVariants(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=50)
    product_variant_id = models.IntegerField()
    product_class_id = models.IntegerField()
    item_sku_code = models.CharField(max_length=25)
    variant_quantity = models.IntegerField()
    variant_unit_id = models.IntegerField()
    variant_unit_name = models.CharField(max_length=25)
    largest_unit_name = models.CharField(max_length=50)
    variant_name = models.CharField(max_length=255)
    variant_size = models.CharField(max_length=255)
    no_of_pouch = models.IntegerField()
    container_size = models.CharField(max_length=100)
    is_bulk_pack = models.IntegerField()
    included_in_scheme = models.IntegerField(null=True)
    mrp = models.FloatField()
    container_mrp = models.FloatField()
    sp_user = models.FloatField()
    container_sp_user = models.FloatField()
    product_limit = models.IntegerField(default=0)
    valid_from = models.DateField()
    valid_to = models.DateField()
    status = models.IntegerField(default=1,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_product_variants'

class SpUserQuantitativeSchemeBifurcation(models.Model):
    user_id = models.IntegerField()
    user_scheme_id = models.IntegerField()
    minimum_order_quantity = models.IntegerField()
    order_container_id = models.IntegerField()
    order_container_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'sp_user_quantitative_scheme_bifurcation'



class UserManager(BaseUserManager):
    def create_user(self, user, password=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not user:
            raise ValueError('Error: The User you want to create must have an username, try again')

        my_user = self.model(
            user=self.model.normalize_username(user)
        )
    
        my_user.set_password(password)
        my_user.save(using=self._db)
        return my_user

    def create_staffuser(self, user, password):
        """
        Creates and saves a staff user with the given username and password.
        """
        my_user = self.create_user(
            user,
            password=password,
        )
        my_user.staff = True
        my_user.save(using=self._db)
        return my_user

    def create_superuser(self, user, password):
        """
        Creates and saves a superuser with the given username and password.
        """
        my_user = self.create_user(
            user,
            password=password,
        )
        my_user.staff = True
        my_user.admin = True
        my_user.save(using=self._db)
        return my_user

class SpUserRolePermissions(models.Model):
    user = models.ForeignKey('SpUsers', models.DO_NOTHING)
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_role_permissions'


class SpUserRoleWorkflowPermissions(models.Model):
    user = models.ForeignKey('SpUsers', models.DO_NOTHING)
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    workflow_level_dept_id = models.IntegerField()
    workflow_level_role_id = models.IntegerField()
    status = models.IntegerField()
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_role_workflow_permissions'

class SpUserSchemes(models.Model):
    user_id = models.IntegerField()
    scheme_id = models.IntegerField()
    scheme_name = models.CharField(max_length=255)
    state_id = models.IntegerField()
    is_route = models.IntegerField(blank=True, null=True)
    main_route_id = models.CharField(max_length=500,blank=True, null=True)
    route_id = models.CharField(max_length=500,blank=True, null=True)
    zone_id = models.CharField(max_length=500,blank=True, null=True)
    town_id = models.CharField(max_length=500,blank=True, null=True)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(null=True)
    scheme_type = models.IntegerField()
    applied_on_variant_id = models.IntegerField(blank=True, null=True)
    applied_on_variant_name = models.CharField(max_length=255, blank=True, null=True)
    minimum_order_quantity = models.IntegerField(blank=True, null=True)
    packaging_type = models.IntegerField(blank=True, null=True)
    order_container_id = models.IntegerField(blank=True, null=True)
    order_container_name = models.CharField(max_length=100, blank=True, null=True)
    order_packaging_id = models.IntegerField(blank=True, null=True)
    order_packaging_name = models.CharField(max_length=100, blank=True, null=True)
    free_variant_id = models.IntegerField()
    free_variant_name = models.CharField(max_length=255)
    container_quantity = models.IntegerField()
    pouch_quantity = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_schemes'

class SpUserTracking(models.Model):
    user_id = models.IntegerField()
    latitude = models.CharField(max_length=25, blank=True, null=True)
    longitude = models.CharField(max_length=25, blank=True, null=True)
    velocity = models.FloatField(blank=True, null=True)
    distance_travelled = models.FloatField(blank=True, null=True)
    travel_charges = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_tracking'


    
class SpUsers(AbstractBaseUser):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'official_email'

    salutation        = models.CharField(max_length=10)
    first_name        = models.CharField(max_length=50)
    middle_name       = models.CharField(max_length=50,null=True)
    last_name         = models.CharField(max_length=50)
    store_name        = models.CharField(max_length=255, blank=True, null=True)
    store_image       = models.CharField(max_length=100, blank=True, null=True)
    official_email    = models.CharField(unique=True,max_length=100)
    primary_contact_number = models.CharField(max_length=25)
    password = models.CharField(max_length=255)
    emp_sap_id = models.CharField(max_length=50)
    organization_id = models.IntegerField()
    organization_name = models.CharField(max_length=222, blank=True, null=True)
    department_id = models.IntegerField()
    department_name = models.CharField(max_length=222, blank=True, null=True)
    role_id = models.IntegerField()
    role_name = models.CharField(max_length=222)
    reporting_to_id = models.IntegerField()
    reporting_to_name = models.CharField(max_length=255)
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    device_id = models.CharField(max_length=50, blank=True, null=True)
    firebase_token = models.CharField(max_length=255, blank=True, null=True)
    web_auth_token = models.CharField(max_length=255, blank=True, null=True)
    auth_otp = models.CharField(max_length=10, blank=True, null=True)
    last_login = models.DateTimeField(null=True)
    last_ip = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(default=1)
    user_type = models.IntegerField(default=0)
    is_distributor = models.IntegerField(default=0)
    is_super_stockist = models.IntegerField(default=0)
    is_retailer = models.IntegerField(default=0)
    is_tagged = models.IntegerField(default=0)
    tagged_by = models.IntegerField(blank=True, null=True)
    tagged_date = models.DateTimeField(blank=True, null=True)
    periphery = models.CharField(max_length=255,blank=True, null=True)
    timing = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    self_owned = models.IntegerField(default=0)
    purchase_milk_from_org = models.IntegerField(default=0, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        managed = False
        db_table = 'sp_users'

class SpVehicleClass(models.Model):
    vehicle_class = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_class'


class SpVehicleFinancer(models.Model):
    financer = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_financer'


class SpVehicleFitnessDetails(models.Model):
    vehicle_id = models.IntegerField()
    application_no = models.CharField(max_length=100, blank=True, null=True)
    inspection_date = models.DateField(blank=True, null=True)
    fitness_valid_till = models.DateField(blank=True, null=True)
    copy_of_fitness_certificate = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_fitness_details'


class SpVehicleInsuranceDetails(models.Model):
    vehicle_id = models.IntegerField()
    name_of_insurer = models.CharField(max_length=50, blank=True, null=True)
    date_of_insurance = models.DateField(blank=True, null=True)
    valid_till = models.DateField(blank=True, null=True)
    premium_amount = models.FloatField(blank=True, null=True)
    total_sum_insured = models.FloatField(blank=True, null=True)
    insurance_copy = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_insurance_details'


class SpVehicleInsurer(models.Model):
    name_of_insurer = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_insurer'


class SpVehicleMaker(models.Model):
    maker_name = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_maker'


class SpVehicleMakerClassification(models.Model):
    classification = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_maker_classification'


class SpVehiclePollutionDetails(models.Model):
    vehicle_id = models.IntegerField()
    certificate_sr_no = models.CharField(max_length=50, blank=True, null=True)
    date_of_registration = models.DateField(blank=True, null=True)
    pollution_valid_till = models.DateField(blank=True, null=True)
    copy_of_certificate = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_pollution_details'


class SpVehicleRegistrationDetails(models.Model):
    vehicle_id = models.IntegerField()
    owner_name = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=50)
    registered_address = models.CharField(max_length=100, blank=True, null=True)
    rto = models.CharField(max_length=50, blank=True, null=True)
    registration_fees_amount = models.FloatField(blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    registration_valid_till = models.DateField(blank=True, null=True)
    registration_copy = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_registration_details'


class SpVehicleRoadpermitDetails(models.Model):
    vehicle_id = models.IntegerField()
    permit_no = models.CharField(max_length=50,blank=True, null=True)
    permit_registration_date = models.DateField(blank=True, null=True)
    permit_valid_till = models.DateField(blank=True, null=True)
    permitted_route = models.CharField(max_length=50,blank=True, null=True)
    purpose = models.CharField(max_length=100,blank=True, null=True)
    insurance_copy = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_roadpermit_details'


class SpVehicleWarrantyDetails(models.Model):
    vehicle_id = models.IntegerField()
    overall_warranty_period = models.IntegerField(blank=True, null=True)
    component_warranty = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_warranty_details'


class SpVehicles(models.Model):
    registration_number = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    ownership_type = models.CharField(max_length=50)
    dealer_name = models.CharField(max_length=50, blank=True, null=True)
    dealer_address = models.CharField(max_length=100, blank=True, null=True)
    dealer_contact_no = models.CharField(max_length=10, blank=True, null=True)
    owner_name = models.CharField(max_length=50, blank=True, null=True)
    owner_address = models.CharField(max_length=100, blank=True, null=True)
    owner_contact_no = models.CharField(max_length=10, blank=True, null=True)
    vehicle_type = models.CharField(max_length=20, blank=True, null=True)
    class_of_vehicle = models.CharField(max_length=50, blank=True, null=True)
    maker_name = models.CharField(max_length=50, blank=True, null=True)
    year_of_manufacture = models.TextField(blank=True, null=True)  # This field type is a guess.
    chassis_no = models.CharField(max_length=50, blank=True, null=True)
    engine_no = models.CharField(max_length=50, blank=True, null=True)
    horsepower = models.CharField(max_length=50, blank=True, null=True)
    cubic_capacity = models.FloatField(blank=True, null=True)
    maker_classification = models.CharField(max_length=50, blank=True, null=True)
    seating_capacity_standard = models.FloatField(blank=True, null=True)
    seating_capacity_max = models.FloatField(blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    ac_fitted = models.CharField(max_length=10, blank=True, null=True)
    finance = models.CharField(max_length=10, blank=True, null=True)
    financer_name = models.CharField(max_length=50, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    fuel_type = models.IntegerField(blank=True, null=True)
    purchase_amount = models.FloatField(blank=True, null=True)
    driver_id = models.IntegerField(blank=True, null=True)
    driver_name = models.CharField(max_length=255, blank=True, null=True)
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=255, blank=True, null=True)
    incharge_id = models.IntegerField(blank=True, null=True)
    assign_from_date = models.DateField(blank=True, null=True)
    assign_to_date = models.DateField(blank=True, null=True)
    petro_card_id = models.IntegerField(blank=True, null=True)
    sale_letter = models.CharField(max_length=100, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    vehicle_pic = models.TextField(blank=True, null=True)
    api_token = models.TextField(blank=True, null=True)
    firebase_token = models.TextField(blank=True, null=True)
    production_unit_id = models.IntegerField()
    status = models.IntegerField()
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicles'


class SpVehicleTracking(models.Model):
    vehicle_id = models.IntegerField()
    driver_id = models.IntegerField(blank=True, null=True)
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=25, blank=True, null=True)
    longitude = models.CharField(max_length=25, blank=True, null=True)
    velocity = models.FloatField(blank=True, null=True)
    distance_travelled = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_tracking'

class SpWorkflowLevels(models.Model):
    level = models.CharField(max_length=15)
    priority = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_workflow_levels'


class SpWorkingShifts(models.Model):
    working_shift = models.CharField(max_length=255)
    order_timing = models.TimeField(null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_working_shifts'


class SpZones(models.Model):
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    zone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_zones'

class SpCountryCodes(models.Model):
    country_code = models.CharField(max_length=10)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_country_codes'

class SpAppVersions(models.Model):
    version = models.CharField(max_length=100)
    status = models.CharField(default=0, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_app_versions'

class AuthtokenToken(models.Model):
    key  = models.CharField(max_length=40)
    created = models.DateTimeField()
    user_id  = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'authtoken_token'

class ProductVariantTemplate(models.Model):
    store_name = models.CharField(max_length=222, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_variant_template'


class SpQuantitativeSchemeBifurcation(models.Model):
    scheme_id = models.IntegerField()
    minimum_order_quantity = models.IntegerField()
    order_container_id = models.IntegerField()
    order_container_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'sp_quantitative_scheme_bifurcation'



class SpReasons(models.Model):
    reason = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_reasons'

class SpGrievance(models.Model):
    user_id = models.IntegerField()
    order_id = models.CharField(max_length=255, null=True)
    reason_id = models.IntegerField(null=True)
    reason_name	 = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)
    attachment = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_grievance'        

class SpLeaveTypes(models.Model):
    leave_type = models.CharField(max_length=50)
    alias = models.CharField(max_length=20)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_leave_types'

class SpUserLeaves(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=100)
    leave_type_id = models.IntegerField()
    leave_status = models.IntegerField(default=0)
    leave_type = models.CharField(max_length=50)
    leave_from_date = models.DateTimeField()
    leave_to_date = models.DateTimeField()
    leave_detail = models.TextField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    attachment = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_leaves'

class SpFocRequests(models.Model):
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=100)
    foc_delivery_date = models.DateTimeField()
    foc_status = models.IntegerField()
    request_by_id = models.IntegerField()
    request_by_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_foc_requests'


class SpFocRequestsDetails(models.Model):
    foc_request_id = models.IntegerField()
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=100)
    product_variant_id = models.IntegerField()
    product_variant_name = models.CharField(max_length=100)
    product_variant_size = models.CharField(max_length=100)
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_foc_requests_details'

class SpIncentive(models.Model):
    user_id = models.IntegerField()
    payment_cycle = models.IntegerField()
    status = models.IntegerField(default=1)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_incentive'


class SpIncentiveDetails(models.Model):
    incentive_id = models.IntegerField()
    incentive_type = models.IntegerField()
    class_product_variant_id = models.IntegerField()
    is_slab = models.IntegerField(default=0)
    ss_incentive = models.FloatField(null=True)
    distributor_incentive = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_incentive_details'


class SpIncentiveSlabDetails(models.Model):
    incentive_id = models.IntegerField()
    incentive_detail_id = models.IntegerField()
    slab_id = models.IntegerField()
    ss_incentive = models.FloatField()
    distributor_incentive = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_incentive_slab_details'


class SpIncentiveHistory(models.Model):
    user_id = models.IntegerField()
    payment_cycle = models.IntegerField()
    status = models.IntegerField(default=1)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_incentive_history'


class SpIncentiveDetailsHistory(models.Model):
    incentive_id = models.IntegerField()
    incentive_type = models.IntegerField()
    class_product_variant_id = models.IntegerField()
    is_slab = models.IntegerField(default=0)
    ss_incentive = models.FloatField(null=True)
    distributor_incentive = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_incentive_details_history'


class SpIncentiveSlabDetailsHistory(models.Model):
    incentive_id = models.IntegerField()
    incentive_detail_id = models.IntegerField()
    slab_id = models.IntegerField()
    ss_incentive = models.FloatField()
    distributor_incentive = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_incentive_slab_details_history'




class SpSlabMasterList(models.Model):
    product_class_id = models.IntegerField()
    more_than_quantity = models.IntegerField()
    upto_quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_slab_master_list'



class SpUserIncentive(models.Model):
    user_id = models.IntegerField()
    ss_incentive = models.FloatField()
    distributor_incentive = models.FloatField()
    primary_transporter_amount = models.FloatField()
    secondary_transporter_amount = models.FloatField()
    net_amount = models.FloatField()
    payment_cycle = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_incentive'


class SpUserIncentiveDetails(models.Model):
    user_incentive_id = models.IntegerField()
    master_slab_id = models.IntegerField()
    slab_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_incentive_details'        


class SpLogisticPlanDetail(models.Model):
    order_id = models.IntegerField()
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    product_variant_id = models.IntegerField()
    product_variant_name = models.CharField(max_length=255)
    product_variant_size = models.CharField(max_length=255)
    product_no_of_pouch = models.IntegerField()
    product_container_size = models.CharField(max_length=100)
    product_container_type = models.CharField(max_length=50)
    product_packaging_type_name = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.FloatField()
    rate = models.FloatField()
    amount = models.FloatField()
    quantity_in_pouch = models.IntegerField(blank=True, null=True)
    quantity_in_ltr = models.FloatField(blank=True, null=True)
    packaging_type = models.CharField(max_length=50)
    is_allow = models.IntegerField(blank=True, null=True)
    tally_export_type = models.IntegerField(default=0,null=True)
    order_date = models.DateTimeField()
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=50, blank=True, null=True)
    vehicle_id = models.IntegerField(blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    gst = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_logistic_plan_detail'
        unique_together = ["order_id", "product_variant_id","vehicle_id"]



class SpLogisticOrderSchemes(models.Model):
    order_id = models.IntegerField()
    scheme_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()
    scheme_type = models.CharField(max_length=50)
    variant_id = models.IntegerField(blank=True, null=True)
    on_order_of = models.IntegerField(blank=True, null=True)
    free_variant_id = models.IntegerField(blank=True, null=True)
    free_variant_container_type = models.CharField(max_length=50, blank=True, null=True)
    free_variant_packaging_type = models.CharField(max_length=100, blank=True, null=True)
    free_variant_container_size = models.CharField(max_length=100, blank=True, null=True)
    container_quantity = models.IntegerField(blank=True, null=True)
    pouch_quantity = models.IntegerField(blank=True, null=True)
    quantity_in_ltr = models.FloatField(blank=True, null=True)
    incentive_amount = models.FloatField(blank=True, null=True)
    unit_id = models.IntegerField(blank=True, null=True)
    unit_name = models.CharField(max_length=50, blank=True, null=True)
    product_id = models.IntegerField(blank=True, null=True)
    product_class_id = models.CharField(max_length=50, blank=True, null=True)
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=50, blank=True, null=True)
    vehicle_id = models.IntegerField(blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_logistic_order_schemes'
        
        
class SpBankDetails(models.Model):
    bank_name = models.CharField(max_length=100)
    account_no = models.CharField(max_length=100)
    organization_id = models.CharField(max_length=110)
    created_by = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_bank_details'
        
class SpTcsMaster(models.Model):
    tcs_value = models.BigIntegerField()
    tcs_percentage = models.FloatField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_tcs_master'

        
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)   


class SalesLedger(models.Model):
    leadger_name = models.CharField(max_length=150)
    class Meta:
        managed = False
        db_table = 'sales_ledger'     
