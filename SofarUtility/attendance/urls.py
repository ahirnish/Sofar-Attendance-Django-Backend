from django.urls import path
from .views import EventCreateView, EventDetailView, EventAllView

urlpatterns= [
    path('event/', EventCreateView.as_view(), name="event-create"),
    path('event/all/', EventAllView.as_view(), name="event-all"),
    path('event/<int:year>/<int:month>/<int:day>/', EventDetailView.as_view(), name="event-detail"),
]
