# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Attributes(models.Model):
    attribute = models.CharField(max_length=50)
    table_name = models.CharField(max_length=100, blank=True, null=True)
    form = models.TextField(blank=True, null=True)
    script = models.TextField(blank=True, null=True)
    style = models.TextField(blank=True, null=True)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'attributes'
