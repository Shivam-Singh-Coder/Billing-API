from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from GroceryApp import models as grocery_models
from GroceryApp import serializers as grocery_serializers
# from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from AuthorizationApp.custom_token_error import CustomTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from uuid import UUID

####################################### shop views #######################################

class GroceryShopListView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all shop lists.
        """
        try:
            # Get the list of shops from the database
            all_shops = grocery_models.GroceryShopDetails.objects.all()
            #check if the list is empty
            if not all_shops.exists():
                response_data = {
                    'isSuccess':False,
                    "message": "No shops available till yet!",
                    "data":[]
                }
                return Response(response_data, status=status.HTTP_200_OK)
            # Serialize the list of shops
            shop_list_serializer = grocery_serializers.GroceryShopListSerializer(all_shops, many=True)
            #create response data
            response_data = {
                'isSuccess':True,
                'message':'Shops list retrieved successfully!',
                'data':shop_list_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            #create response data
            response_data = {
                'isSuccess':False,
                'message':f'Error occurred while retrieving shops list: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GroceryShopCreateView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handles POST request to create a new shop entry."""
        try:
            serializer = grocery_serializers.GroceryShopEntrySerializer(data=request.data)
            if serializer.is_valid():
                # Create a new shop entry
                serializer.save()
                response_data = {
                    'isSuccess':True,
                    'message':'Shop created successfully!',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            response_data = {
                'isSuccess':False,
                'message':'Invalid data provided!',
                'errors':serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            #create response data
            response_data = {
                'isSuccess':False,
                'message':f'Error occurred while creating shop entry: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroceryShopUpdateView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, shop_id):
        """Handles GET request to retrieve a shop entry by ID."""
        try:
            shop = grocery_models.GroceryShopDetails.objects.get(id=shop_id)
            serializer = grocery_serializers.GroceryShopEntrySerializer(shop)
            response_data = {
                'isSuccess': True,
                'message': 'Shop retrieved successfully!',
                'data': serializer.data
                }
            return Response(response_data, status=status.HTTP_200_OK)
        except grocery_models.GroceryShopDetails.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Shop not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving shop: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, shop_id):
        """
        Fully update a shop record.
        """
        try:
            shop = get_object_or_404(grocery_models.GroceryShopDetails, id=shop_id)
            serializer = grocery_serializers.GroceryShopEntrySerializer(shop, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Shop updated successfully!',
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
                'message': f'Error occurred while updating shop! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, shop_id):
        """
        Partially update a shop record.
        """
        try:
            shop = get_object_or_404(grocery_models.GroceryShopDetails, id=shop_id)
            serializer = grocery_serializers.GroceryShopEntrySerializer(shop, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Shop updated successfully!',
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
                'message': f'Error occurred while updating shop! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GroceryShopDeleteView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, shop_id):
        """
        Delete a shop record. Prevent deletion if referenced in other tables.
        """
        try:
            shop = get_object_or_404(grocery_models.GroceryShopDetails, id=shop_id)
            shop.delete()
            return Response({
                'isSuccess': True,
                'message': 'Shop deleted successfully!'
            }, status=status.HTTP_200_OK)

        except ProtectedError:
            return Response({
                'isSuccess': False,
                'message': 'This shop cannot be deleted because it is referenced in other records (e.g., orders, products).'
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                'isSuccess': False,
                'message': 'Database constraint prevents deletion. The shop may have linked records in other tables.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while deleting shop! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

####################################### end shop views #######################################

############################### category views ##########################################
class GroceryCategoryListView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all product categories.
        """
        try:
            all_categories = grocery_models.GroceryCategory.objects.all()
            if not all_categories.exists():
                response_data = {
                    'isSuccess': False,
                    'message': 'No categories available yet!',
                    'data': []
                }
                return Response(response_data, status=status.HTTP_200_OK)

            category_list_serializer = grocery_serializers.GroceryCategoryListSerializer(all_categories, many=True)
            response_data = {
                'isSuccess': True,
                'message': 'Categories retrieved successfully!',
                'data': category_list_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving categories: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GroceryCategoryCreateView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handles POST request to create a new category entry."""
        try:
            serializer = grocery_serializers.GroceryCategoryEntrySerializer(data=request.data)
            if serializer.is_valid():
                # Create a new category entry
                serializer.save()
                response_data = {
                    'isSuccess': True,
                    'message': 'Category created successfully!',
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
            #create response data
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while creating category entry: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroceryCategoryUpdateView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request, category_id):
        """Handles GET request to retrieve a specific category entry by ID."""
        try:
            category = grocery_models.GroceryCategory.objects.get(id=category_id)
            serializer = grocery_serializers.GroceryCategoryEntrySerializer(category)
            response_data = {
                'isSuccess': True,
                'data': serializer.data
                }
            return Response(response_data, status=status.HTTP_200_OK)
        except grocery_models.GroceryCategory.DoesNotExist:
            response_data = {
                'isSuccess': False,
                'message': 'Category not found!'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving category: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, category_id):
        """
        Fully update a category record.
        """
        try:
            category = get_object_or_404(grocery_models.GroceryCategory, id=category_id)
            serializer = grocery_serializers.GroceryCategoryEntrySerializer(category, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Category updated successfully!',
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
                'message': f'Error occurred while updating category! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, category_id):
        """
        Partially update a category record.
        """
        try:
            category = get_object_or_404(grocery_models.GroceryCategory, id=category_id)
            serializer = grocery_serializers.GroceryCategoryEntrySerializer(category, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Category updated successfully!',
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
                'message': f'Error occurred while updating category! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GroceryCategoryDeleteView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, category_id):
        """
        Delete a category record. Prevent deletion if referenced in other tables.
        """
        try:
            category = get_object_or_404(grocery_models.GroceryCategory, id=category_id)
            category.delete()
            return Response({
                'isSuccess': True,
                'message': 'Category deleted successfully!'
            }, status=status.HTTP_200_OK)

        except ProtectedError:
            return Response({
                'isSuccess': False,
                'message': 'This category cannot be deleted because it is referenced in other records (e.g., stock inventory).'
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                'isSuccess': False,
                'message': 'Database constraint prevents deletion. The category may have linked records in other tables.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while deleting category! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
################################ end category views ##########################################

############################### stock inventory views ##########################################
class GroceryStockInventoryListView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all stock inventory items.
        """
        try:
            all_stock_items = grocery_models.GroceryStockInventory.objects.all()
            if not all_stock_items.exists():
                response_data = {
                    'isSuccess': False,
                    'message': 'No stock inventory items available yet!',
                    'data': []
                }
                return Response(response_data, status=status.HTTP_200_OK)

            stock_list_serializer = grocery_serializers.GroceryStockInventoryListSerializer(all_stock_items, many=True)
            response_data = {
                'isSuccess': True,
                'message': 'Stock inventory items retrieved successfully!',
                'data': stock_list_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while retrieving stock inventory items: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroceryStockInventoryCreateView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handles POST request to create a new stock inventory entry."""
        try:
            serializer = grocery_serializers.GroceryStockInventoryEntrySerializer(data=request.data)
            if serializer.is_valid():
                # Create a new stock inventory entry
                serializer.save()
                response_data = {
                    'isSuccess': True,
                    'message': 'Stock inventory item created successfully!',
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
            #create response data
            response_data = {
                'isSuccess': False,
                'message': f'Error occurred while creating stock inventory entry: {str(e)}'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroceryStockInventoryUpdateView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def put(self, request, stock_id):
        """
        Fully update a stock inventory record.
        """
        try:
            stock_item = get_object_or_404(grocery_models.GroceryStockInventory, id=stock_id)
            serializer = grocery_serializers.GroceryStockInventoryEntrySerializer(stock_item, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Stock inventory item updated successfully!',
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
                'message': f'Error occurred while updating stock inventory item! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, stock_id):
        """
        Partially update a stock inventory record.
        """
        try:
            stock_item = get_object_or_404(grocery_models.GroceryStockInventory, id=stock_id)
            serializer = grocery_serializers.GroceryStockInventoryEntrySerializer(stock_item, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'isSuccess': True,
                    'message': 'Stock inventory item updated successfully!',
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
                'message': f'Error occurred while updating stock inventory item! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroceryStockInventoryDeleteView(APIView):
    # authentication_classes = [JWTAuthentication, CustomTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, stock_id):
        """
        Delete a stock inventory record. Prevent deletion if referenced in other tables.
        """
        try:
            stock_item = get_object_or_404(grocery_models.GroceryStockInventory, id=stock_id)
            stock_item.delete()
            return Response({
                'isSuccess': True,
                'message': 'Stock inventory item deleted successfully!'
            }, status=status.HTTP_200_OK)

        except ProtectedError:
            return Response({
                'isSuccess': False,
                'message': 'This stock inventory item cannot be deleted because it is referenced in other records.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                'isSuccess': False,
                'message': 'Database constraint prevents deletion. The stock inventory item may have linked records in other tables.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'isSuccess': False,
                'message': f'Error occurred while deleting stock inventory item! Errors: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
################################ end stock inventory views ##########################################


    