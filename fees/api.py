from rest_framework import serializers, viewsets
from .models import (
    FeeCategory, 
    FeeStructure, 
    FeeItem, 
    PaymentMethod, 
    FeePayment, 
    FeeDiscount
)

# Serializers
class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = '__all__'

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = '__all__'

# ViewSets
class FeeCategoryViewSet(viewsets.ModelViewSet):
    queryset = FeeCategory.objects.all()
    serializer_class = FeeCategorySerializer

class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer

class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer 