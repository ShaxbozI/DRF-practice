from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import exceptions
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound


from shared.utility import check_email_or_phone, send_email, chack_user_type
from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, CODE_VERIFIED, NEW, DONE, UP_PHOTO




class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required = False)    
        
    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )
        extra_kwargs = {
            'auth_type': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False}
        }
        
    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        print(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            print(code)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone, code)
            # send_phone_code(user.phone_number, code)
        
        user.save()
        return user
        
    
    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data
    
    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        print('user_input', user_input)
        print('input_type', input_type)
        
        if input_type=='email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        elif input_type=='phone':
            data = {
                'phone': user_input,
                'auth_type': VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': 'Email yoki telfon raqam kiriting'
            }
            raise ValidationError(data)
        
        return data
    
    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                "success": False,
                "message": "bu emaildagi foydalanvchi mavjud"
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone=value).exists():
            data = {
                "success": False,
                "message": "bu telfon raqamidagi foydalanvchi mavjud"
            }
            raise ValidationError(data)
        return value
    
    
    def to_representation(self, instance):
        print("to_rep", instance)
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        
        return data
    
    
class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only = True, required = True)
    last_name = serializers.CharField(write_only = True, required = True)
    username = serializers.CharField(write_only = True, required = True)
    password = serializers.CharField(write_only = True, required = True)
    confrim_password = serializers.CharField(write_only = True, required = True)
    
    
    def validate(self, data):
        password = data.get('password', None)
        confrim_password = data.get('confrim_password', None)
        if password != confrim_password:
            raise ValidationError(
                {
                    "message": "Kiritilgan parol mos kelmadi"
                }
            )
        
        if password:
            validate_password(password)
            validate_password(confrim_password)
            
        return data
    
    def validate_username(self, username):
        if len(username) < 5 or len(username) >30:
            raise ValidationError(
                {
                    "message": "Foydalanuvchi nomi uzunligi 5 va 30 oralig'ida bo'lishi kerak"
                }
            )
        
        if username.isdigit():
            raise ValidationError(
                {
                    "message": "Foydalanuvchi nomi Faqat raqamdan iborat bo'lmasligi kerak"
                }
            )
        return username
    
    def update(self, instance, validate_data):
        
        instance.first_name = validate_data.get('first_name', instance.first_name)
        instance.last_name = validate_data.get('first_name', instance.last_name)
        instance.password = validate_data.get('first_name', instance.password)
        instance.username = validate_data.get('first_name', instance.username )
        
        if validate_data.get('password'):
            instance.set_password(validate_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance
            
    
    
class ChangeUserPhoto(serializers.Serializer):
    photo = serializers.ImageField(validators = [FileExtensionValidator(allowed_extensions = ['jpg', 'png', 'jpeg'])])
    
    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = UP_PHOTO
            instance.save()
        return instance
    
    
    
class LoginUserSerializer(TokenObtainPairSerializer):
    
    def __init__(self, *args, **kwargs):
        super(LoginUserSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required = True)
        self.fields['username'] = serializers.CharField(required = False, read_only = True)
        
    def auth_validate(self, data):
        user_input = data.get('userinput')
        if chack_user_type(user_input) == 'username':
            username = user_input
        
        elif chack_user_type(user_input) == 'email':
            user = self.get_user(email__iexact = user_input)
            username = user.username
        elif chack_user_type(user_input) == 'phone':
            user = self.get_user(phone = user_input)
            username = user.username
        else:
            data = {
                'success': True,
                "message": "Noto'g'ri malumot kiritdingiz"
            }
            raise ValidationError(data)
        authentication_kwargs = {
            self.username_field: username,
            'password': data['password']
        }
        current_user = User.objects.filter(username__iexact = username).first()
        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError(
                {
                "success": False,
                "message": "Ro'yhatdan o'tish yakunlanmagan"
            }
            )
        user = authenticate(**authentication_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError(
                {
                "success": False,
                "message": "Login yoki parol xato"
            }
            )
            
    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in (DONE, UP_PHOTO):
            raise PermissionDenied('siz login qila olmaysiz')
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data['full_name'] = self.user.full_name
        return data
        
    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {
                    "message": "Bunday foydalanuvchi mavjud emas"
                }
            )
        return users.first()
    
    
    
class LoginRefreshSerializer(TokenRefreshSerializer):
    
    def validate(self, data):
        data = super().validate(data)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id = user_id)
        update_last_login(None, user)
        return data
        
        
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    
class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only = True, required = True)
    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone', None)
        if email_or_phone is None:
            raise ValidationError(
                    {
                    "success": False,
                    "message": "Email yoki Telfon raqam kiritish shart"
                    }
                )
        user = User.objects.filter(Q(phone = email_or_phone) | Q(email = email_or_phone))
        if not user.exists():
            raise NotFound(detail = "Bunday foydalanuvchi mavjud emas")
        attrs['user'] = user.first()
        return attrs


class RessetPaswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only = True)
    password = serializers.CharField(min_length = 8, required = True, write_only = True)
    confrim_password = serializers.CharField(min_length = 8, required = True, write_only = True)
    
    class Meta:
        model = User
        fields = (
            "id",
            "password",
            "confrim_password"
        )
        
    def validate(self, data):
        password = data.get("password", None)
        confrim_password = data.get("password", None)
        if password != confrim_password:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Email yoki Telfon raqam kiritish shart"
                }
            )
        if password:
            validate_password(password)
        return data
    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        return super(RessetPaswordSerializer, self).update(instance, validated_data)
        