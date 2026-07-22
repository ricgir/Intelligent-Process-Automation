from django.urls import path, include
from rest_framework.routers import DefaultRouter
from invoices.views import InvoiceViewSet, index_view, results_view

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', index_view, name='index'),
    path('results/', results_view, name='results'),
]
