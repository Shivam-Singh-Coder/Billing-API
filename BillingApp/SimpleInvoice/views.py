from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from SimpleInvoice import models as simple_invoice_models
from SimpleInvoice import serializers as simple_invoice_serializers
# from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from AuthorizationApp.custom_token_error import CustomTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from uuid import UUID

####################################### stock inventory views #######################################

class SimpleInvoiceStockListView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the entire list of stock inventory items.
        """
        try:
            company_id = request.user.company_details
            if not company_id:
                return Response({
                    'isSuccess': False,
                    'message': 'No company details found for the user.',
                }, status=status.HTTP_400_BAD_REQUEST)
            stock_inventory = simple_invoice_models.SimpleInvoiceStockInventory.objects.filter(company=company_id)

            # Check if the inventory list is empty
            if not stock_inventory.exists():
                response_data = {
                    'isSuccess': False,
                    'message': 'No stock items available.',
                }
                return Response(response_data, status=status.HTTP_200_OK)

            # Serialize the stock items list
            stock_list_serializer = simple_invoice_serializers.SimpleInvoiceStockSerializer(stock_inventory, many=True)

            # Create the response data
            response_data = {
                'isSuccess': True,
                'message': 'Stock list retrieved successfully!',
                'data': stock_list_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving stock list: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SimpleInvoiceStockCreateView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles POST request to create a new stock entry.
        """
        try:
            # Serialize the incoming data
            serializer = simple_invoice_serializers.SimpleInvoiceStockSerializer(data=request.data,context={'request': request})

            if serializer.is_valid():
                # Save the new stock entry
                serializer.save()
                response_data = {
                    'isSuccess': True,
                    'message': 'Stock item created successfully!',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            # If data is invalid, return validation errors
            response_data = {
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle unexpected errors
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while creating stock entry: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimpleInvoiceStockDetailView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, stock_id):
        """
        Retrieve a stock entry by ID.
        """
        try:
            company_id = request.user.company_details
            if not company_id:
                return Response({
                    'isSuccess': False,
                    'message': 'No company details found for the user.',
                }, status=status.HTTP_400_BAD_REQUEST)
            shop = simple_invoice_models.SimpleInvoiceStockInventory.objects.filter(id=stock_id, company=company_id).first()
            if not shop:
                response_data = {
                    'isSuccess': False,
                    'message': 'Stock item not found!'
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            serializer = simple_invoice_serializers.SimpleInvoiceStockSerializer(shop)
            response_data = {
                'isSuccess': True,
                'message': 'Stock item retrieved successfully!',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except simple_invoice_models.SimpleInvoiceStockInventory.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Stock item not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving stock: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimpleInvoiceStockUpdateView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, stock_id):
        """
        Fully update a stock entry.
        """
        try:
            # shop = get_object_or_404(simple_invoice_models.SimpleInvoiceStockInventory, id=stock_id)
            company_id = request.user.company_details
            if not company_id:
                return Response({
                    'isSuccess': False,
                    'message': 'No company details found for the user.',
                }, status=status.HTTP_400_BAD_REQUEST)
            shop = simple_invoice_models.SimpleInvoiceStockInventory.objects.filter(id=stock_id,company=company_id).first()
            if not shop:
                response_data = {
                    'isSuccess': False,
                    'message': 'Stock item not found!'
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            serializer = simple_invoice_serializers.SimpleInvoiceStockSerializer(shop, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Stock item updated successfully!',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except simple_invoice_models.SimpleInvoiceStockInventory.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Stock item not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while updating stock! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SimpleInvoiceStockDeleteView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, stock_id):
        """
        Delete a stock record. Prevent deletion if referenced in other tables.
        """
        try:
            # shop = get_object_or_404(simple_invoice_models.SimpleInvoiceStockInventory, id=stock_id)
            company_id = request.user.company_details
            if not company_id:
                return Response({
                    'isSuccess': False,
                    'message': 'No company details found for the user.',
                }, status=status.HTTP_400_BAD_REQUEST)
            shop = simple_invoice_models.SimpleInvoiceStockInventory.objects.filter(id=stock_id,company=company_id).first()
            if not shop:
                response_data = {
                    'isSuccess': False,
                    'message': 'Stock item not found!'
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            shop.delete()
            return Response({
                'isSuccess': True,
                'message': 'Stock item deleted successfully!'
            }, status=status.HTTP_200_OK)

        except ProtectedError:
            return Response({
                'isSuccess': False,
                'message': 'This stock item cannot be deleted because it is referenced in other records (e.g., orders, products).'
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                'isSuccess': False,
                'message': 'Database constraint prevents deletion. The stock item may have linked records in other tables.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except simple_invoice_models.SimpleInvoiceStockInventory.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Stock item not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while deleting stock! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


####################################### end stock inventory views #######################################
####################################### measurement unit views #######################################

class SimpleInvoiceMeasurementUnitListView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the entire list of measurement units.
        """
        try:
            # Fetch all measurement units from the database
            stock_inventory = simple_invoice_models.SimpleInvoiceMeasurementUnit.objects.all()

            # Check if the inventory list is empty
            if not stock_inventory.exists():
                response_data = {
                    'isSuccess': False,
                    'message': 'No measurement units available.',
                }
                return Response(response_data, status=status.HTTP_200_OK)

            # Serialize the measurement units list
            stock_list_serializer = simple_invoice_serializers.SimpleInvoiceMeasurementUnitSerializer(stock_inventory, many=True)

            # Create the response data
            response_data = {
                'isSuccess': True,
                'message': 'Measurement units retrieved successfully!',
                'data': stock_list_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected errors
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving measurement units: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimpleInvoiceMeasurementUnitCreateView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles POST request to create a new measurement unit entry.
        """
        try:
            # Serialize the incoming data
            serializer = simple_invoice_serializers.SimpleInvoiceMeasurementUnitSerializer(data=request.data)

            if serializer.is_valid():
                # Save the new measurement unit entry
                serializer.save()
                response_data = {
                    'isSuccess': True,
                    'message': 'Measurement unit created successfully!',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            # If data is invalid, return validation errors
            response_data = {
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle unexpected errors
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while creating measurement unit: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimpleInvoiceMeasurementUnitDetailView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, unit_id):
        """
        Retrieve a measurement unit by ID.
        """
        try:
            # Retrieve the measurement unit by its ID
            unit = simple_invoice_models.SimpleInvoiceMeasurementUnit.objects.get(id=unit_id)
            serializer = simple_invoice_serializers.SimpleInvoiceMeasurementUnitSerializer(unit)

            response_data = {
                'isSuccess': True,
                'message': 'Measurement unit retrieved successfully!',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except simple_invoice_models.SimpleInvoiceMeasurementUnit.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Measurement unit not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving measurement unit: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimpleInvoiceMeasurementUnitUpdateView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, unit_id):
        """
        Fully update a measurement unit entry.
        """
        try:
            # Retrieve the measurement unit by its ID
            unit = simple_invoice_models.SimpleInvoiceMeasurementUnit.objects.get(id=unit_id)
            serializer = simple_invoice_serializers.SimpleInvoiceMeasurementUnitSerializer(unit, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Measurement unit updated successfully!',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except simple_invoice_models.SimpleInvoiceMeasurementUnit.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Measurement unit not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while updating measurement unit! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimpleInvoiceMeasurementUnitDeleteView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, unit_id):
        """
        Delete a measurement unit record. Prevent deletion if referenced in other tables.
        """
        try:
            # Retrieve the measurement unit by its ID
            unit = simple_invoice_models.SimpleInvoiceMeasurementUnit.objects.get(id=unit_id)
            unit.delete()
            return Response({
                'isSuccess': True,
                'message': 'Measurement unit deleted successfully!'
            }, status=status.HTTP_200_OK)

        except ProtectedError:
            return Response({
                'isSuccess': False,
                'message': 'This measurement unit cannot be deleted because it is referenced in other records (e.g., orders, products).'
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                'isSuccess': False,
                'message': 'Database constraint prevents deletion. The measurement unit may have linked records in other tables.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except simple_invoice_models.SimpleInvoiceMeasurementUnit.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Measurement unit not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while deleting measurement unit! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


####################################### end measurement unit views #######################################

####################################### bill views #######################################

class SimpleInvoiceBillListView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the entire list of invoice items (bills).
        """
        try:
            # Ensure the company ID exists
            company_id = request.user.company_details
            if not company_id:
                return Response({
                    'isSuccess': False,
                    'message': 'No company details found for the user.',
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch all invoices from the database
            invoice_list = simple_invoice_models.SimpleInvoiceGenerateBill.objects.filter(company=company_id)

            if not invoice_list:
                response_data = {
                    'isSuccess': False,
                    'message': 'No bills available.',
                    'data': []
                }
                return Response(response_data, status=status.HTTP_200_OK)

            # Serialize the invoice list
            invoice_list_serializer = simple_invoice_serializers.SimpleInvoiceGenerateBillSerializer(invoice_list, many=True)

            response_data = {
                'isSuccess': True,
                'message': 'Invoices retrieved successfully!',
                'data': invoice_list_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving invoice list: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimpleInvoiceBillCreateView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles POST request to create a new invoice bill entry.
        """
        try:
            # Serialize the incoming data
            serializer = simple_invoice_serializers.SimpleInvoiceGenerateBillSerializer(data=request.data, context={'request': request})

            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'isSuccess': True,
                    'message': 'Invoice bill created successfully!',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            response_data = {
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while creating invoice bill: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimpleInvoiceBillDetailView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, invoice_id):
        """
        Retrieve an invoice by ID.
        """
        try:
            company_id = request.user.company_details
            if not company_id:
                return Response({
                    'isSuccess': False,
                    'message': 'No company details found for the user.',
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the invoice entry
            invoice = simple_invoice_models.SimpleInvoiceGenerateBill.objects.filter(id=invoice_id, company=company_id).first()
            if not invoice:
                response_data = {
                    'isSuccess': False,
                    'message': 'Invoice not found!'
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            serializer = simple_invoice_serializers.SimpleInvoiceGenerateBillSerializer(invoice)
            response_data = {
                'isSuccess': True,
                'message': 'Invoice retrieved successfully!',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving invoice: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimpleInvoiceBillUpdateView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, invoice_id):
        """
        Fully update an invoice entry.
        """
        try:
            company_id = request.user.company_details
            if not company_id:
                return Response({
                    'isSuccess': False,
                    'message': 'No company details found for the user.',
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the invoice entry
            invoice = simple_invoice_models.SimpleInvoiceGenerateBill.objects.filter(id=invoice_id, company=company_id).first()
            if not invoice:
                response_data = {
                    'isSuccess': False,
                    'message': 'Invoice not found!'
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            serializer = simple_invoice_serializers.SimpleInvoiceGenerateBillSerializer(invoice, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Invoice updated successfully!',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while updating invoice! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimpleInvoiceBillDeleteView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, invoice_id):
        """
        Delete an invoice record. Prevent deletion if referenced in other tables.
        """
        try:
            company_id = request.user.company_details
            if not company_id:
                return Response({
                    'isSuccess': False,
                    'message': 'No company details found for the user.',
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the invoice entry
            invoice = simple_invoice_models.SimpleInvoiceGenerateBill.objects.filter(id=invoice_id, company=company_id).first()
            if not invoice:
                response_data = {
                    'isSuccess': False,
                    'message': 'Invoice not found!'
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            invoice.delete()
            return Response({
                'isSuccess': True,
                'message': 'Invoice deleted successfully!'
            }, status=status.HTTP_200_OK)

        except ProtectedError:
            return Response({
                'isSuccess': False,
                'message': 'This invoice cannot be deleted because it is referenced in other records (e.g., orders, products).'
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                'isSuccess': False,
                'message': 'Database constraint prevents deletion. The invoice may have linked records in other tables.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while deleting invoice! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



####################################### end bill views #######################################

