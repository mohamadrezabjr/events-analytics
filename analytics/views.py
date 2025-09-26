from django.shortcuts import render
from rest_framework import generics
from analytics.models import Event
from analytics.serializers import CreateEventSerializer


class CreateEvent(generics.CreateAPIView):
    serializer_class = CreateEventSerializer
