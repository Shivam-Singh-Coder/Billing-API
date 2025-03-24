import re
from rest_framework import serializers
from SimpleInvoice import views as simple_invoice_views
from SimpleInvoice import models as simple_invoice_models
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from datetime import datetime

####################################### stock inventory list serializers #######################################

class SimpleInvoiceStockSerializer(serializers.ModelSerializer):
    """Serializer for stock inventory entry with validation."""

    product_name = serializers.CharField(max_length=100)
    unit = serializers.IntegerField()  # Assuming numeric value (e.g., quantity)
    unit_type = serializers.PrimaryKeyRelatedField(queryset=simple_invoice_models.SimpleInvoiceMeasurementUnit.objects.all(), write_only=True, required=False)  # Relates to unit type
    sale_price = serializers.DecimalField(max_digits=10, decimal_places=2)  # Assuming price is a numeric value
    app_name = serializers.ChoiceField(choices=[('web', 'Web App'), ('mobile', 'Mobile App')], required=False)
    fcreated_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fupdated_at = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    unit_name = serializers.CharField(source="unit_type.name", read_only=True)  # Unit name from the related unit_type model

    def validate_sale_price(self, value):
        """Ensure that the sale price is greater than zero."""
        if value <= 0:
            raise serializers.ValidationError("Sale price must be greater than zero.")
        return value

    def validate_unit(self, value):
        """Ensure that the unit (quantity) is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Unit (quantity) must be greater than zero.")
        return value

    def validate(self, data):
        """Trim all string fields before saving and handle other validations."""
        # Trim spaces from product_name
        if 'product_name' in data and isinstance(data['product_name'], str):
            data['product_name'] = data['product_name'].strip()

        return data

    class Meta:
        model = simple_invoice_models.SimpleInvoiceStockInventory
        fields = ['id', 'product_name', 'unit', 'unit_type', 'sale_price', 'unit_name', 'app_name', 'fcreated_at', 'fupdated_at']

    def create(self, validated_data):
        """Create a new stock inventory entry."""
        # Access the logged-in user
        user = self.context['request'].user
        # Retrieve the associated company (software) from the user
        software = user.company_details

        # Add the 'software' field to validated_data (e.g., company linked to the user)
        validated_data['company'] = software

        # # Create the inventory record with the additional software field
        return simple_invoice_models.SimpleInvoiceStockInventory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing stock inventory entry."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
####################################### end stock inventory serializers #######################################

####################################### generate bill serializers #######################################

class SimpleInvoiceBillItemSerializer(serializers.ModelSerializer):
    """Serializer for listing stock inventory with formatted timestamps."""
    prod_id = serializers.PrimaryKeyRelatedField(queryset=simple_invoice_models.SimpleInvoiceStockInventory.objects.all(),write_only=True)
    product_name = serializers.CharField(source='product.product_name',read_only=True)
    quantity = serializers.IntegerField()
    sub_unit_type = serializers.CharField(max_length=200,source='sub_unit')
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_quantity(self, value):
        """Ensure quantity is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_total_price(self, value):
        """Ensure total price is a positive decimal value."""
        if value <= 0:
            raise serializers.ValidationError("Total price must be greater than zero.")
        return value
    
    def validate(self, data):
        """Trim all string fields before saving and check app_name"""
        # Trim the fields that are strings
        for field in ['software_type_name', 'app_name']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()

        return data

    class Meta:
        model = simple_invoice_models.SimpleInvoiceBillItem
        fields = ['prod_id','product_name', 'quantity', 'sub_unit_type', 'total_price']


