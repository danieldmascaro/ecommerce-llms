from django.urls import path

from .views import SaleEventDetailView, SaleEventListView, SalesSummaryView

urlpatterns = [
    path("summary/", SalesSummaryView.as_view(), name="sales-summary"),
    path("events/", SaleEventListView.as_view(), name="sales-events"),
    path("events/<int:pk>/", SaleEventDetailView.as_view(), name="sales-event-detail"),
]

