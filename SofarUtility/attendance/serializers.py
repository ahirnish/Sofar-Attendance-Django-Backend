from rest_framework import serializers
from .models import Event, Person, Attendance

class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for Event model
    """
    class Meta:
        model = Event
        fields = ("date", "location")

class PersonSerializer(serializers.ModelSerializer):
    """
    Serializer for Person model
    """
    class Meta:
        model = Person
        fields = ("first_name", "last_name", "email")

class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model
    """
    event = EventSerializer()
    person = PersonSerializer()
    
    class Meta:
        model = Attendance
        depth = 2
        fields = ("event", "person", "attended")

    # gets called only when is_valid() is called. Only then 'event' and 'person' converted to id. This is done on initial data, before validation.
    def to_internal_value(self, data):
         self.fields['event'] = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
         self.fields['person'] = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())
         return super(AttendanceSerializer, self).to_internal_value(data)

    # to represent back the actual object which was replaced with thier id by to_internal_value() func
    def to_representation(self, data):
        self.fields['event'] = EventSerializer()
        self.fields['person'] = PersonSerializer()
        return super(AttendanceSerializer, self).to_representation(data)
