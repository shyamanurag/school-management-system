from rest_framework import serializers, viewsets
from .models import Hostel, RoomType, HostelRoom, HostelAssignment

# Serializers
class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'

class HostelRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelRoom
        fields = '__all__'

class HostelAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAssignment
        fields = '__all__'

# ViewSets
class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer

class RoomTypeViewSet(viewsets.ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer

class HostelRoomViewSet(viewsets.ModelViewSet):
    queryset = HostelRoom.objects.all()
    serializer_class = HostelRoomSerializer

class HostelAssignmentViewSet(viewsets.ModelViewSet):
    queryset = HostelAssignment.objects.all()
    serializer_class = HostelAssignmentSerializer
