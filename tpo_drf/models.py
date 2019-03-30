from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

ROLE_TYPE = (
    ('TEACHER', 'TEACHER'),
    ('STUDENT', 'STUDENT')
)

DEPARTMENT = (
    ('Computer_Engineering', 'Computer Engineering'),
    ('IT', 'IT'),
    ('Electronic & Communication Engineering', 'Electronic & Communication Engineering'),
    ('Mechanical Engineering', 'Mechanical Engineering'),
    ('Civil Engineering', 'Civil Engineering'),
)


class CollegeInfo(models.Model):
    i_card_no = models.CharField(max_length=16, null=True, blank=True)
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    middle_name = models.CharField(max_length=64, null=True, blank=True)
    email = models.CharField(max_length=64, null=True, blank=True, unique=True)
    contact = models.CharField(max_length=64, null=True, blank=True, unique=True)
    department = models.CharField(max_length=64, blank=True)
    admission_year = models.CharField(max_length=112, null=True, blank=True)
    role = models.CharField(max_length=64, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {} {}".format(self.first_name, self.middle_name, self.last_name)

    class Meta:
        db_table = 'college_info'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    #
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    contact = models.CharField(max_length=15, null=True)
    dob = models.DateField(null=True)
    address = models.CharField(max_length=512, null=True)
    branch = models.CharField(max_length=64, null=True, blank=True)
    academic_year = models.CharField(max_length=8, null=True, blank=True)
    placement = models.BooleanField(default=False)
    aggregate = models.CharField(max_length=8, null=True, blank=True)
    role = models.CharField(max_length=64, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='User_Profile_Picture', null=True, blank=True)
    text = models.CharField(max_length=112, null=True, blank=True)
    i_card_no = models.CharField(max_length=64, null=True, blank=True)
    resume = models.FileField(upload_to="Student's Resumes", null=True, blank=True)
    status = models.BooleanField(default=False)
    department = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        db_table = 'custom_user'


class Drive(models.Model):
    company_name = models.CharField(max_length=224, null=True, blank=True)
    designation = models.CharField(max_length=112, null=True, blank=True)
    package = models.CharField(max_length=112, null=True, blank=True)
    criteria = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    apply_link = models.CharField(max_length=224, null=True, blank=True)
    drive_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} {}".format(self.company_name, self.designation)

    class Meta:
        db_table = 'company_drive'


class PlacedStudent(models.Model):
    student = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING)
    company_name = models.CharField(max_length=112, null=True, blank=True)
    designation = models.CharField(max_length=64, null=True, blank=True)
    package = models.CharField(max_length=16, null=True, blank=True)
    location = models.CharField(max_length=224, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    placement_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'placed_student'


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('timestamp',)
