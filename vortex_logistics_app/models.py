# models.py
from django.db import models


class Delivery(models.Model):
    recipient_name = models.CharField(max_length=100)
    recipient_mobile_number = models.CharField(max_length=15)
    pickup = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50, choices=[
        ('Documents', 'Documents'),
        ('Clothing', 'Clothing'),
        ('Electronics', 'Electronics'),
        ('Food', 'Food'),
        ('Furniture', 'Furniture'),
        ('Gifts', 'Gifts'),
        ('Health', 'Health & Beauty Products'),
        ('Office Supplies', 'Office Supplies'),
        ('Industrial Parts', 'Industrial & Automotive Parts'),
        ('Medical Supplies', 'Medical Supplies'),
    ])
    distance = models.FloatField()
    weight = models.CharField(max_length=50)
    delivery_charge = models.FloatField()
    status = models.CharField(max_length=25, choices=[
        ('Ordered', 'Ordered'),
        ('Picked', 'Picked'),
        ('In-Transist', 'In-Transist'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ], null=True, blank=True
    )

    def __str__(self):
        return (
            f"{self.recipient_name} "
            f"Distance: {self.distance} km, "
            f"Weight: {self.weight}, "
            f"Charge: ₹{self.delivery_charge}"
        )


class DeliveryCharge(models.Model):
    distance = models.FloatField()
    weight = models.CharField(max_length=50)
    delivery_charge = models.FloatField()

    def __str__(self):
        return (
            f"Distance: {self.distance} km,"
            f"Weight: {self.weight},"
            f"Charge: ₹{self.delivery_charge}"
        )


class username(models.Model):
    name = models.CharField(max_length=30)
