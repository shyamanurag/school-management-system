from rest_framework import serializers, viewsets
from .models import (
    HostelBlock,
    HostelRoom,
    HostelAdmission,
    HostelResident,
    MessMenu,
    MessAttendance,
    HostelVisitor,
    HostelDisciplinary,
    HostelFeedback,
    HostelReport
)

# Serializers
class HostelBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelBlock
        fields = '__all__'

class HostelRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelRoom
        fields = '__all__'

class HostelAdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAdmission
        fields = '__all__'

class HostelResidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelResident
        fields = '__all__'

class MessMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessMenu
        fields = '__all__'

class MessAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessAttendance
        fields = '__all__'

class HostelVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelVisitor
        fields = '__all__'

class HostelFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelFeedback
        fields = '__all__'

# ViewSets
class HostelBlockViewSet(viewsets.ModelViewSet):
    queryset = HostelBlock.objects.all()
    serializer_class = HostelBlockSerializer

class HostelRoomViewSet(viewsets.ModelViewSet):
    queryset = HostelRoom.objects.all()
    serializer_class = HostelRoomSerializer

class HostelAdmissionViewSet(viewsets.ModelViewSet):
    queryset = HostelAdmission.objects.all()
    serializer_class = HostelAdmissionSerializer

class HostelResidentViewSet(viewsets.ModelViewSet):
    queryset = HostelResident.objects.all()
    serializer_class = HostelResidentSerializer

class MessMenuViewSet(viewsets.ModelViewSet):
    queryset = MessMenu.objects.all()
    serializer_class = MessMenuSerializer

class MessAttendanceViewSet(viewsets.ModelViewSet):
    queryset = MessAttendance.objects.all()
    serializer_class = MessAttendanceSerializer

class HostelVisitorViewSet(viewsets.ModelViewSet):
    queryset = HostelVisitor.objects.all()
    serializer_class = HostelVisitorSerializer

class HostelFeedbackViewSet(viewsets.ModelViewSet):
    queryset = HostelFeedback.objects.all()
    serializer_class = HostelFeedbackSerializer 