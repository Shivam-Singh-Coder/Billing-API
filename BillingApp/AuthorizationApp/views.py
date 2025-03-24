from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from AuthorizationApp import models as auth_models
from AuthorizationApp import serializers as auth_serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from AuthorizationApp.custom_token_error import CustomTokenAuthentication
from rest_framework.generics import get_object_or_404
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import AuthenticationFailed

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        pass

class CustomLoginView(APIView):
    def post(self, request):
        """
        Custom login endpoint that returns JWT tokens along with user data.
        """
        try:
            serializer = auth_serializers.CustomLoginSerializer(data=request.data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)

            # If validation fails, return errors
            return Response({"isSuccess": False, "message": "Login failed!", "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"isSuccess": False, "message": f"Error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

####################################### shop views #######################################

class CompanyListView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all company details (or software types) from the database.
        """
        try:
            # Get the list of CompanyIDs from the database
            all_companies = auth_models.CompanyID.objects.all()

            # If the list is empty, return a message
            if not all_companies:
                response_data = {
                    'isSuccess': False,
                    "message": "No companies available yet!",
                }
                return Response(response_data, status=status.HTTP_200_OK)

            # Serialize the list of companies
            company_serializer = auth_serializers.CompanySerializer(all_companies, many=True)

            # Create the response data with the serialized data
            response_data = {
                'isSuccess': True,
                'message': 'Companies list retrieved successfully!',
                'data': company_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for better debugging (use logging in production)
            # Example: logger.error(str(e))
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving companies list: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompanyCreateView(APIView):
    # Uncomment these lines if authentication and permissions are required
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handles POST request to create a new Company entry."""
        try:
            # Initialize the serializer with request data
            serializer = auth_serializers.CompanySerializer(data=request.data)

            if serializer.is_valid():
                # Save the new company entry
                serializer.save()
                response_data = {
                    'isSuccess': True,
                    'message': 'Company created successfully!',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            # If serializer is not valid, return errors
            response_data = {
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Catch any unexpected errors and return a 500 internal server error
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while creating company: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompanyDetailView(APIView):
    # Uncomment these lines if authentication and permissions are required
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        """Handles GET request to retrieve a Company entry by ID."""
        try:
            company = auth_models.CompanyID.objects.get(pk=company_id)
            serializer = auth_serializers.CompanySerializer(company)  # Assuming CompanyIDSerializer here
            response_data = {
                'isSuccess': True,
                'message': 'Company retrieved successfully!',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except auth_models.CompanyID.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Company not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving Company: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompanyUpdateView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, company_id):
        """Fully update a Company record."""
        try:
            company = auth_models.CompanyID.objects.get(pk=company_id)
            serializer = auth_serializers.CompanySerializer(company, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Company updated successfully!',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except auth_models.CompanyID.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Company not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while updating Company! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyDeleteView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, company_id):
        """Delete a Company record. Prevent deletion if referenced in other tables."""
        try:
            company = auth_models.CompanyID.objects.get(pk=company_id)
            company.delete()
            return Response({
                'isSuccess': True,
                'message': 'Company deleted successfully!'
            }, status=status.HTTP_200_OK)

        except auth_models.CompanyID.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Company not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except ProtectedError:
            return Response({
                'isSuccess': False,
                'message': 'This Company cannot be deleted because it is referenced in other records (e.g., orders, products).'
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                'isSuccess': False,
                'message': 'Database constraint prevents deletion. The Company may have linked records in other tables.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while deleting Company! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

####################################### end shop views #######################################
####################################### shop views #######################################

class SoftwareTypeListView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all software type lists.
        """
        try:
            # Get the list of SoftwareTypes from the database
            all_software_types = auth_models.SoftwareType.objects.all()

            # Check if the list is empty
            if not all_software_types.exists():
                response_data = {
                    'isSuccess': False,
                    "message": "No software types available yet!",
                }
                return Response(response_data, status=status.HTTP_200_OK)

            # Serialize the list of SoftwareTypes
            software_type_serializer = auth_serializers.SoftwareTypeSerializer(all_software_types, many=True)

            # Create response data
            response_data = {
                'isSuccess': True,
                'message': 'Software types list retrieved successfully!',
                'data': software_type_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Create response data for errors
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving software types list: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SoftwareTypeCreateView(APIView):
    # Uncomment these lines if authentication and permissions are required
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handles POST request to create a new SoftwareType entry."""
        try:
            # Serializer for creating a new software type
            serializer = auth_serializers.SoftwareTypeSerializer(data=request.data)

            if serializer.is_valid():
                # Save the new software type entry
                serializer.save()
                response_data = {
                    'isSuccess': True,
                    'message': 'Software Type created successfully!',
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
                'message': f'Error occurred while creating Software Type: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SoftwareTypeDetailView(APIView):
    # Uncomment these lines if authentication and permissions are required
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, software_id):
        """Handles GET request to retrieve a SoftwareType entry by ID."""
        try:
            software_type = auth_models.SoftwareType.objects.get(pk=software_id)
            serializer = auth_serializers.SoftwareTypeSerializer(software_type)
            response_data = {
                'isSuccess': True,
                'message': 'Software Type retrieved successfully!',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except auth_models.SoftwareType.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Software Type not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving Software Type: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SoftwareTypeUpdateView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, software_id):
        """Fully update a SoftwareType record."""
        try:
            software_type = auth_models.SoftwareType.objects.get(pk=software_id)
            serializer = auth_serializers.SoftwareTypeSerializer(software_type, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Software Type updated successfully!',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'isSuccess': False,
                'message': 'Invalid data provided!',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except auth_models.SoftwareType.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Software Type not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while updating Software Type! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

class SoftwareTypeDeleteView(APIView):
    authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, software_id):
        """Delete a SoftwareType record. Prevent deletion if referenced in other tables."""
        try:
            software_type = auth_models.SoftwareType.objects.get(pk=software_id)
            software_type.delete()
            return Response({
                'isSuccess': True,
                'message': 'Software Type deleted successfully!'
            }, status=status.HTTP_200_OK)

        except auth_models.SoftwareType.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Software Type not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except ProtectedError:
            return Response({
                'isSuccess': False,
                'message': 'This Software Type cannot be deleted because it is referenced in other records (e.g., orders, products).'
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                'isSuccess': False,
                'message': 'Database constraint prevents deletion. The Software Type may have linked records in other tables.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while deleting Software Type! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

####################################### end shop views #######################################