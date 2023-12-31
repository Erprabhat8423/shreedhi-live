# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


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
    user_id = models.IntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user_id', 'group_id'),)


class AuthUserUserPermissions(models.Model):
    user_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user_id', 'permission_id'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user_id = models.IntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class Configuration(models.Model):
    logo = models.CharField(max_length=100, blank=True, null=True)
    loader = models.TextField(blank=True, null=True)
    page_limit = models.IntegerField(blank=True, null=True)
    org_name = models.CharField(max_length=255, blank=True, null=True)
    org_code = models.CharField(max_length=6, blank=True, null=True)
    google_app_key = models.CharField(max_length=500, blank=True, null=True)
    order_timing = models.CharField(max_length=50, blank=True, null=True)
    user_tracking_time = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'configuration'


class Departments(models.Model):
    organization_id = models.IntegerField()
    department_name = models.CharField(max_length=200)
    land_line_code = models.CharField(max_length=6, blank=True, null=True)
    phone_code = models.CharField(max_length=3, blank=True, null=True)
    landline_no = models.CharField(max_length=20, blank=True, null=True)
    dept_ext = models.CharField(max_length=3, blank=True, null=True)
    mobile_code = models.CharField(max_length=6, blank=True, null=True)
    mobile_no = models.CharField(max_length=10, blank=True, null=True)
    email_id = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'departments'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()

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


class Organizations(models.Model):
    organization_name = models.CharField(max_length=200)
    land_line_code = models.CharField(max_length=6, blank=True, null=True)
    phone_code = models.CharField(max_length=3, blank=True, null=True)
    landline_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_code = models.CharField(max_length=6, blank=True, null=True)
    mobile_no = models.CharField(max_length=10, blank=True, null=True)
    email_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'organizations'


