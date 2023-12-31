# Generated by Django 3.1.2 on 2020-10-26 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.IntegerField()),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.IntegerField()),
                ('is_active', models.IntegerField()),
                ('date_joined', models.DateTimeField()),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_time', models.DateTimeField()),
                ('object_id', models.TextField(blank=True, null=True)),
                ('object_repr', models.CharField(max_length=200)),
                ('action_flag', models.PositiveSmallIntegerField()),
                ('change_message', models.TextField()),
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('applied', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_migrations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('session_key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('session_data', models.TextField()),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_session',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SpCountryCodes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_code', models.CharField(max_length=10)),
                ('status', models.IntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'sp_country_codes',
                'managed': False,
            },
        ),
        migrations.AlterModelOptions(
            name='configuration',
            options={'managed': False},
        ),
        migrations.RemoveField(
            model_name='departments',
            name='dept_ext',
        ),
        migrations.RemoveField(
            model_name='departments',
            name='email_id',
        ),
        migrations.RemoveField(
            model_name='departments',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='departments',
            name='land_line_code',
        ),
        migrations.RemoveField(
            model_name='departments',
            name='landline_no',
        ),
        migrations.RemoveField(
            model_name='departments',
            name='mobile_code',
        ),
        migrations.RemoveField(
            model_name='departments',
            name='mobile_no',
        ),
        migrations.RemoveField(
            model_name='departments',
            name='phone_code',
        ),
        migrations.RemoveField(
            model_name='organizations',
            name='email_id',
        ),
        migrations.RemoveField(
            model_name='organizations',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='organizations',
            name='land_line_code',
        ),
        migrations.RemoveField(
            model_name='organizations',
            name='landline_no',
        ),
        migrations.RemoveField(
            model_name='organizations',
            name='mobile_code',
        ),
        migrations.RemoveField(
            model_name='organizations',
            name='mobile_no',
        ),
        migrations.RemoveField(
            model_name='organizations',
            name='phone_code',
        ),
        migrations.AddField(
            model_name='departments',
            name='email',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='departments',
            name='extension_number',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='departments',
            name='landline_country_code',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='departments',
            name='landline_number',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='departments',
            name='landline_state_code',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='departments',
            name='mobile_country_code',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='departments',
            name='mobile_number',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='departments',
            name='status',
            field=models.IntegerField(default='1'),
        ),
        migrations.AddField(
            model_name='organizations',
            name='email',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='organizations',
            name='landline_country_code',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='organizations',
            name='landline_number',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='organizations',
            name='landline_state_code',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='organizations',
            name='mobile_country_code',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='organizations',
            name='mobile_number',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='organizations',
            name='status',
            field=models.IntegerField(default='1'),
        ),
        migrations.AlterModelTable(
            name='departments',
            table='sp_departments',
        ),
        migrations.AlterModelTable(
            name='organizations',
            table='sp_organizations',
        ),
    ]
