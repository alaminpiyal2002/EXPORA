from rest_framework import serializers
from .models import Category, Transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

#transaction amount and category wise organized
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "category",
            "amount",
            "type",
            "description",
            "date",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate_category(self, value):
        request = self.context.get("request")
        if value.user != request.user:
            raise serializers.ValidationError("Invalid category.")
        return value        