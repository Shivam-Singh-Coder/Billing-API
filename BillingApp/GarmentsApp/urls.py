from django.urls import path
from GarmentsApp import views as garments_views

urlpatterns = [
    # all shop crud operations
    path('garments/shop/list/',garments_views.GarmentsShopListView.as_view(),name="garments-shop-list"),
    path('garments/shop/create/',garments_views.GarmentsShopCreateView.as_view(),name="garments-shop-create"),
    path('garments/shop/edit/<int:shop_id>/',garments_views.GarmentsShopUpdateView.as_view(),name="garments-shop-edit"),
    path('garments/shop/delete/<int:shop_id>/',garments_views.GarmentsShopDeleteView.as_view(),name="garments-shop-delete"),
    # end shop crud operations

    # all product category crud operations
    path('garments/category/list/',garments_views.GarmentsCategoryListView.as_view(),name="garments-category-list"),
    path('garments/category/create/',garments_views.GarmentsCategoryCreateView.as_view(),name="garments-category-create"),
    path('garments/category/edit/<int:category_id>/',garments_views.GarmentsCategoryUpdateView.as_view(),name="garments-category-edit"),
    path('garments/category/delete/<int:category_id>/',garments_views.GarmentsCategoryDeleteView.as_view(),name="garments-category-delete"),
    # end product category crud operations

    # all stock inventory crud operations
    path('garments/stock-inventory/list/',garments_views.GarmentsStockInventoryListView.as_view(),name="garments-stock-list"),
    path('garments/stock-inventory/create/',garments_views.GarmentsStockInventoryCreateView.as_view(),name="garments-stock-create"),
    path('garments/stock-inventory/edit/<int:stock_id>/',garments_views.GarmentsStockInventoryUpdateView.as_view(),name="garments-stock-edit"),
    path('garments/stock-inventory/delete/<int:stock_id>/',garments_views.GarmentsStockInventoryDeleteView.as_view(),name="garments-stock-delete"),
    # end stock inventory crud operations
]
