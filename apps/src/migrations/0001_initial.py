# Generated by Django 3.1.2 on 2020-10-10 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('salutation', models.CharField(max_length=10)),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('store_name', models.CharField(blank=True, max_length=255, null=True)),
                ('store_image', models.CharField(blank=True, max_length=100, null=True)),
                ('official_email', models.CharField(max_length=100, unique=True)),
                ('primary_contact_number', models.CharField(max_length=25)),
                ('password', models.CharField(max_length=255)),
                ('plain_password', models.CharField(max_length=50)),
                ('emp_sap_id', models.CharField(max_length=50)),
                ('organization_id', models.IntegerField()),
                ('department_id', models.IntegerField()),
                ('role_id', models.IntegerField()),
                ('reporting_to_id', models.IntegerField()),
                ('reporting_to_name', models.CharField(max_length=255)),
                ('profile_image', models.CharField(blank=True, max_length=100, null=True)),
                ('device_id', models.CharField(blank=True, max_length=50, null=True)),
                ('firebase_token', models.CharField(blank=True, max_length=255, null=True)),
                ('auth_token', models.CharField(blank=True, max_length=255, null=True)),
                ('auth_otp', models.CharField(blank=True, max_length=10, null=True)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpAddresses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('type', models.CharField(max_length=100)),
                ('address_line_1', models.CharField(max_length=250)),
                ('address_line_2', models.CharField(blank=True, max_length=250, null=True)),
                ('country_id', models.IntegerField()),
                ('country_name', models.CharField(max_length=100)),
                ('state_id', models.IntegerField()),
                ('state_name', models.CharField(max_length=100)),
                ('city_id', models.IntegerField()),
                ('city_name', models.CharField(max_length=100)),
                ('pincode', models.CharField(max_length=8)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_addresses',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpAttendanceConfigs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('attendance_image_1', models.CharField(max_length=255)),
                ('attendance_image_2', models.CharField(max_length=255)),
                ('attendance_image_3', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_attendance_configs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpBasicDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('father_name', models.CharField(max_length=100)),
                ('mother_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(max_length=25)),
                ('blood_group', models.CharField(blank=True, max_length=10, null=True)),
                ('aadhar_nubmer', models.CharField(blank=True, max_length=15, null=True)),
                ('pan_number', models.CharField(blank=True, max_length=20, null=True)),
                ('cin', models.CharField(blank=True, max_length=20, null=True)),
                ('gstin', models.CharField(blank=True, max_length=20, null=True)),
                ('working_shift_id', models.IntegerField(blank=True, null=True)),
                ('working_shift_name', models.CharField(blank=True, max_length=50, null=True)),
                ('date_of_joining', models.DateField(blank=True, null=True)),
                ('personal_email', models.CharField(blank=True, max_length=50, null=True)),
                ('outlet_owned', models.CharField(blank=True, max_length=50, null=True)),
                ('outstanding_amount', models.FloatField(blank=True, null=True)),
                ('opening_crates', models.IntegerField(blank=True, null=True)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_basic_details',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpCities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_id', models.IntegerField()),
                ('state_name', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_cities',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpContactNumbers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('contact_type', models.CharField(max_length=50)),
                ('contact_number', models.CharField(max_length=15)),
                ('is_primary', models.IntegerField()),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_contact_numbers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpContactPersons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('contact_person_name', models.CharField(max_length=10)),
                ('designation', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=15)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_contact_persons',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpContactTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_type', models.CharField(max_length=100)),
                ('status', models.IntegerField()),
                ('create_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_contact_types',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpCountries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_countries',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpDepartments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_id', models.IntegerField()),
                ('organization_name', models.CharField(max_length=150)),
                ('department_name', models.CharField(max_length=100)),
                ('landline_country_code', models.CharField(max_length=10)),
                ('landline_state_code', models.CharField(max_length=10)),
                ('landline_number', models.CharField(max_length=15)),
                ('extension_number', models.CharField(max_length=10)),
                ('mobile_country_code', models.CharField(max_length=10)),
                ('mobile_number', models.CharField(max_length=15)),
                ('email', models.CharField(max_length=50)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_departments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpDistributorAreaAllocations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('zone_id', models.IntegerField()),
                ('zone_name', models.CharField(max_length=100)),
                ('town_id', models.IntegerField()),
                ('town_name', models.IntegerField()),
                ('route_id', models.IntegerField()),
                ('route_name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_distributor_area_allocations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpDistributorProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('sku_code', models.CharField(max_length=50)),
                ('product_id', models.IntegerField()),
                ('product_name', models.CharField(max_length=100)),
                ('product_variant_id', models.CharField(max_length=50)),
                ('product_mrp', models.FloatField()),
                ('product_sale_price', models.FloatField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_distributor_products',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpFavorites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('favorite', models.CharField(blank=True, max_length=100, null=True)),
                ('link', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_favorites',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpModules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_name', models.CharField(max_length=100)),
                ('link', models.CharField(blank=True, max_length=100, null=True)),
                ('icon', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_modules',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpOrganizations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_name', models.CharField(max_length=150)),
                ('landline_country_code', models.CharField(max_length=10)),
                ('landline_state_code', models.CharField(max_length=10)),
                ('landline_number', models.CharField(max_length=15)),
                ('mobile_country_code', models.CharField(max_length=10)),
                ('mobile_number', models.CharField(max_length=15)),
                ('email', models.CharField(max_length=50)),
                ('address', models.TextField(blank=True, null=True)),
                ('pincode', models.CharField(blank=True, max_length=8, null=True)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_organizations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(max_length=100)),
                ('slug', models.CharField(max_length=150)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpRolePermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_id', models.IntegerField()),
                ('module_id', models.IntegerField(blank=True, null=True)),
                ('sub_module_id', models.IntegerField(blank=True, null=True)),
                ('permission_id', models.BigIntegerField(blank=True, null=True)),
                ('workflow', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_role_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpRoles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_id', models.IntegerField()),
                ('organization_name', models.CharField(max_length=100)),
                ('department_id', models.IntegerField()),
                ('department_name', models.CharField(max_length=100)),
                ('role_name', models.CharField(max_length=100)),
                ('reporting_department_id', models.IntegerField()),
                ('reporting_department_name', models.CharField(max_length=100)),
                ('reporting_role_id', models.IntegerField()),
                ('reporting_role_name', models.CharField(max_length=100)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_roles',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpRoleWorkflowPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_id', models.IntegerField()),
                ('module_id', models.IntegerField()),
                ('sub_module_id', models.IntegerField()),
                ('permission_id', models.IntegerField()),
                ('level_id', models.IntegerField()),
                ('level', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255)),
                ('workflow_level_dept_id', models.IntegerField()),
                ('workflow_level_role_id', models.IntegerField()),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_role_workflow_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpRoutes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_routes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpStates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_id', models.IntegerField()),
                ('country_name', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_states',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpSubModules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_id', models.IntegerField()),
                ('module_name', models.CharField(max_length=100)),
                ('sub_module_name', models.CharField(max_length=100)),
                ('link', models.CharField(max_length=100)),
                ('icon', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_sub_modules',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpTowns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone_id', models.CharField(max_length=255)),
                ('zone_name', models.CharField(max_length=255)),
                ('town', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_towns',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpUserAreaAllocations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('zone_id', models.IntegerField()),
                ('zone_name', models.CharField(max_length=100)),
                ('town_id', models.IntegerField()),
                ('town_name', models.IntegerField()),
                ('route_id', models.IntegerField(blank=True, null=True)),
                ('route_name', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_user_area_allocations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpUserAttendanceLocations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('attendance_config_id', models.IntegerField()),
                ('distributor_ss_id', models.IntegerField()),
                ('distributor_ss_name', models.CharField(max_length=255)),
                ('periphery', models.IntegerField()),
                ('timing', models.TimeField()),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_user_attendance_locations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpUserDocuments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('aadhaar_card', models.CharField(blank=True, max_length=255, null=True)),
                ('pan_card', models.CharField(blank=True, max_length=255, null=True)),
                ('cin', models.CharField(blank=True, max_length=255, null=True)),
                ('gstin', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_user_documents',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpWorkflowLevels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=15)),
                ('priority', models.CharField(blank=True, max_length=10, null=True)),
                ('color', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_workflow_levels',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpWorkingShifts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('working_shift', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_working_shifts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpZones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_zones',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.CharField(max_length=100, null=True)),
                ('loader', models.TextField(null=True)),
                ('page_limit', models.IntegerField(default='10', null=True)),
                ('is_active', models.IntegerField(default='1')),
            ],
            options={
                'db_table': 'configuration',
            },
        ),
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_id', models.IntegerField()),
                ('department_name', models.CharField(max_length=200)),
                ('land_line_code', models.CharField(max_length=3, null=True)),
                ('phone_code', models.CharField(max_length=6, null=True)),
                ('landline_no', models.CharField(max_length=20, null=True)),
                ('dept_ext', models.CharField(max_length=3, null=True)),
                ('mobile_code', models.CharField(max_length=6, null=True)),
                ('mobile_no', models.CharField(max_length=10, null=True)),
                ('email_id', models.CharField(max_length=50, null=True)),
                ('is_active', models.IntegerField(default='1')),
            ],
            options={
                'db_table': 'departments',
            },
        ),
        migrations.CreateModel(
            name='Organizations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_name', models.CharField(max_length=200)),
                ('land_line_code', models.CharField(max_length=3, null=True)),
                ('phone_code', models.CharField(max_length=6, null=True)),
                ('landline_no', models.CharField(max_length=20, null=True)),
                ('mobile_code', models.CharField(max_length=6, null=True)),
                ('mobile_no', models.CharField(max_length=10, null=True)),
                ('email_id', models.CharField(max_length=50, null=True)),
                ('address', models.CharField(max_length=500, null=True)),
                ('pincode', models.CharField(max_length=6, null=True)),
                ('is_active', models.IntegerField(default='1')),
            ],
            options={
                'db_table': 'organizations',
            },
        ),
    ]
