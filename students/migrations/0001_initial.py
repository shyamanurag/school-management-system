# Generated by Django 5.2.3 on 2025-06-23 21:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='students.schoolclass')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admission_no', models.CharField(max_length=20, unique=True)),
                ('roll_no', models.CharField(blank=True, max_length=20, null=True)),
                ('admission_date', models.DateField()),
                ('firstname', models.CharField(max_length=100)),
                ('lastname', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='student_images/')),
                ('mobileno', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('pincode', models.CharField(blank=True, max_length=20, null=True)),
                ('religion', models.CharField(blank=True, max_length=50, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('current_address', models.TextField(blank=True, null=True)),
                ('permanent_address', models.TextField(blank=True, null=True)),
                ('adhar_no', models.CharField(blank=True, max_length=20, null=True)),
                ('samagra_id', models.CharField(blank=True, max_length=20, null=True)),
                ('bank_account_no', models.CharField(blank=True, max_length=30, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=100, null=True)),
                ('ifsc_code', models.CharField(blank=True, max_length=20, null=True)),
                ('guardian_name', models.CharField(blank=True, max_length=100, null=True)),
                ('guardian_relation', models.CharField(blank=True, max_length=50, null=True)),
                ('guardian_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('guardian_address', models.TextField(blank=True, null=True)),
                ('father_name', models.CharField(blank=True, max_length=100, null=True)),
                ('father_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('father_occupation', models.CharField(blank=True, max_length=100, null=True)),
                ('mother_name', models.CharField(blank=True, max_length=100, null=True)),
                ('mother_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('mother_occupation', models.CharField(blank=True, max_length=100, null=True)),
                ('guardian_occupation', models.CharField(blank=True, max_length=100, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10, null=True)),
                ('rte', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.category')),
                ('class_enrolled', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.schoolclass')),
                ('section_enrolled', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.section')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