class ProductVariantTemplate(models.Model):
    store_name = models.CharField(max_length=222, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_variant_template'


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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_activity_logs'


class SpAddresses(models.Model):
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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_addresses'


class SpAppVersions(models.Model):
    version = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_app_versions'


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
    final_status_user_id = models.IntegerField(blank=True, null=True)
    final_status_user_name = models.CharField(max_length=255, blank=True, null=True)
    final_update_date_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_approval_status'


class SpAttendanceConfigs(models.Model):
    user_id = models.IntegerField()
    attendance_image_1 = models.CharField(max_length=255)
    attendance_image_2 = models.CharField(max_length=255)
    attendance_image_3 = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_attendance_configs'


class SpBasicDetails(models.Model):
    user_id = models.IntegerField()
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=25, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_nubmer = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    cin = models.CharField(max_length=20, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    fssai = models.CharField(max_length=14, blank=True, null=True)
    working_shift_id = models.IntegerField(blank=True, null=True)
    working_shift_name = models.CharField(max_length=50, blank=True, null=True)
    order_timing = models.CharField(max_length=50, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    personal_email = models.CharField(max_length=50, blank=True, null=True)
    outlet_owned = models.CharField(max_length=50, blank=True, null=True)
    outstanding_amount = models.FloatField(blank=True, null=True)
    security_amount = models.FloatField(blank=True, null=True)
    opening_crates = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_basic_details'


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
    product_class_id = models.IntegerField(blank=True, null=True)
    product_variant_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_bulkpack_schemes'


class SpCities(models.Model):
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_cities'


class SpColorCodes(models.Model):
    color = models.CharField(max_length=50)
    code = models.CharField(max_length=15)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_color_codes'


class SpComponents(models.Model):
    component = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'sp_components'


class SpContactNumbers(models.Model):
    user_id = models.IntegerField()
    country_code = models.CharField(max_length=10)
    contact_type = models.IntegerField()
    contact_type_name = models.CharField(max_length=25, blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    is_primary = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_contact_numbers'


class SpContactPersons(models.Model):
    user_id = models.IntegerField()
    contact_person_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_contact_persons'


class SpContactTypes(models.Model):
    contact_type = models.CharField(max_length=100)
    status = models.IntegerField()
    create_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_contact_types'


class SpContainers(models.Model):
    container = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_containers'


class SpCountries(models.Model):
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_countries'


class SpCountryCodes(models.Model):
    country_code = models.CharField(max_length=10)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_country_codes'


class SpDepartments(models.Model):
    organization_id = models.IntegerField()
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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_departments'


class SpDistributorAreaAllocations(models.Model):
    user_id = models.IntegerField()
    zone_id = models.IntegerField()
    zone_name = models.CharField(max_length=100)
    town_id = models.IntegerField()
    town_name = models.IntegerField()
    route_id = models.IntegerField()
    route_name = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_distributor_area_allocations'


class SpDistributorProducts(models.Model):
    user_id = models.IntegerField()
    sku_code = models.CharField(max_length=50)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=100)
    product_variant_id = models.CharField(max_length=50)
    product_mrp = models.FloatField()
    product_sale_price = models.FloatField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_drivers'


class SpFavorites(models.Model):
    user_id = models.IntegerField()
    favorite = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_favorites'


class SpFlatSchemes(models.Model):
    name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=100)
    route_id = models.CharField(max_length=100)
    town_id = models.CharField(max_length=100)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(blank=True, null=True)
    incentive_amount = models.FloatField()
    unit_id = models.IntegerField()
    unit_name = models.CharField(max_length=50)
    product_class_id = models.IntegerField(blank=True, null=True)
    product_variant_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_flat_schemes'


class SpFuelType(models.Model):
    fuel_type = models.CharField(max_length=100)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_fuel_type'


class SpGrievance(models.Model):
    order_id = models.CharField(max_length=100, blank=True, null=True)
    reason_id = models.IntegerField(blank=True, null=True)
    reason_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_grievance'


class SpHoReport(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    product_variant_id = models.IntegerField()
    quantity = models.BigIntegerField(blank=True, null=True)
    foc_pouch = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_ho_report'


class SpHoReportHistory(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    product_variant_id = models.IntegerField()
    quantity = models.BigIntegerField(blank=True, null=True)
    foc_pouch = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_ho_report_history'


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


class SpModeOfPayments(models.Model):
    mode_of_payment = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_mode_of_payments'


class SpModules(models.Model):
    module_name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_modules'


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
    quantity = models.IntegerField()
    rate = models.FloatField()
    amount = models.FloatField()
    order_date = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_order_details'


class SpOrderOtp(models.Model):
    vehicle_id = models.IntegerField()
    order_id = models.IntegerField()
    otp = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_order_otp'


class SpOrderSchemes(models.Model):
    order_id = models.IntegerField()
    scheme_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()
    scheme_type = models.CharField(max_length=50)
    variant_id = models.IntegerField(blank=True, null=True)
    on_order_of = models.IntegerField(blank=True, null=True)
    free_variant_id = models.IntegerField(blank=True, null=True)
    free_variant_container_type = models.CharField(max_length=50, blank=True, null=True)
    container_quantity = models.IntegerField(blank=True, null=True)
    pouch_quantity = models.IntegerField(blank=True, null=True)
    incentive_amount = models.FloatField(blank=True, null=True)
    unit_id = models.IntegerField(blank=True, null=True)
    unit_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_order_schemes'


class SpOrders(models.Model):
    order_code = models.CharField(max_length=255)
    user_id = models.IntegerField()
    user_sap_id = models.CharField(max_length=50)
    user_name = models.CharField(max_length=150)
    user_type = models.CharField(max_length=50)
    town_id = models.IntegerField()
    town_name = models.CharField(max_length=100)
    route_id = models.IntegerField()
    route_name = models.CharField(max_length=100)
    order_date = models.DateTimeField()
    order_status = models.IntegerField()
    order_shift_id = models.IntegerField()
    order_shift_name = models.CharField(max_length=255)
    order_scheme_id = models.IntegerField(blank=True, null=True)
    order_total_amount = models.FloatField()
    order_items_count = models.IntegerField()
    mode_of_payment = models.CharField(max_length=100)
    amount_to_be_paid = models.FloatField()
    updated_date = models.DateTimeField(blank=True, null=True)
    indent_status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_orders'


class SpOrganizations(models.Model):
    organization_name = models.CharField(max_length=150)
    landline_country_code = models.CharField(max_length=10)
    landline_state_code = models.CharField(max_length=10)
    landline_number = models.CharField(max_length=15)
    mobile_country_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=8, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_organizations'


class SpPermissions(models.Model):
    permission = models.CharField(max_length=100)
    slug = models.CharField(max_length=150)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_permissions'


class SpPetroCard(models.Model):
    petro_card_number = models.CharField(max_length=100)
    petro_card_provider = models.CharField(max_length=100, blank=True, null=True)
    petro_card_issued_to = models.CharField(max_length=100, blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)
    customer_id = models.CharField(max_length=100, blank=True, null=True)
    scan_of_card = models.TextField(blank=True, null=True)
    is_assigned = models.IntegerField()
    created_at = models.DateTimeField()
    created_by = models.IntegerField()
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_petro_card'


class SpProductClass(models.Model):
    product_class = models.CharField(max_length=50)
    product_hsn = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_class'


class SpProductUnits(models.Model):
    unit = models.CharField(max_length=100)
    largest_unit = models.CharField(max_length=50)
    conversion_value = models.FloatField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_units'


class SpProductVariantImages(models.Model):
    product_variant_id = models.IntegerField()
    image_url = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_variant_images'


class SpProductVariants(models.Model):
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=50)
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
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_variants_history'


class SpProducts(models.Model):
    product_hsn = models.CharField(max_length=10)
    product_class_id = models.IntegerField()
    product_class_name = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    container_id = models.IntegerField()
    container_name = models.CharField(max_length=50)
    product_color_code = models.CharField(max_length=15)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_products'


class SpReasons(models.Model):
    reason = models.CharField(max_length=255)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_reasons'


class SpRolePermissions(models.Model):
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    workflow = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    workflow_level_dept_id = models.IntegerField(blank=True, null=True)
    workflow_level_role_id = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_role_workflow_permissions'


class SpRoles(models.Model):
    organization_id = models.IntegerField()
    organization_name = models.CharField(max_length=100)
    department_id = models.IntegerField()
    department_name = models.CharField(max_length=100)
    role_name = models.CharField(max_length=100)
    reporting_department_id = models.IntegerField(blank=True, null=True)
    reporting_department_name = models.CharField(max_length=100, blank=True, null=True)
    reporting_role_id = models.IntegerField(blank=True, null=True)
    reporting_role_name = models.CharField(max_length=100, blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_roles'


class SpRoutes(models.Model):
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    route = models.CharField(max_length=255)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_routes'


class SpRoutesTown(models.Model):
    route_id = models.IntegerField()
    route_name = models.CharField(max_length=222)
    town_id = models.IntegerField()
    town_name = models.CharField(max_length=255)
    order_index = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_routes_town'


class SpSchemes(models.Model):
    name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=100)
    route_id = models.CharField(max_length=100)
    town_id = models.CharField(max_length=100)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(blank=True, null=True)
    scheme_type = models.IntegerField()
    applied_on_variant_id = models.IntegerField(blank=True, null=True)
    applied_on_variant_name = models.CharField(max_length=255, blank=True, null=True)
    minimum_order_quantity = models.IntegerField(blank=True, null=True)
    order_container_id = models.IntegerField(blank=True, null=True)
    order_container_name = models.CharField(max_length=100, blank=True, null=True)
    free_variant_id = models.IntegerField()
    free_variant_name = models.CharField(max_length=255)
    container_quantity = models.IntegerField()
    pouch_quantity = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_schemes'


class SpStates(models.Model):
    country_id = models.IntegerField()
    country_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_states'


class SpSubModules(models.Model):
    module_id = models.IntegerField()
    module_name = models.CharField(max_length=100)
    sub_module_name = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_sub_modules'


class SpTowns(models.Model):
    zone_id = models.IntegerField(blank=True, null=True)
    zone_name = models.CharField(max_length=255, blank=True, null=True)
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    town = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_towns'


class SpUserAreaAllocations(models.Model):
    user_id = models.IntegerField()
    state_id = models.IntegerField(blank=True, null=True)
    state_name = models.CharField(max_length=50, blank=True, null=True)
    zone_id = models.IntegerField(blank=True, null=True)
    zone_name = models.CharField(max_length=100, blank=True, null=True)
    town_id = models.IntegerField(blank=True, null=True)
    town_name = models.CharField(max_length=100, blank=True, null=True)
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_area_allocations'


class SpUserAttendance(models.Model):
    user_id = models.IntegerField()
    attendance_date_time = models.DateTimeField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_attendance'


class SpUserAttendanceLocations(models.Model):
    user_id = models.IntegerField()
    attendance_config_id = models.IntegerField()
    distributor_ss_id = models.IntegerField()
    distributor_ss_name = models.CharField(max_length=255)
    periphery = models.IntegerField()
    timing = models.CharField(max_length=100)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    product_class_id = models.IntegerField(blank=True, null=True)
    product_variant_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_bulkpack_schemes'


class SpUserDocuments(models.Model):
    user_id = models.IntegerField()
    aadhaar_card = models.CharField(max_length=255, blank=True, null=True)
    pan_card = models.CharField(max_length=255, blank=True, null=True)
    cin = models.CharField(max_length=255, blank=True, null=True)
    gstin = models.CharField(max_length=255, blank=True, null=True)
    fssai = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_documents'


class SpUserFlatSchemes(models.Model):
    user_id = models.IntegerField()
    scheme_id = models.IntegerField()
    scheme_name = models.CharField(max_length=255)
    state_id = models.IntegerField()
    route_id = models.CharField(max_length=100)
    town_id = models.CharField(max_length=100)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(blank=True, null=True)
    incentive_amount = models.FloatField()
    unit_id = models.IntegerField()
    unit_name = models.CharField(max_length=50)
    product_class_id = models.IntegerField(blank=True, null=True)
    product_variant_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    mrp = models.FloatField()
    container_mrp = models.FloatField()
    sp_user = models.FloatField()
    container_sp_user = models.FloatField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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


class SpUserRolePermissions(models.Model):
    user_id = models.IntegerField()
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    workflow = models.TextField(blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_role_permissions'


class SpUserRoleWorkflowPermissions(models.Model):
    user_id = models.IntegerField()
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    workflow_level_dept_id = models.IntegerField(blank=True, null=True)
    workflow_level_role_id = models.IntegerField()
    status = models.IntegerField()
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_role_workflow_permissions'


class SpUserSchemes(models.Model):
    user_id = models.IntegerField()
    scheme_id = models.IntegerField()
    scheme_name = models.CharField(max_length=255)
    state_id = models.IntegerField()
    route_id = models.CharField(max_length=100)
    town_id = models.CharField(max_length=100)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField(blank=True, null=True)
    scheme_type = models.IntegerField()
    applied_on_variant_id = models.IntegerField(blank=True, null=True)
    applied_on_variant_name = models.CharField(max_length=255, blank=True, null=True)
    minimum_order_quantity = models.IntegerField(blank=True, null=True)
    order_container_id = models.IntegerField(blank=True, null=True)
    order_container_name = models.CharField(max_length=100, blank=True, null=True)
    free_variant_id = models.IntegerField()
    free_variant_name = models.CharField(max_length=255)
    container_quantity = models.IntegerField()
    pouch_quantity = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_schemes'


class SpUsers(models.Model):
    salutation = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    store_name = models.CharField(max_length=255, blank=True, null=True)
    store_image = models.CharField(max_length=100, blank=True, null=True)
    official_email = models.CharField(max_length=100)
    primary_contact_number = models.CharField(max_length=25)
    password = models.CharField(max_length=255)
    emp_sap_id = models.CharField(max_length=50)
    organization_id = models.IntegerField(blank=True, null=True)
    organization_name = models.CharField(max_length=222, blank=True, null=True)
    department_id = models.IntegerField(blank=True, null=True)
    department_name = models.CharField(max_length=222, blank=True, null=True)
    role_id = models.IntegerField(blank=True, null=True)
    role_name = models.CharField(max_length=222, blank=True, null=True)
    reporting_to_id = models.IntegerField(blank=True, null=True)
    reporting_to_name = models.CharField(max_length=255, blank=True, null=True)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    device_id = models.CharField(max_length=50, blank=True, null=True)
    firebase_token = models.CharField(max_length=255, blank=True, null=True)
    web_auth_token = models.CharField(max_length=255, blank=True, null=True)
    auth_otp = models.CharField(max_length=10, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    last_ip = models.CharField(max_length=255, blank=True, null=True)
    user_type = models.IntegerField()
    is_distributor = models.IntegerField()
    is_super_stockist = models.IntegerField()
    is_retailer = models.IntegerField()
    is_tagged = models.IntegerField()
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    self_owned = models.IntegerField()
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()
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
    created_at = models.DateTimeField()
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
    created_at = models.DateTimeField()
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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_registration_details'


class SpVehicleRoadpermitDetails(models.Model):
    vehicle_id = models.IntegerField()
    permit_no = models.CharField(max_length=50, blank=True, null=True)
    permit_registration_date = models.DateField(blank=True, null=True)
    permit_valid_till = models.DateField(blank=True, null=True)
    permitted_route = models.CharField(max_length=50, blank=True, null=True)
    purpose = models.CharField(max_length=100, blank=True, null=True)
    insurance_copy = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_roadpermit_details'


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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_tracking'


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
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicles'


class SpWorkflowLevels(models.Model):
    level = models.CharField(max_length=15)
    priority = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_workflow_levels'


class SpWorkingShifts(models.Model):
    working_shift = models.CharField(max_length=255)
    order_timing = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_working_shifts'


class SpZones(models.Model):
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    zone = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_zones'
