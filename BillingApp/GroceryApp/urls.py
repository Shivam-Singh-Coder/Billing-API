from django.urls import path
from GroceryApp import views as grocery_views

urlpatterns = [
    # all shop crud operations
    path('grocery/shop/list/',grocery_views.GroceryShopListView.as_view(),name="grocery-shop-list"),
    path('grocery/shop/create/',grocery_views.GroceryShopCreateView.as_view(),name="grocery-shop-create"),
    path('grocery/shop/edit/<int:shop_id>/',grocery_views.GroceryShopUpdateView.as_view(),name="grocery-shop-edit"),
    path('grocery/shop/delete/<int:shop_id>/',grocery_views.GroceryShopDeleteView.as_view(),name="grocery-shop-delete"),
    # end shop crud operations

    # all product category crud operations
    path('grocery/category/list/',grocery_views.GroceryCategoryListView.as_view(),name="grocery-category-list"),
    path('grocery/category/create/',grocery_views.GroceryCategoryCreateView.as_view(),name="grocery-category-create"),
    path('grocery/category/edit/<int:category_id>/',grocery_views.GroceryCategoryUpdateView.as_view(),name="grocery-category-edit"),
    path('grocery/category/delete/<int:category_id>/',grocery_views.GroceryCategoryDeleteView.as_view(),name="grocery-category-delete"),
    # end product category crud operations

    # all stock inventory crud operations
    path('grocery/stock-inventory/list/',grocery_views.GroceryStockInventoryListView.as_view(),name="grocery-stock-list"),
    path('grocery/stock-inventory/create/',grocery_views.GroceryStockInventoryCreateView.as_view(),name="grocery-stock-create"),
    path('grocery/stock-inventory/edit/<int:stock_id>/',grocery_views.GroceryStockInventoryUpdateView.as_view(),name="grocery-stock-edit"),
    path('grocery/stock-inventory/delete/<int:stock_id>/',grocery_views.GroceryStockInventoryDeleteView.as_view(),name="grocery-stock-delete"),
    # end stock inventory crud operations
]
