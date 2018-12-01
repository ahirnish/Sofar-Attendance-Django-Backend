from django.db import models

# Create your models here.

class Event(models.Model):
    """
    Model to hold detail of Sofar event.
    """
    date = models.DateField(unique=True, help_text="Date of Sofar event")
    location = models.CharField(max_length=255, help_text="Location of Sofar Event")

    class Meta:
        ordering = ['date']

    def __str__(self):
        return "Sofar: date - {}/{}/{}, location - {}".format(self.date.day, self.date.month,self.date.year, self.location)

class Person(models.Model):
    """
    Model to hold detail of person attending the event.
    """
    first_name = models.CharField(max_length=255, help_text="First name of the person")
    last_name = models.CharField(max_length=255, blank=True, help_text="Last name of the person")
    email = models.EmailField(unique=True, help_text="Email of the person")

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} {} ({})".format(self.first_name, self.last_name, self.email)

class Attendance(models.Model):
    """
    Model to keep track of attendance of people.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, help_text="Sofar event detail")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, help_text="Detail of person attending the event")
    attended = models.BooleanField(default=False, help_text="Attended or did not attend the event")

    class Meta:
        ordering = ['event']

    def __str__(self):
        return "{} {} attended the event on {}/{}/{}: {}".format(self.person.first_name, self.person.last_name, self.event.date.day, self.event.date.month, self.date.year, self.attended)
