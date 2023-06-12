from datetime import datetime

import requests
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import filters, generics, pagination
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from core.models import Rate
from core.serializers import (
    MyTokenObtainPairSerializer,
    RateSerializer,
    RegisterSerializer,
)


class RateList(APIView):
    """
    List all of the exchange rates.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        rates = Rate.objects.all()
        serializer = RateSerializer(rates, many=True)
        return Response(serializer.data)


class RateWithBase(generics.ListAPIView):
    """
    List all the exchange rates with a given base currency.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = RateSerializer
    pagination_class = PageNumberPagination
    PageNumberPagination.page_size = 20
    parser_classes = (JSONParser, XMLParser)
    renderer_classes = (JSONRenderer, XMLRenderer)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["rate", "target"]
    ordering = ["target"]

    def get_queryset(self):
        return Rate.objects.filter(base=self.kwargs["base"])


class RateWithBaseAndTarget(APIView):
    """
    Return exchange rate with a given base currnecy and a target currency.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, base, target, format=None):
        rates = Rate.objects.filter(base=base, target=target).all()
        serializer = RateSerializer(rates, many=True)
        return Response(serializer.data)

    def post(self, request, base, target, format=None):

        rates = Rate.objects.filter(base=base, target=target).all()

        if rates:
            serializer = RateSerializer(rates, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = RateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(serializer.data)


class Seed(APIView):
    """
    Exchange rate seed.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        currencies = ["USD", "EUR", "CHF", "GBP"]
        temporary_object_dict = {}
        objects_list = []
        for base in currencies:
            request_params = {"base": base}
            response = requests.get(
                "https://api.exchangerate.host/latest", params=request_params
            )
            response_data = response.json()
            for target in response_data["rates"]:
                temporary_object_dict = {
                    "target": target,
                    "date": datetime.strptime(response_data["date"], "%Y-%m-%d").date(),
                    "base": base,
                    "rate": response_data["rates"][target],
                }
                if Rate.objects.filter(base=base, target=target).all():
                    Rate.objects.get(base=base, target=target).delete()
                objects_list.append(temporary_object_dict)
        serializer = RateSerializer(data=objects_list, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()


class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class MyObtainTokenPairView(TokenObtainPairView):
    """
    Get a Token for a user that logged in.
    """

    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer
