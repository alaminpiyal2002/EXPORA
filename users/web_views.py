from datetime import datetime
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from expenses.models import Transaction
from expenses.models import Category, Transaction
from django.views.decorators.http import require_POST
from django.contrib import messages
import csv
from django.http import HttpResponse

def home(request):
    return render(request, "home.html", {"year": datetime.now().year})

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("/dashboard/")
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        try:
            user = User.objects.create_user(
                username=request.POST["username"],
                password=request.POST["password"],
                email=request.POST.get("email", ""),
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
            )
            login(request, user)
            return redirect("/dashboard/")
        except Exception:
            return render(request, "register.html", {"error": "User already exists"})
    return render(request, "register.html")

def logout_view(request):
    logout(request)
    return redirect("/")

@login_required
def dashboard(request):
    income = (
        Transaction.objects.filter(
            user=request.user,
            type=Transaction.INCOME,
            is_deleted=False,
        ).aggregate(total=Sum("amount"))["total"] or 0
    )

    expense = (
        Transaction.objects.filter(
            user=request.user,
            type=Transaction.EXPENSE,
            is_deleted=False,
        ).aggregate(total=Sum("amount"))["total"] or 0
    )

    recent_transactions = Transaction.objects.filter(
        user=request.user,
        is_deleted=False
    ).order_by("-date")[:5]

    context = {
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "recent_transactions": recent_transactions,
    }
    return render(request, "dashboard.html", context)

@login_required
def transactions_page(request):
    categories = Category.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(
        user=request.user, is_deleted=False
    ).order_by("-date")

    # Add Category
    if request.method == "POST" and "add_category" in request.POST:
        Category.objects.create(
            user=request.user,
            name=request.POST.get("category_name")
        )
        return redirect("/transactions/")

    # Add Transaction
    if request.method == "POST" and "add_transaction" in request.POST:
        Transaction.objects.create(
            user=request.user,
            category_id=request.POST.get("category"),
            type=request.POST.get("type"),
            amount=request.POST.get("amount"),
            date=request.POST.get("date"),
            description=request.POST.get("description"),
        )
        return redirect("/transactions/")

    context = {
        "categories": categories,
        "transactions": transactions,
    }
    return render(request, "transactions.html", context)
@login_required
@require_POST
def delete_transaction(request, pk):
    Transaction.objects.filter(
        id=pk, user=request.user
    ).update(is_deleted=True)
    return redirect("/transactions/")


@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("/profile/")

    return render(request, "profile.html")

@login_required
def export_transactions_csv(request):
    transactions = Transaction.objects.filter(
        user=request.user,
        is_deleted=False
    ).order_by("-date")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Type", "Category", "Amount", "Description"])

    for t in transactions:
        writer.writerow([t.date, t.type, t.category.name, t.amount, t.description])

    return response