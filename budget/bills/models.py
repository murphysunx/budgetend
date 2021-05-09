from django.db import models

# Create your models here.


class Bill(models.Model):
    payer = models.CharField(max_length=20)
    payee = models.CharField(max_length=20)
    venue = models.CharField(max_length=50)
    effectStartDate = models.DateField()
    effectEndDate = models.DateField(null=True)
    payDate = models.DateField(null=True)
    note = models.CharField(max_length=50, null=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2)


class Category(models.Model):
    category = models.CharField(max_length=20, unique=True)


class BillItem(models.Model):
    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    qty = models.IntegerField(null=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    note = models.CharField(max_length=50, null=True)
    categories = models.ManyToManyField(
        Category, through='Catelog', through_fields=('item', 'category'))
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)


class Catelog(models.Model):
    item = models.ForeignKey(BillItem, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
