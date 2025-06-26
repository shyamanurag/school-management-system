from rest_framework import serializers, viewsets
from .models import (
    InventoryCategory,
    Supplier,
    Brand,
    InventoryItem,
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceipt,
    StockTransaction,
    StockIssue,
    InventoryAudit,
    InventoryReport
)

# Serializers
class InventoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'

class GoodsReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceipt
        fields = '__all__'

class StockTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransaction
        fields = '__all__'

class StockIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockIssue
        fields = '__all__'

class InventoryAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAudit
        fields = '__all__'

class InventoryReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryReport
        fields = '__all__'

# ViewSets
class InventoryCategoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryCategory.objects.all()
    serializer_class = InventoryCategorySerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer

class GoodsReceiptViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceipt.objects.all()
    serializer_class = GoodsReceiptSerializer

class StockTransactionViewSet(viewsets.ModelViewSet):
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer

class StockIssueViewSet(viewsets.ModelViewSet):
    queryset = StockIssue.objects.all()
    serializer_class = StockIssueSerializer

class InventoryAuditViewSet(viewsets.ModelViewSet):
    queryset = InventoryAudit.objects.all()
    serializer_class = InventoryAuditSerializer

class InventoryReportViewSet(viewsets.ModelViewSet):
    queryset = InventoryReport.objects.all()
    serializer_class = InventoryReportSerializer 