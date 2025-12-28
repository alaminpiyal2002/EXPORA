from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Category
from .serializers import CategorySerializer
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import date
import calendar
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
import csv
from django.http import HttpResponse

class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDeleteView(generics.DestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


from .models import Transaction
from .serializers import TransactionSerializer



class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
            is_deleted=False
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
            is_deleted=False
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class MonthlySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = int(request.query_params.get("month"))
        year = int(request.query_params.get("year"))

        last_day = calendar.monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        qs = Transaction.objects.filter(
            user=request.user,
            is_deleted=False,
            date__range=(start_date, end_date),
        )

        income = qs.filter(type=Transaction.INCOME).aggregate(total=Sum("amount"))["total"] or 0
        expense = qs.filter(type=Transaction.EXPENSE).aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "month": month,
            "year": year,
            "income": income,
            "expense": expense,
            "balance": income - expense,
        })

#this is used for the calculating balance and do summary of calculation
class CategorySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = int(request.query_params.get("month"))
        year = int(request.query_params.get("year"))

        last_day = calendar.monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        qs = Transaction.objects.filter(
            user=request.user,
            is_deleted=False,
            type=Transaction.EXPENSE,
            date__range=(start_date, end_date),
        )

        data = (
            qs.values("category__name")
              .annotate(total=Sum("amount"))
              .order_by("-total")
        )

        return Response({
            "month": month,
            "year": year,
            "categories": list(data),
        })


class TransactionCSVExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(
            user=request.user,
            is_deleted=False
        )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

        writer = csv.writer(response)
        writer.writerow(["Date", "Type", "Category", "Amount", "Description"])

        for t in transactions:
            writer.writerow([
                t.date,
                t.type,
                t.category.name,
                t.amount,
                t.description,
            ])

        return response
