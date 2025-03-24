from django.urls import path
from SimpleInvoice import views as simple_invoice_views

urlpatterns = [
    # all simple-invoice stock inventory crud operations
    path('simple-invoice/stock-inventory/list/',simple_invoice_views.SimpleInvoiceStockListView.as_view(),name="simple-invoice-stock-list"),
    path('simple-invoice/stock-inventory/create/',simple_invoice_views.SimpleInvoiceStockCreateView.as_view(),name="simple-invoice-stock-create"),
    path('simple-invoice/stock-inventory/edit/<int:stock_id>/',simple_invoice_views.SimpleInvoiceStockUpdateView.as_view(),name="simple-invoice-stock-edit"),
    path('simple-invoice/stock-inventory/detail/<int:stock_id>/',simple_invoice_views.SimpleInvoiceStockDetailView.as_view(),name="simple-invoice-stock-detail"),
    path('simple-invoice/stock-inventory/delete/<int:stock_id>/',simple_invoice_views.SimpleInvoiceStockDeleteView.as_view(),name="simple-invoice-stock-delete"),
    # end simple-invoice stock inventory crud operations

    # all simple-invoice stock inventory crud operations
    path('simple-invoice/measurement-unit/list/',simple_invoice_views.SimpleInvoiceMeasurementUnitListView.as_view(),name="simple-invoice-measurement-unit-list"),
    path('simple-invoice/measurement-unit/create/',simple_invoice_views.SimpleInvoiceMeasurementUnitCreateView.as_view(),name="simple-invoice-measurement-unit-create"),
    path('simple-invoice/measurement-unit/edit/<int:unit_id>/',simple_invoice_views.SimpleInvoiceMeasurementUnitUpdateView.as_view(),name="simple-invoice-measurement-unit-edit"),
    path('simple-invoice/measurement-unit/detail/<int:unit_id>/',simple_invoice_views.SimpleInvoiceMeasurementUnitDetailView.as_view(),name="simple-invoice-measurement-unit-detail"),
    path('simple-invoice/measurement-unit/delete/<int:unit_id>/',simple_invoice_views.SimpleInvoiceMeasurementUnitDeleteView.as_view(),name="simple-invoice-measurement-unit-delete"),
    # end simple-invoice stock inventory crud operations

    # all simple-invoice stock inventory crud operations
    path('simple-invoice/bill/list/',simple_invoice_views.SimpleInvoiceBillListView.as_view(),name="simple-invoice-bill-list"),
    path('simple-invoice/bill/create/',simple_invoice_views.SimpleInvoiceBillCreateView.as_view(),name="simple-invoice-bill-create"),
    path('simple-invoice/bill/edit/<int:invoice_id>/',simple_invoice_views.SimpleInvoiceBillUpdateView.as_view(),name="simple-invoice-bill-edit"),
    path('simple-invoice/bill/detail/<int:invoice_id>/',simple_invoice_views.SimpleInvoiceBillDetailView.as_view(),name="simple-invoice-bill-detail"),
    path('simple-invoice/bill/delete/<int:invoice_id>/',simple_invoice_views.SimpleInvoiceBillDeleteView.as_view(),name="simple-invoice-bill-delete"),
    # end simple-invoice stock inventory crud operations
]