class SimpleInvoiceGenerateBillSerializer(serializers.ModelSerializer):
    """Serializer for stock inventory entry with validation."""

    customer_name = serializers.CharField(max_length=200,write_only=True)
    customer_number = serializers.CharField(max_length=15,write_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    grand_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    invoice_item = SimpleInvoiceBillItemSerializer(many=True,write_only=True)
    created_invoice_item = SimpleInvoiceBillItemSerializer(many=True,read_only=True,source='items')
    app_name = serializers.ChoiceField(choices=[('web', 'Web App'), ('mobile', 'Mobile App')], required=False)
    invoice_number = serializers.CharField(read_only=True)
    fcreated_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fupdated_at = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    finvoice_date = serializers.DateTimeField(source='invoice_date', format='%Y-%m-%d %H:%M:%S', read_only=True)
    cust_name = serializers.CharField(source='customer.name',read_only=True)
    cust_number = serializers.IntegerField(source='customer.phone',read_only=True)
    
    def validate_customer_number(self, value):
        """Ensure customer number is a valid phone number."""
        if not re.match(r'^\d{7,15}$', value):
            raise serializers.ValidationError("Customer number should be between 7 to 15 digits.")
        return value
    
    def validate_total_amount(self, value):
        """Ensure total amount is a positive decimal value."""
        if value <= 0:
            raise serializers.ValidationError("Total amount must be greater than zero.")
        if value != self.initial_data['grand_amount'] + self.initial_data['discount_amount']:
            raise serializers.ValidationError("Total amount must be equal to grand amount plus discount amount.")
        return value
    
    def validate_discount_amount(self, value):
        """Ensure discount amount is a positive decimal value."""
        if value < 0:
            raise serializers.ValidationError("Discount amount must be greater than or equal to zero.")
        if value > self.initial_data['total_amount']:
            raise serializers.ValidationError("Discount amount cannot be greater than total amount.")
        if value != self.initial_data['total_amount'] - self.initial_data['grand_amount']:
            raise serializers.ValidationError("Discount amount is not equal to total amount minus grand amount.")
        return value
    
    def validate_grand_amount(self, value):
        """Ensure grand amount is a positive decimal value."""
        if value < 0:
            raise serializers.ValidationError("Grand amount must be greater than or equal to zero.")
        if value != self.initial_data['total_amount'] - self.initial_data['discount_amount']:
            raise serializers.ValidationError("Grand amount is not equal to total amount minus discount amount.")
        return value
    
    def validate_invoice_item(self, value):
        """Ensure invoice item is a list of valid bill items."""
        if not value:
            raise serializers.ValidationError("Invoice item cannot be empty.")
        prod_total_price = 0
        for item in value:
            print(item)
            prod_total_price += item['total_price']
            if not isinstance(item, dict):
                raise serializers.ValidationError("Invalid invoice item.")
        if prod_total_price != self.initial_data['total_amount']:
            raise serializers.ValidationError("Total price of invoice item is not equal to total amount.")
        return value
    
    def validate(self, data):
        """Trim all string fields before saving and check app_name"""
        # Trim the fields that are strings
        for field in ['customer_name', 'customer_number', 'total_amount', 'discount_amount', 'grand_amount', 'invoice_item', 'app_name']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()

        return data
    
    class Meta:
        model = simple_invoice_models.SimpleInvoiceGenerateBill
        fields = ['id','customer_name', 'customer_number','cust_name','cust_number', 'total_amount', 'discount_amount', 'grand_amount', 'invoice_item','created_invoice_item', 'app_name','invoice_number','fcreated_at','fupdated_at','finvoice_date']
    
    def create(self, validated_data):
        """Create a new invoice entry, ensuring customer exists."""
        # Access the logged-in user
        user = self.context['request'].user
        if not user:
            raise serializers.ValidationError("User must be logged in to create an invoice.")
        # Retrieve the associated company (software) from the user
        company = user.company_details
        if not company:
            raise serializers.ValidationError("User must be associated with a company to create an invoice.")
        # Add the 'software' field to validated_data (e.g., company linked to the user)
        validated_data['company'] = company
        invoice_items_data = validated_data.pop('invoice_item')
        customer, created = simple_invoice_models.SimpleInvoiceCustomer.objects.get_or_create(
            company = company,
            phone=validated_data.pop('customer_number'),
            defaults={'name': validated_data.pop('customer_name')}
        )
        validated_data['customer'] = customer

        # Retrieve the last invoice number for the company
        try:
            last_invoice_no = simple_invoice_models.SimpleInvoiceNumberGenerate.objects.get(company=company)
            last_invoice_no = int(last_invoice_no.last_invoice_number) + 1 if last_invoice_no else 1
        except simple_invoice_models.SimpleInvoiceNumberGenerate.DoesNotExist:
            last_invoice_no = 1
            simple_invoice_models.SimpleInvoiceNumberGenerate.objects.create(company=company,last_invoice_number=0)
        
        ### company name of login id
        company_name = company.company_name
        # cp_name = "".join([part[0].upper() for part in company_name.split()[:2]])[:2]
        if ' ' in company_name:
            cp = company_name.split(' ')
            cp_name = str.upper(list(cp[0])[0])+str.upper(list(cp[1])[0])
        else:
            if len(company_name) > 2:
                cp_name = str.upper(list(company_name)[0])+str.upper(list(company_name)[1])
            else:
                cp_name = str.upper(company_name)
        ## genearte invoice number
        current_year = datetime.now().year
        current_month = datetime.now().month

        # if last_invoice_no < 10:
        #     validated_data['invoice_number'] = f"{cp_name}{company.invoice_code}/{current_year % 100:02d}{current_month:02d}00{last_invoice_no}"
        # elif last_invoice_no < 100:
        #     validated_data['invoice_number'] = f"{cp_name}{company.invoice_code}/{current_year % 100:02d}{current_month:02d}0{last_invoice_no}"
        # else:
        #     validated_data['invoice_number'] = f"{cp_name}{company.invoice_code}/{current_year % 100:02d}{current_month:02d}{last_invoice_no}"
        
        validated_data['invoice_number'] = f"{cp_name}{company.invoice_code}/{current_year % 100:02d}{current_month:02d}{last_invoice_no:04d}"

        invoice = simple_invoice_models.SimpleInvoiceGenerateBill.objects.create(**validated_data)
        for item_data in invoice_items_data:
            product = simple_invoice_models.SimpleInvoiceStockInventory.objects.get(id=item_data['prod_id'].id)
            simple_invoice_models.SimpleInvoiceBillItem.objects.create(
                invoice=invoice,
                product=product, 
                quantity=item_data['quantity'], 
                sub_unit=item_data['sub_unit'],
                total_price= item_data['total_price'],
                app_name = invoice.app_name
            )
        simple_invoice_models.SimpleInvoiceNumberGenerate.objects.update_or_create(
            company=company,
            defaults={'last_invoice_number': last_invoice_no}
        )
        return invoice
    
    def update(self, instance, validated_data):
        """Update an existing invoice entry."""
        invoice_items_data = validated_data.pop('invoice_item', [])

        customer, created = simple_invoice_models.SimpleInvoiceCustomer.objects.get_or_create(
            company=instance.company,
            phone=validated_data.pop('customer_number'),
            defaults={'name': validated_data.pop('customer_name')}
        )
        validated_data['customer'] = customer

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        item_prod_id = list()
        if invoice_items_data:
            for item_data in invoice_items_data:
                item_prod_id.append(item_data['prod_id'].id)
                product = simple_invoice_models.SimpleInvoiceStockInventory.objects.get(id=item_data['prod_id'].id)
                try:
                    item_obj = simple_invoice_models.SimpleInvoiceBillItem.objects.filter(invoice=instance,product=product)
                    if item_obj.exists():
                        item_obj.update(
                            quantity=item_data['quantity'],
                            sub_unit=item_data['sub_unit'],
                            total_price=item_data['total_price'],
                            app_name=instance.app_name
                            )
                    else:
                        simple_invoice_models.SimpleInvoiceBillItem.objects.create(
                            invoice=instance,
                            product=product,
                            quantity=item_data['quantity'],
                            sub_unit=item_data['sub_unit'],
                            total_price=item_data['total_price'],
                            app_name=instance.app_name
                            )
                except Exception as e:
                    raise serializers.ValidationError({'Error occured during updation of records': str(e)})
            instance_prod_id = list()
            for item in instance.items.all():
                instance_prod_id.append(item.product.id)
            for prod_id in instance_prod_id:
                if prod_id not in item_prod_id:
                    item_obj = simple_invoice_models.SimpleInvoiceBillItem.objects.filter(invoice=instance,product=simple_invoice_models.SimpleInvoiceStockInventory.objects.get(id=prod_id))
                    if item_obj.exists():
                        item_obj.delete()

        return instance
    
####################################### end stock inventory serializers #######################################

########################### measurement unit serializers #######################
class SimpleInvoiceMeasurementUnitSerializer(serializers.ModelSerializer):
    """Serializer for measurement unit."""
    
    unit_name = serializers.CharField(max_length=255, required=True, source="name")
    fcreated_at = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    fupdated_at = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    app_name = serializers.ChoiceField(choices=[('web', 'Web App'), ('mobile', 'Mobile App')], required=False)

    def validate_unit_name(self, value):
        """Validate the uniqueness of the measurement unit name."""
        if not value:
            raise serializers.ValidationError('Measurement unit cannot be empty')
        
        # Check for uniqueness only if the instance exists (for update operations)
        if self.instance:
            if simple_invoice_models.SimpleInvoiceMeasurementUnit.objects.filter(name=value).exclude(pk=self.instance.id).exists():
                raise serializers.ValidationError('Measurement unit already exists')
        else:
            if simple_invoice_models.SimpleInvoiceMeasurementUnit.objects.filter(name=value).exists():
                raise serializers.ValidationError('Measurement unit already exists')
        
        return value

    def validate(self, data):
        """Trim all string fields before saving and check app_name."""
        # Trim string fields
        for field in ['unit_name', 'app_name']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()
        
        return data

    class Meta:
        model = simple_invoice_models.SimpleInvoiceMeasurementUnit
        fields = ['id', 'unit_name', 'app_name', 'fcreated_at', 'fupdated_at']

    def create(self, validated_data):
        """Create a new measurement unit entry."""
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing measurement unit entry."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
############################# end of measurement unit serializers ##############################
        