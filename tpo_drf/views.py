from django.conf import Settings, settings
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from tpo_drf.models import *
from tpo_drf.serializer import *
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@api_view()
def dashboard(request):
    data = {
        "student_count": User.objects.filter(role='STUDENT').count(),
        "placed_student_count": PlacedStudent.objects.all().count(),
        "drive_count": Drive.objects.all().count(),
        "active_user": ActiveUserSerializer(User.objects.filter(is_staff=False), many=True,
                                            context={"request": request}).data,
        "status": status.HTTP_200_OK
    }
    return Response(data)


class CollegeUserViewSet(ModelViewSet):
    queryset = CollegeInfo.objects.all()
    serializer_class = CollegeUserSerializer

    def create(self, request, *args, **kwargs):
        role = request.data.get('role', None)
        if role == 'STUDENT':
            return Response(
                {'Student_list': CollegeUserSerializer(CollegeInfo.objects.filter(role='STUDENT'), many=True).data},
                status=status.HTTP_200_OK)
        elif role == 'TEACHER':
            return Response(
                {'Teacher_list': CollegeUserSerializer(CollegeInfo.objects.filter(role='TEACHER'), many=True).data},
                status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Role not found.', 'status': status.HTTP_404_NOT_FOUND})


class CreateStudentViewSet(ModelViewSet):
    serializer_class = CollegeUserViewSet
    queryset = CollegeInfo.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            first_name = request.data.get('first_name')
            middle_name = request.data.get('middle_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            contact = request.data.get('contact')
            department = request.data.get('department')
            role = request.data.get('role')
            i_card_no = request.data.get('i_card_no')

            obj = CollegeInfo.objects.create(first_name=first_name, middle_name=middle_name, last_name=last_name,
                                             email=email, contact=contact, department=department, role=role,
                                             i_card_no=i_card_no)

            return Response({"message": "Student Added in College Records.", 'status': status.HTTP_200_OK})
        except Exception as e:
            return Response({"message": "Something went wrong.", "error": e, 'status': status.HTTP_404_NOT_FOUND})


class UserListViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer

    def create(self, request, *args, **kwargs):
        role = request.data.get('role', None)
        if role == 'STUDENT':
            return Response(
                {'Student_list': CollegeUserSerializer(User.objects.filter(role='STUDENT'), many=True).data},
                status=status.HTTP_200_OK)
        elif role == 'TEACHER':
            return Response(
                {'Teacher_list': CollegeUserSerializer(User.objects.filter(role='TEACHER'), many=True).data},
                status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        data = {
            "first_name": request.data.get('first_name'),
            "last_name": request.data.get('last_name'),
            "username": request.data.get('email'),
            "email": request.data.get('email'),
            "password": request.data.get('password'),
            "contact": request.data.get('contact'),
            "dob": request.data.get('dob'),
            "address": request.data.get('address'),
            "branch": request.data.get('branch'),
            "department": request.data.get('department'),
            "aggregate": request.data.get('aggregate'),
            "role": request.data.get('role'),
            "i_card_no": request.data.get('i_card_no'),
            "academic_year": request.data.get('academic_year'),

        }
        try:
            obj = CollegeInfo.objects.filter(first_name=data['first_name'], last_name=data['last_name'],
                                             i_card_no=data['i_card_no']).exists()
            if obj:
                prfile_pic = request.FILES['profile_pic']
                user_object = User.objects.create(**data)
                user_object.set_password(data['password'])
                user_object.profile_pic = prfile_pic
                user_object.save()
                return Response({"message": "User registered successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User is not found in College Records."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": "User Not Found in College Records.", "ERROR": e},
                            status=status.HTTP_404_NOT_FOUND)


class LoginViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('email')
        password = request.data.get('password')

        if username is not None and password is not None:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                user.status = True
                user.save()
                return Response(
                    {"data": UserSerializer(user, context={'request': request}).data, "status": "200",
                     "message": "success"})
            else:
                return Response({"message": "Invalid credentials.", "status": '404'})


@api_view()
def logout_view(request):
    id = request.query_params.get('id')
    if id:
        obj = User.objects.get(pk=id)
        obj.status = False
        obj.save()
    request.session.flush()
    return Response({'message': 'User Logout Successfully.'}, status=status.HTTP_200_OK)


class DriveViewSet(ModelViewSet):
    queryset = Drive.objects.all()
    queryset = Drive.objects.all()
    serializer_class = DriveSerializer

    def list(self, request, *args, **kwargs):
        # get criteria from request
        criteria = self.request.query_params.get('criteria')
        if criteria:
            return Response(
                {'drive_list': DriveSerializer(Drive.objects.filter(criteria__gte=criteria), many=True).data})
        else:
            return Response({'drive_list': DriveSerializer(Drive.objects.all(), many=True).data})

    def create(self, request, *args, **kwargs):
        data = request.data
        obj = Drive.objects.create(**data)
        if obj:
            return Response({"message": "Drive created successfully.", "status": status.HTTP_201_CREATED})
        else:
            return Response({"message": "Something went wrong.", "status": status.HTTP_400_BAD_REQUEST})


class PlacedStudentViewSet(ModelViewSet):
    queryset = PlacedStudent.objects.all()
    serializer_class = PlacedStudentSerializer

    def create(self, request, *args, **kwargs):
        try:
            student_i_card_no = request.data.get('student_i_card_no')
            company_name = request.data.get('company_name')
            designation = request.data.get('designation')
            package = request.data.get('package')
            location = request.data.get('location')
            joining_date = request.data.get('joining_date')
            placement_date = request.data.get('placement_date')
            student_object = User.objects.get(i_card_no=student_i_card_no)
            student_object.placement = True
            student_object.save()

            if PlacedStudent.objects.filter(student_id=student_object.id, company_name=company_name).exists():
                return Response({"message": "This Student is already placed in " + company_name,
                                 'status': status.HTTP_400_BAD_REQUEST})

            obj = PlacedStudent.objects.create(student=student_object, company_name=company_name,
                                               designation=designation,
                                               package=package, location=location, joining_date=joining_date,
                                               placement_date=placement_date)
            # return Response(PlacedStudentSerializer(obj).data, status=status.HTTP_201_CREATED)
            return Response({"message": "Added student in placed student.", 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({"message": "Something went wrong.", "error": e, "status": status.HTTP_400_BAD_REQUEST})

    def list(self, request, *args, **kwargs):
        return Response({'placed_student_list': PlacedStudentSerializer(PlacedStudent.objects.all(), many=True).data})


#

class CollegeStudentViewSet(ModelViewSet):
    queryset = CollegeInfo.objects.filter(role='STUDENT')
    serializer_class = CollegeStudentSerializer

    def list(self, request, *args, **kwargs):
        return Response(
            {"student_list": CollegeStudentSerializer(CollegeInfo.objects.filter(role='STUDENT'), many=True).data},
            status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        student_data = {
            'i_card_no': request.data.get("i_card_no"),
            'first_name': request.data.get("first_name"),
            'middle_name': request.data.get("middle_name"),
            'last_name': request.data.get("last_name"),
            'email': request.data.get("email"),
            'contact': request.data.get("contact"),
            'department': request.data.get("department"),
            'admission_year': request.data.get("admission_year"),
            'role': request.data.get("role")
        }

        if CollegeInfo.objects.filter(email=student_data['email']).exists():
            return Response({'message': 'Email is already registered.', 'status': status.HTTP_404_NOT_FOUND})
        else:
            obj = CollegeInfo.objects.create(**student_data)
        return Response({'message': 'Student added in college records.', 'status': status.HTTP_201_CREATED})


class CollegeTeacherViewSet(ModelViewSet):
    queryset = CollegeInfo.objects.filter(role='TEACHER')
    serializer_class = CollegeStudentSerializer

    def list(self, request, *args, **kwargs):
        return Response(
            {"teacher_list": CollegeStudentSerializer(CollegeInfo.objects.filter(role='TEACHER'), many=True).data,
             "status": status.HTTP_200_OK})

    def create(self, request, *args, **kwargs):
        teacher_data = {
            'i_card_no': request.data.get("i_card_no", None),
            'first_name': request.data.get("first_name", None),
            'middle_name': request.data.get("middle_name", None),
            'last_name': request.data.get("last_name", None),
            'email': request.data.get("email", None),
            'contact': request.data.get("contact", None),
            'department': request.data.get("department", None),
            'role': request.data.get("role", None)
        }

        if CollegeInfo.objects.filter(email=teacher_data['email'], contact=teacher_data['contact']).exists():
            return Response({'message': 'Email or contact already registered.', 'status': status.HTTP_404_NOT_FOUND}, )
        else:
            obj = CollegeInfo.objects.create(**teacher_data)
        return Response({'message': 'Teacher added in college records.', 'status': status.HTTP_200_OK})


class TpoStudentViewSet(ModelViewSet):
    queryset = User.objects.filter(role="STUDENT")
    serializer_class = TpoStudentSerializer

    def list(self, request, *args, **kwargs):
        return Response({"student_list": TpoStudentSerializer(User.objects.filter(role="STUDENT"), many=True,
                                                              context={'request': request}).data,
                         'status': status.HTTP_200_OK})


class TpoTeacherViewSet(ModelViewSet):
    queryset = User.objects.filter(role="TEACHER")
    serializer_class = TpoTeacherSerializer

    def list(self, request, *args, **kwargs):
        return Response({"teacher_list": TpoTeacherSerializer(User.objects.filter(role="TEACHER"), many=True,
                                                              context={'request': request}).data,
                         'status': status.HTTP_200_OK})


class ChatViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def list(self, request, *args, **kwargs):
        sender = int(self.request.query_params.get('sender'))
        receiver = int(self.request.query_params.get('receiver'))
        chat_data = MessageSerializer(Message.objects.filter(sender_id=sender, receiver_id=receiver) |
                                      Message.objects.filter(sender_id=receiver, receiver_id=sender), many=True).data

        return Response({'receiver': receiver, 'messages': chat_data, 'status': status.HTTP_200_OK})


@api_view(['GET'])
def send_notification(request):
    drive_id = request.query_params.get('drive_id')
    if drive_id is not None:
        drive_obj = Drive.objects.get(pk=3)
        try:
            subject = 'Campus drive of ' + drive_obj.company_name
            html_message = render_to_string('drive_notification.html', {'drive_obj': drive_obj})
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER

            for user in User.objects.filter(is_staff=False, role='STUDENT'):
                user_email = user.email
                # to = 'hemantbadhe1305@gmail.com'
                to = user_email

                mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

            return Response({'message': 'success', 'status': status.HTTP_200_OK})
        except Exception as e:
            return Response({"message": 'failure', 'status': status.HTTP_400_BAD_REQUEST})

    return Response({'message': 'failure', 'status': status.HTTP_400_BAD_REQUEST})
