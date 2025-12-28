from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDeleteView,
    TransactionListCreateView,
    TransactionUpdateDeleteView,
    MonthlySummaryView,
    CategorySummaryView,
    TransactionCSVExportView,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDeleteView.as_view(), name="category-delete"),
    #urls for transactions
    path("transactions/", TransactionListCreateView.as_view()),
    path("transactions/<int:pk>/", TransactionUpdateDeleteView.as_view()),
    #urls for calculation and summary
        path("summary/monthly/", MonthlySummaryView.as_view()),
    path("summary/category/", CategorySummaryView.as_view()),
     path("transactions/export/", TransactionCSVExportView.as_view()),
]
