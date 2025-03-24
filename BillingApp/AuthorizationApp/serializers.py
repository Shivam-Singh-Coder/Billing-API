import string
from AuthorizationApp import models as auth_models
from rest_framework import serializers
from django.contrib.auth import password_validation
from SimpleInvoice import models as simple_invoice_models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        # Ensure username and password are provided
        if not username or not password:
            raise serializers.ValidationError({"message": "Username and password are required."})

        # Authenticate the user
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({"message": "Invalid credentials."})

        if not user.is_active:
            raise serializers.ValidationError({ "message": "User account is disabled."})

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "isSuccess": True,
            "message": "Login successful!",
            "data": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name":user.first_name
                }
            }
        }

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    # Fields for the registration form
    username = serializers.CharField(max_length=200)
    email = serializers.EmailField(required=False,allow_blank=True)  # Making email optional
    password = serializers.CharField(write_only=True, required=True, max_length=200)
    first_name = serializers.CharField(max_length=200)
    app_name = serializers.ChoiceField(choices=[('web', 'Web App'), ('mobile', 'Mobile App')], required=False)

    class Meta:
        model = auth_models.User
        fields = ['username', 'password', 'first_name', 'email','app_name']

    def validate_password(self, value):
        """Ensure that the password is valid according to Django's password validation rules."""
        password_validation.validate_password(value)
        return value
    
    # def validate_app_name(self, value):
    #     if value in ['web', 'mobile']:
    #         return value
    #     elif value is None:
    #         return 'web'
    #     else:
    #         raise serializers.ValidationError("App name should be either web or mobile")

    def validate(self, data):
        """Trim all string fields before saving and check app_name"""
        # Trim the fields that are strings
        for field in ['software_type_name', 'app_name']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()

        # Check if 'app_name' is not provided, set it to 'web' by default
        if 'app_name' not in data:
            data['app_name'] = 'web'  # Set default to 'web' if not provided

        return data
####################################### software type list serializers #######################################

class SoftwareTypeSerializer(serializers.ModelSerializer):
    software_type_name = serializers.CharField(max_length=100, source="name")
    fcreated_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fupdated_at = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    app_name = serializers.ChoiceField(choices=[('web', 'Web App'), ('mobile', 'Mobile App')], required=False)
    
    # Custom validation for software_type_name
    def validate_software_type_name(self, value):
        """Ensure Software type name"""
        value = value.strip()  # Trim whitespace
        if value and len(value) > 0:
            if self.instance:
                if auth_models.SoftwareType.objects.filter(name=value).exclude(id=self.instance.pk).exists():
                    raise serializers.ValidationError("Software type name already exists.")
            else:
                if auth_models.SoftwareType.objects.filter(name=value).exists():
                    raise serializers.ValidationError("Software type name already exists.")
        else:
            raise serializers.ValidationError("Software type name is required.")
        return value

    def validate(self, data):
        """Trim all string fields before saving and check app_name"""
        # Trim the fields that are strings
        for field in ['software_type_name', 'app_name']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()

        return data

    class Meta:
        model = auth_models.SoftwareType
        fields = [
            'id',
            'software_type_name',
            'fcreated_at',
            'fupdated_at',
            'app_name',
        ]

    
####################################### end software type serializers #######################################
####################################### company entry list serializers #######################################

class CompanySerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=200, write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, max_length=200)
    software_type = serializers.PrimaryKeyRelatedField(queryset=auth_models.SoftwareType.objects.all(), write_only=True, required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=200)
    company_number = serializers.IntegerField()
    company_address = serializers.CharField(source='address', max_length=200, required=False)
    expire_days = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    app_name = serializers.ChoiceField(choices=[('web', 'Web App'), ('mobile', 'Mobile App')], required=False)
    fcreated_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fupdated_at = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    company_user = serializers.CharField(read_only=True, source='user.username')
    company_software_type = serializers.CharField(read_only=True, source='software_type.name')

    class Meta:
        model = auth_models.CompanyID
        fields = ['id', 'username', 'password', 'email', 'company_name', 'company_number', 'company_address', 'expire_days', 'software_type', 'company_software_type', 'company_user', 'app_name', 'fcreated_at', 'fupdated_at']

    def validate_password(self, value):
        if not self.instance:  # Only enforce validation on create
            value = value.strip()
            if not value:
                raise serializers.ValidationError("Password is required.")
            password_validation.validate_password(value)
        return value

    def validate_username(self, value):
        if not self.instance:  # Only enforce validation on create
            value = value.strip()
            if auth_models.User.objects.filter(username=value).exists():
                raise serializers.ValidationError("Username already exists.")
        return value

    def validate_software_type(self, value):
        if not self.instance and not value:
            raise serializers.ValidationError("Software type is required.")
        return value

    def validate(self, data):
        """Validate that username and password are required during creation"""
        """Validate that username and password are required during creation"""
        errors = {}

        # Username validation
        if 'username' not in data or len(data.get('username', '').strip()) == 0:
            errors['username'] = "Username is required."
        else:
            if auth_models.User.objects.filter(username=data.get('username', '').strip()).exists():
                errors['username'] = "Username already exists."
        
        # Password validation
        if 'password' not in data or len(data.get('password', '').strip()) == 0:
            errors['password'] = "Password is required."
        else:
            password = data.get('password', '').strip()
            try:
                password_validation.validate_password(password)  # This will raise an error if the password is invalid
            except Exception as e:
                errors['password'] = str(e)  # Catch the validation exception and add it to the errors dict
        
        if 'software_type' not in data:
            errors['software_type'] = "Software type is required."

        if errors:
            raise serializers.ValidationError(errors)  # If there are errors, raise them all at once           

        for field in ['username', 'password', 'email', 'company_name', 'company_number', 'company_address', 'expire_days', 'app_name']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()

        if 'expire_days' not in data or data['expire_days'] in [None, '']:
            data['expire_days'] = 0

        if 'app_name' not in data or not data['app_name']:
            data['app_name'] = 'web'

        return data

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        software_type = validated_data.pop('software_type')
        email = validated_data.pop('email', '')
        company_name = validated_data.pop('company_name')
        company_number = validated_data.pop('company_number')
        company_address = validated_data.pop('address')
        expire_days = validated_data.pop('expire_days', 0)
        app_name = validated_data.pop('app_name', 'web')
        user_obj = auth_models.User.objects.create_user(
            username=username,
            email=email,
            first_name=company_name,
            software_type=software_type
        )
        user_obj.set_password(password)
        user_obj.save()
        last_id = auth_models.CompanyID.objects.last()
        last_id = last_id.id + 1 if last_id else 1
        company_obj = auth_models.CompanyID.objects.create(
            user=user_obj,
            company_name=user_obj.first_name,
            company_number=company_number,
            email=user_obj.email,
            address=company_address,
            expire_days=expire_days,
            app_name=app_name,
            software_type=user_obj.software_type,
            invoice_code="INV" + str(last_id)
        )
        simple_invoice_models.SimpleInvoiceNumberGenerate.objects.create(company=company_obj, last_invoice_number=0)
        
        return company_obj

    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)
        company_name = validated_data.pop('company_name', None)
        company_number = validated_data.pop('company_number', None)
        company_address = validated_data.pop('address', None)
        expire_days = validated_data.pop('expire_days', None)

        user_obj = instance.user
        if email:
            user_obj.email = email
        if company_name:
            user_obj.first_name = company_name
        user_obj.save()

        if email:
            instance.email = user_obj.email
        if company_name:
            instance.company_name = user_obj.first_name
        if company_number:
            instance.company_number = company_number
        if company_address:
            instance.address = company_address
        if expire_days is not None:
            instance.expire_days = expire_days

        instance.save()
        return instance
    
####################################### end company entry serializers #######################################