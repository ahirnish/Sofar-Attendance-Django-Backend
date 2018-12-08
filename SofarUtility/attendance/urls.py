from django.urls import path
from .views import EventCreateView, EventDetailView, EventAllView, AttendanceCreateView, \
    AttendanceAllView, PersonAllView, AttendanceMarkPresentView, AttendanceDateView, AttendanceDatePresentView

urlpatterns= [
    path('event/', EventCreateView.as_view(), name="event-create"),
    path('event/all/', EventAllView.as_view(), name="event-all"),
    path('event/<int:year>/<int:month>/<int:day>/', EventDetailView.as_view(), name="event-detail"),
    path('attendance/', AttendanceCreateView.as_view(), name="attendance-create"),
    path('attendance/<int:year>/<int:month>/<int:day>/', AttendanceDateView.as_view(), name="attendance-date"),
    path('attendance/present/<int:year>/<int:month>/<int:day>/', AttendanceDatePresentView.as_view(), name="attendance-date-present"),
    path('attendance/all/', AttendanceAllView.as_view(), name="attendance-all"),
    path('attendance/present/', AttendanceMarkPresentView.as_view(), name="attendance-present"),
    path('person/all/', PersonAllView.as_view(), name="person-all"),
]
