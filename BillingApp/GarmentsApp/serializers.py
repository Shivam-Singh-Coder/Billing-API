import re
from rest_framework import serializers
from GarmentsApp import views as garments_views
from GarmentsApp import models as garments_models
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

####################################### shop list serializers #######################################

class GarmentsShopListSerializer(serializers.ModelSerializer):
    # Custom format for created_at and updated_at
    fcreated_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fupdated_at = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = garments_models.GarmentsShopDetails
        fields = ['id', 'shop_name', 'shop_owner_name', 'shop_phone', 'shop_email', 'shop_address', 'fcreated_at', 'fupdated_at']

class GarmentsShopEntrySerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(max_length=100)
    shop_owner_name = serializers.CharField(max_length=100)
    shop_phone = serializers.CharField(max_length=10)
    shop_email = serializers.EmailField(max_length=100, required=False, allow_blank=True)
    shop_address = serializers.CharField(style={'base_template': 'textarea.html'})
    
    # Custom validation for shop_name
    def validate_shop_name(self, value):
        """Ensure shop_name is at least 3 characters long."""
        value = value.strip()  # Trim whitespace
        if len(value) < 3:
            raise serializers.ValidationError("Shop name must be at least 3 characters long.")
        return value
    
    # Custom validation for shop_phone (exactly 10 digits)
    def validate_shop_phone(self, value):
        """Ensure phone number is exactly 10 digits and contains only digits."""
        if not re.fullmatch(r"\d{10}", value):
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        # Check if the phone is unique
        # Check uniqueness excluding the current instance (for updates)
        if self.instance:
            if garments_models.GarmentsShopDetails.objects.filter(shop_phone=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A shop with this phone number already exists.")
        else:
            if garments_models.GarmentsShopDetails.objects.filter(shop_phone=value).exists():
                raise serializers.ValidationError("A shop with this phone number already exists.")
        return value
    
    # Custom validation for shop_email (must be a valid email and unique)
    def validate_shop_email(self, value):
        """Ensure email is valid and unique."""
        if value:
            value = value.strip()  # Trim whitespace
            # Ensure uniqueness excluding current instance (for updates)
            if self.instance:
                if garments_models.GarmentsShopDetails.objects.filter(shop_email=value).exclude(pk=self.instance.pk).exists():
                    raise serializers.ValidationError("A shop with this email address already exists.")
            else:
                if garments_models.GarmentsShopDetails.objects.filter(shop_email=value).exists():
                    raise serializers.ValidationError("A shop with this email address already exists.")
        return value

    def validate(self, data):
        """Trim all string fields before saving."""
        for field in ['shop_name', 'shop_owner_name', 'shop_phone', 'shop_email', 'shop_address']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()
        return data

    class Meta:
        model = garments_models.GarmentsShopDetails
        fields = [
            'shop_name',
            'shop_owner_name',
            'shop_phone',
            'shop_email',
            'shop_address',
        ]

    def create(self, validated_data):
        """Create a new GarmentsShopDetails instance."""
        return garments_models.GarmentsShopDetails.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing GarmentsShopDetails instance."""
        # instance.shop_name = validated_data.get('shop_name', instance.shop_name)
        # instance.shop_owner_name = validated_data.get('shop_owner_name', instance.shop_owner_name)
        # instance.shop_phone = validated_data.get('shop_phone', instance.shop_phone)
        # instance.shop_email = validated_data.get('shop_email', instance.shop_email)
        # instance.shop_address = validated_data.get('shop_address', instance.shop_address)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
####################################### end shop list serializers #######################################

#################################### category serializers ####################################

class GarmentsCategoryListSerializer(serializers.ModelSerializer):
    """Serializer for listing GarmentsCategory instances."""

    # Custom format for created_at and updated_at
    fcreated_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fupdated_at = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = garments_models.GarmentsCategory
        fields = ['id', 'category_name','category_description','fcreated_at','fupdated_at']

class GarmentsCategoryEntrySerializer(serializers.ModelSerializer):
    """Serializer for creating and updating GarmentsCategory instances."""
    category_name = serializers.CharField(max_length=255)
    category_description = serializers.CharField(required=False, allow_blank=True)

    # Custom validation for category_name
    def validate_category_name(self, value):
        """Ensure category name is at least 3 characters long and unique."""
        value = value.strip()  # Trim whitespace
        if len(value) < 3:
            raise serializers.ValidationError("Category name must be at least 3 characters long.")

        # Ensure uniqueness, excluding the current instance during updates
        if self.instance:
            if garments_models.GarmentsCategory.objects.filter(category_name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A category with this name already exists.")
        else:
            if garments_models.GarmentsCategory.objects.filter(category_name=value).exists():
                raise serializers.ValidationError("A category with this name already exists.")

        return value
    
    def validate(self, data):
        """Trim leading and trailing spaces for all string fields before saving."""
        for field in ['category_name', 'category_description']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()
        return data

    class Meta:
        model = garments_models.GarmentsCategory
        fields = [
            'category_name',
            'category_description',
        ]

    def create(self, validated_data):
        """Create a new GarmentsCategory instance."""
        return garments_models.GarmentsCategory.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing GarmentsCategory instance dynamically."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

####################################### end category serializers #######################################

####################################### stock inventory serializers #######################################

class GarmentsStockInventoryListSerializer(serializers.ModelSerializer):
    """Serializer for listing GarmentsStockInventory instances."""

    # Custom format for created_at and updated_at
    fpurchased_at = serializers.DateTimeField(source='purchased_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fcreated_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fupdated_at = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = garments_models.GarmentsStockInventory
        fields = ['id', 'category', 'shop', 'product_name', 'product_description', 'purchase_price', 'sale_price', 'unit', 'expire_at', 'fpurchased_at', 'fcreated_at', 'fupdated_at']

class GarmentsStockInventoryEntrySerializer(serializers.ModelSerializer):
    """Serializer for creating and updating GarmentsStockInventory instances."""
    item_name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    # Custom validation for item_name
    def validate_item_name(self, value):
        """Ensure item name is at least 3 characters long and unique."""
        value = value.strip()  # Trim whitespace
        if len(value) < 3:
            raise serializers.ValidationError("Item name must be at least 3 characters long.")

        # Ensure uniqueness, excluding the current instance during updates
        if self.instance:
            if garments_models.GarmentsStockInventory.objects.filter(item_name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("An item with this name already exists.")
        else:
            if garments_models.GarmentsStockInventory.objects.filter(item_name=value).exists():
                raise serializers.ValidationError("An item with this name already exists.")

        return value
    
    def validate(self, data):
        """Trim leading and trailing spaces for all string fields before saving."""
        for field in ['item_name']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()
        return data

    class Meta:
        model = garments_models.GarmentsStockInventory
        fields = [
            'item_name',
            'quantity',
            'price',
        ]

    def create(self, validated_data):
        """Create a new GarmentsStockInventory instance."""
        return garments_models.GarmentsStockInventory.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing GarmentsStockInventory instance dynamically."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

####################################### end stock inventory serializers #######################################
