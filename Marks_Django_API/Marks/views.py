from rest_framework.views import APIView
from rest_framework.response import Response
from . import serializers
from rest_framework import status
from .Scraper import Scrapy
from django.http import response,request
from django.shortcuts import render
class MarksApiView(APIView):
     """Marks API View"""
     serializer_class = serializers.HelloSerializer
     def get(self,request,format=None):
         """Returns a list of APIView"""
         an_apiview = ['Use Post request for Progress bar','Send Username and Password in body']
         return Response({'message':'Hello','an_apiview':an_apiview})
     def post(self,request):
         """Post request"""
         serializers = self.serializer_class(data = request.data)
         if serializers.is_valid():
             message = {}
             Username= serializers.validated_data.get('Username')
             Password = serializers.validated_data.get('Password')
             message = Scrapy(Username,Password)

             return Response(message)
         else:
             return Response(
                 serializers.errors,
                 status=status.HTTP_400_BAD_REQUEST
             )

def index(request):
     return render(request, 'Marks/index.html')

