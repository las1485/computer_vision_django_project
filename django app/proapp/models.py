# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

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
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
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
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

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


class Executions(models.Model):
    created_at = models.DateTimeField()
    spot = models.CharField(max_length=45)
    run = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'executions'


class LastestStats(models.Model):
    created_at = models.DateTimeField()
    spot = models.CharField(max_length=45)
    run = models.IntegerField(blank=True, null=True)
    surfable_waves = models.IntegerField(blank=True, null=True)
    left_waves = models.IntegerField(blank=True, null=True)
    right_waves = models.IntegerField(blank=True, null=True)
    set_interval = models.IntegerField(blank=True, null=True)
    waves_per_10min = models.IntegerField(blank=True, null=True)
    avg_wave_distance = models.IntegerField(blank=True, null=True)
    avg_wave_duration = models.IntegerField(blank=True, null=True)
    distance_outside = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lastest_stats'


class Momentos(models.Model):
    created_at = models.DateTimeField()
    praia = models.CharField(max_length=45)
    momento1 = models.CharField(max_length=45)
    momento2 = models.CharField(max_length=45)
    momento3 = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'momentos'


class SensorConnectionControl(models.Model):
    created_at = models.DateTimeField()
    spot = models.CharField(max_length=45)
    run = models.IntegerField()
    framecount = models.CharField(max_length=45)
    missed_frame = models.TextField()

    class Meta:
        managed = False
        db_table = 'sensor_connection_control'


class Validation(models.Model):
    created_at = models.DateTimeField()
    spot = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    file = models.CharField(max_length=100)
    coords = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'validation'


class Waves(models.Model):
    created_at = models.DateTimeField()
    spot = models.CharField(max_length=45)
    direction = models.CharField(max_length=45)
    start_pixel = models.CharField(max_length=45)
    tracing = models.TextField()
    wave_time_start = models.CharField(max_length=45)
    wave_time_end = models.CharField(max_length=45)
    run = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'waves'
