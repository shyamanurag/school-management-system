from rest_framework import serializers, viewsets
from .models import Route, Vehicle, TransportAssignment

# Serializers
class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class TransportAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportAssignment
        fields = '__all__'

# ViewSets
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class TransportAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TransportAssignment.objects.all()
    serializer_class = TransportAssignmentSerializer
