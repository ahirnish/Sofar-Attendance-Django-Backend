from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework import permissions
from .models import Event, Person, Attendance
from .serializers import EventSerializer, PersonSerializer, AttendanceSerializer
from rest_framework.response import Response
from rest_framework.views import status
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import RedirectView
import datetime, json

def errorMessageFromSerializer(serializer):
    error_msg = ""
    for val in serializer.errors.values(): # keys of 'error' dict are model field names ( {'model_field_name': 'associated error'} ).
        if isinstance(val,list): # there could be multiple errors associated with a single model field.
            for detail in val:
                error_msg = error_msg + detail + " "
        else:
            error_msg = error_msg + str(val) + " "
    error_msg = error_msg[:-1] # to remove trailing one whitespace
    return error_msg

class EventCreateView(generics.CreateAPIView):
    """
    POST event/
    """    
    serializer_class = EventSerializer

    def post(self, request, *args, **kwargs):
        day = request.data.get("day", "")
        month = request.data.get("month", "")
        year = request.data.get("year", "")
        location = request.data.get("location", "")
        
        if not day or not month or not year or not location:
            return Response(data={"message": "need complete date and location of the event"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.date(day=int(day), month=int(month), year=int(year))
        except ValueError as err:
            return Response(data={"message":err.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        event_serializer = self.serializer_class(data={'date':date, 'location':location})
        if event_serializer.is_valid():
            event_serializer.save()
            return Response(data=event_serializer.data, status=status.HTTP_201_CREATED)
        else:
            error_msg = errorMessageFromSerializer(event_serializer)
            return Response(data={"message":error_msg}, status=status.HTTP_400_BAD_REQUEST)

class EventAllView(generics.ListAPIView):
    """
    GET event/all/
    """
    serializer_class = EventSerializer
    queryset = Event.objects.all()


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET event/<int:year>/<int:month>/<int:day>/
    PUT event/<int:year>/<int:month>/<int:day>/
    DELETE event/<int:year>/<int:month>/<int:day>/
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get(self, request, *args, **kwargs):
        date = datetime.date(day=kwargs["day"], month=kwargs["month"], year=kwargs["year"])
        try:
            event_obj = self.queryset.get(date=date)
            return Response(self.serializer_class(event_obj).data)
        except Event.DoesNotExist:
            return Response(data={"message": "event on {}/{}/{} does not exist".format(kwargs["day"], kwargs["month"], kwargs["year"])}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        date = datetime.date(day=kwargs["day"], month=kwargs["month"], year=kwargs["year"])
        try:
            event_obj = self.queryset.get(date=date)
            day = request.data.get("day", kwargs["day"])
            month = request.data.get("month", kwargs["month"])
            year = request.data.get("year", kwargs["year"])
            update_location = request.data.get("location", event_obj.location)
            update_date = datetime.date(day=int(day), month=int(month), year=int(year))
            if update_date == date and update_location == event_obj.location:
                return Response(data={"message": "event with date {}/{}/{} and location {} already exists".format(day, month, year, update_location)}, status=status.HTTP_400_BAD_REQUEST)
            event_serializer = self.serializer_class(instance=event_obj, data={'date':update_date, 'location':update_location})
            if event_serializer.is_valid():
                event_serializer.save()
                return Response(data=event_serializer.data)
            else:
                return Response(data=event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response(data={"message": "event on {}/{}/{} does not exist".format(kwargs["day"], kwargs["month"], kwargs["year"])}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        date = datetime.date(day=kwargs["day"], month=kwargs["month"], year=kwargs["year"])
        try:
            event_obj = self.queryset.get(date=date)
            event_obj.delete()
            return Response(data={"message": "event on {}/{}/{} deleted".format(kwargs["day"], kwargs["month"], kwargs["year"])}, status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response(data={"message": "event on {}/{}/{} does not exist".format(kwargs["day"], kwargs["month"], kwargs["year"])}, status=status.HTTP_404_NOT_FOUND)


class PersonAllView(generics.ListAPIView):
    """
    GET person/all/
    """
    serializer_class = PersonSerializer
    queryset = Person.objects.all()
        
class AttendanceAllView(generics.ListAPIView):
    """
    GET attendance/all/
    """
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()

class AttendanceDateView(generics.ListAPIView):
    """
    GET attendance/<int:year>/<int:month>/<int:day>/
    """
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            date = datetime.date(day=kwargs["day"], month=kwargs["month"], year=kwargs["year"])
        except ValueError as err:
            return Response(data={"message":err.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_obj = Event.objects.get(date=date)
            attendance_objs = self.queryset.filter(event=event_obj)
            if len(attendance_objs) != 0:
                return Response(self.serializer_class(attendance_objs, many=True).data)
            else:
                return Response(data={"message": "attendance for event on {}/{}/{} does not exist".format(kwargs["day"], kwargs["month"], kwargs["year"])}, status=status.HTTP_404_NOT_FOUND)
        except Event.DoesNotExist:
            return Response(data={"message": "event on {}/{}/{} does not exist".format(kwargs["day"], kwargs["month"], kwargs["year"])}, status=status.HTTP_404_NOT_FOUND)

class AttendanceDatePresentView(generics.ListAPIView):
    """
    GET attendance/present/<int:year>/<int:month>/<int:day>/
    """
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()
    
    def get(self, request, *args, **kwargs):
        try:
            date = datetime.date(day=kwargs["day"], month=kwargs["month"], year=kwargs["year"])
        except ValueError as err:
            return Response(data={"message":err.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_obj = Event.objects.get(date=date)
            attendance_objs = self.queryset.filter(event=event_obj, attended=True)
            if len(attendance_objs) != 0:
                return Response(self.serializer_class(attendance_objs, many=True).data)
            else:
                return Response(data={"message": "either attendance does not exist for event on {}/{}/{} or no one attended the show".format(kwargs["day"], kwargs["month"], kwargs["year"])},
                                status=status.HTTP_404_NOT_FOUND)
        except Event.DoesNotExist:
            return Response(data={"message": "event on {}/{}/{} does not exist".format(kwargs["day"], kwargs["month"], kwargs["year"])}, status=status.HTTP_404_NOT_FOUND)
        
class AttendanceCreateView(generics.CreateAPIView):
    """
    POST attendance/
    """
    serializer_class = AttendanceSerializer

    def post(self, request, *args, **kwargs):
        day = request.data.get("day", "")
        month = request.data.get("month", "")
        year = request.data.get("year", "")
        people_list = request.data.get("people",[])

        if not day or not month or not year:
            return Response(data={"message":"need complete date to create attendance"}, status=status.HTTP_400_BAD_REQUEST)

        if not people_list:
             return Response(data={"message":"need email addresses to create attendance"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.date(day=int(day), month=int(month), year=int(year))
        except ValueError as err:
            return Response(data={"message":err.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_obj = Event.objects.get(date=date)
        except Event.DoesNotExist:
            return Response(data={"message":"event on {}/{}/{} does not exist. Create event first.".format(day, month, year)}, status=status.HTTP_404_NOT_FOUND)

        for people in people_list:
            first_name = str(people['first_name'])
            last_name = str(people['last_name'])
            email = str(people['email'])
            person_obj = None
            if not Person.objects.filter(email=email).exists():
                person_serializer = PersonSerializer(data={'first_name':first_name, 'last_name':last_name, 'email':email})
                if person_serializer.is_valid():
                    person_obj = person_serializer.save()
                else:
                    error_msg = errorMessageFromSerializer(person_serializer)
                    return Response(data={"message":error_msg + " for {} {} ({})".format(first_name, last_name, email)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                person_obj = Person.objects.get(email=email)

            if not Attendance.objects.filter(event=event_obj, person=person_obj).exists():
                attendance_serializer = self.serializer_class(data={'event':event_obj.id, 'person':person_obj.id, 'attended':False}) # NOTE: passing id instead of object. See overridden 'to_internal_value' in the declaration of serializer
                if attendance_serializer.is_valid():
                    attendance_serializer.save()
                else:
                    errorMsg = errorMessageFromSerializer(attendance_serializer)
                    return Response(data={"message":errorMsg + " while creating attendance for {} {}".format(first_name, last_name)},status=status.HTTP_400_BAD_REQUEST)

        attendance_objs = Attendance.objects.filter(event=event_obj)
        return Response(self.serializer_class(attendance_objs, many=True).data, status=status.HTTP_201_CREATED)

class AttendanceMarkPresentView(generics.UpdateAPIView):
    """
    PUT attendance/present/
    """
    serializer_class = AttendanceSerializer

    def put(self, request, *args, **kwargs):
        day = request.data.get("day", "")
        month = request.data.get("month", "")
        year = request.data.get("year", "")
        email = request.data.get("email", "")
        attended = request.data.get("attended", False)

        if not day or not month or not year:
            return Response(data={"message":"need complete date to mark attendance"}, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response(data={"message":"need email address of attendee to mark attendance"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.date(day=int(day), month=int(month), year=int(year))
        except ValueError as err:
            return Response(data={"message":err.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_obj = Event.objects.get(date=date)
        except Event.DoesNotExist:
            return Response(data={"message":"event on {}/{}/{} does not exist. Create event first.".format(day, month, year)}, status=status.HTTP_404_NOT_FOUND)

        try:
            person_obj = Person.objects.get(email=email)
        except Person.DoesNotExist:
            return Response(data={"message":"person with email address: {} did not sign up".format(email)}, status=status.HTTP_404_NOT_FOUND)

        try:
            attendance_obj = Attendance.objects.get(event=event_obj, person=person_obj)
            if attended == attendance_obj.attended:
                return Response(data={"message":"attendance for email address: {} for event on {}/{}/{} already marked {}".format(email, day, month, year, attended)}, status=status.HTTP_400_BAD_REQUEST)
            attendance_serializer = self.serializer_class(instance=attendance_obj, data={'attended':attended}, partial=True)
            if attendance_serializer.is_valid():
                attendance_obj = attendance_serializer.save()
                return Response(attendance_serializer.data)
            else:
                errorMsg = errorMessageFromSerializer(attendance_serializer)
                return Response(data={"message":errorMsg + " while updating attendance for {} for event on {}/{}/{}".format(email, day, month, year)},status=status.HTTP_400_BAD_REQUEST)
        except Attendance.DoesNotExist:
            return Response(data={"message":"no attendance exist for person with email address: {} for event on {}/{}/{}".format(email, day, month, year)}, status=status.HTTP_404_NOT_FOUND)

        
                    
