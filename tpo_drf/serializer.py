from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from tpo_drf.models import *


class CollegeUserSerializer(ModelSerializer):
    class Meta:
        model = CollegeInfo
        fields = "__all__"


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'password', 'username', 'last_login', 'username', 'is_staff', 'is_active', 'date_joined', 'placement',
            'role',
            'text', 'created_at', 'groups', 'user_permissions', 'is_superuser')


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'is_superuser', 'groups', 'user_permissions', 'is_staff', 'is_active', 'date_joined', 'text', 'created_at',)

    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     obj = User.objects.create(**validated_data)
    #     obj.set_password(password)
    #     obj.text = password
    #     obj.save()
    #     return obj


class ActiveUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'profile_pic', 'i_card_no', 'role', 'academic_year', 'department', ]


class StudentSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'id', 'password', 'last_login', 'username', 'is_staff', 'is_active', 'date_joined', 'placement', 'role',
            'text', 'created_at', 'groups', 'user_permissions', 'is_superuser')


class DriveSerializer(ModelSerializer):
    class Meta:
        model = Drive
        # fields = '__all__'
        exclude = ['created_at', ]


class PlacedStudentSerializer(ModelSerializer):
    # student = StudentSerializer()
    first_name = serializers.CharField(source='student.first_name')
    last_name = serializers.CharField(source='student.last_name')
    email = serializers.CharField(source='student.email')
    contact = serializers.CharField(source='student.contact')
    aggregate = serializers.CharField(source='student.aggregate')
    profile_pic = serializers.CharField(source='student.profile_pic')

    class Meta:
        model = PlacedStudent
        fields = (
            'id', 'first_name', 'last_name', 'email', 'contact', 'aggregate', 'profile_pic', 'company_name',
            'designation', 'package', 'location', 'joining_date',
            'placement_date')


#
class CollegeStudentSerializer(ModelSerializer):
    class Meta:
        model = CollegeInfo
        fields = "__all__"


class TpoStudentSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_superuser', 'username', 'is_staff', 'is_active', 'date_joined', 'role',
                   'text', 'created_at', 'groups', 'user_permissions', ]


class TpoTeacherSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_superuser', 'username', 'is_staff', 'is_active', 'date_joined', 'role',
                   'text', 'created_at', 'groups', 'user_permissions', 'academic_year', 'placement', 'aggregate',
                   'resume', ]


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

# class MessageSerializer(ModelSerializer):
#     class Meta:
#         model = Message
