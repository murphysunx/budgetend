from rest_framework import serializers
from .models import Bill, BillItem, Category, Catelog


class BillSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    payer = serializers.CharField(required=True, max_length=20)
    payee = serializers.CharField(required=True, max_length=20)
    venue = serializers.CharField(required=True, max_length=50)
    effectStartDate = serializers.DateField(required=True)
    effectEndDate = serializers.DateField()
    payDate = serializers.DateField()
    note = serializers.CharField(required=False, max_length=50)
    cost = serializers.DecimalField(
        max_digits=7, decimal_places=2, required=True)

    def create(self, validated_data):
        return Bill.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.payer = validated_data.get('payer', instance.payer)
        instance.payee = validated_data.get('payee', instance.payee)
        instance.veune = validated_data.get('veune', instance.veune)
        instance.effectStartDate = validated_data.get(
            'effectStartDate', instance.effectStartDate)
        instance.effectEndDate = validated_data.get(
            'effectEndDate', instance.effectEndDate)
        instance.payDate = validated_data.get(
            'payDate', instance.payDate)
        instance.note = validated_data.get('note', instance.note)
        instance.cost = validated_data.get('cost', instance.cost)
        instance.save()
        return instance


class BillItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, max_length=20)
    price = serializers.DecimalField(
        max_digits=7, decimal_places=2, required=False)
    qty = serializers.IntegerField(required=False)
    cost = serializers.DecimalField(
        max_digits=7, decimal_places=2, required=True)
    note = serializers.CharField(max_length=20, required=False)
    # categories = serial
    bill_id = serializers.CharField(max_length=20, required=True)

    def create(self, validated_data):
        return BillItem.objects.create(**validated_data)

    def addBillId(self, validated_data, billId):
        return validated_data


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    category = serializers.CharField(max_length=20, required=True)

    def create(self, validated_data):
        return Category.objects.create(**validated_data)


class CatelogSerializer(serializers.Serializer):
    item_id = serializers.CharField(max_length=20, required=True)
    category_id = serializers.CharField(max_length=20, required=True)

    def create(self, validated_data):
        return Catelog.objects.create(**validated_data)
