from rest_framework import serializers, viewsets
from .models import ItemCategory, Item, ItemStock, ItemIssue

# Serializers
class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class ItemStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemStock
        fields = '__all__'

class ItemIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemIssue
        fields = '__all__'

# ViewSets
class ItemCategoryViewSet(viewsets.ModelViewSet):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemStockViewSet(viewsets.ModelViewSet):
    queryset = ItemStock.objects.all()
    serializer_class = ItemStockSerializer

class ItemIssueViewSet(viewsets.ModelViewSet):
    queryset = ItemIssue.objects.all()
    serializer_class = ItemIssueSerializer
