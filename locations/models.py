from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100) # Local Area / City
    city = models.CharField(max_length=100) # District
    address = models.TextField()

    class Meta:
        unique_together = ('name', 'city')

    def __str__(self):
        if self.name == self.city:
            return self.name
        return f"{self.name}, {self.city}"
