from rest_framework import serializers, viewsets
from .models import (
    TransportVendor,
    Vehicle,
    TransportRoute,
    StudentTransport
)

# Serializers
class TransportVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportVendor
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class TransportRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportRoute
        fields = '__all__'

class StudentTransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTransport
        fields = '__all__'

# ViewSets
class TransportVendorViewSet(viewsets.ModelViewSet):
    queryset = TransportVendor.objects.all()
    serializer_class = TransportVendorSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class TransportRouteViewSet(viewsets.ModelViewSet):
    queryset = TransportRoute.objects.all()
    serializer_class = TransportRouteSerializer

class StudentTransportViewSet(viewsets.ModelViewSet):
    queryset = StudentTransport.objects.all()
    serializer_class = StudentTransportSerializer 