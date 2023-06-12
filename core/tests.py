import json
from collections import OrderedDict

import rest_framework_simplejwt
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Rate
import responses


class RatesTests(APITestCase):
    def setUp(self):
        date = timezone.datetime(2022, 1, 1)
        self.rate = Rate(
            base="USD",
            target="XDR",
            rate=0.1,
            date=date,
        )
        self.rate.save()
        self.user = User.objects.create_user("foo", password="bar")
        self.client.force_authenticate(user=self.user)

    def test_get_rates(self):
        response = self.client.get("/rates/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            json.loads(response.content)["results"],
            [{"base": "USD", "target": "XDR", "rate": 0.1, "date": "2022-01-01"}],
        )

    def tearDown(self):
        self.client.force_authenticate(user=None)
        self.rate.delete()
        self.user.delete()

class RatesWithBaseTests(APITestCase):
    def setUp(self):
        date = timezone.datetime(2022, 1, 1)
        self.rate = Rate(
            base="USD",
            target="XDR",
            rate=0.1,
            date=date,
        )
        self.rate.save()
        self.user = User.objects.create_user("foo", password="bar")
        self.client.force_authenticate(user=self.user)

    def test_get_rates(self):
        response = self.client.get("/rates/USD/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # breakpoint()
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            json.loads(response.content)["results"],
            [{"base": "USD", "target": "XDR", "rate": 0.1, "date": "2022-01-01"}],
        )

    def tearDown(self):
        self.client.force_authenticate(user=None)
        self.rate.delete()
        self.user.delete()


class UserRegisterTests(APITestCase):
    def test_user_registration(self):
        response = self.client.post(
            "/register/",
            {
                "username": "test_user",
                "password": "pass12345",
                "confirmPassword": "pass12345",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="test_user").username, "test_user")

    def tearDown(self):
        User.objects.get(username="test_user").delete()


class UserRegisterThatAlreadyExistsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_user", password="pass12345")

    def test_user_registration(self):
        response = self.client.post(
            "/register/",
            {
                "username": "test_user",
                "password": "pass12345",
                "confirmPassword": "pass12345",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        User.objects.get(username="test_user").delete()


class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_user22", password="pass12345")
        
    def test_user_login(self):
        response = self.client.post("/login/", {"username": "test_user22", "password": "pass12345"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        User.objects.get(username=self.user.username).delete()

class RatesWithBaseAndTargetTests(APITestCase):
    def setUp(self):
        date = timezone.datetime(2022, 1, 1)
        self.rate = Rate(
            base="USD",
            target="XDR",
            rate=0.1,
            date=date,
        )
        self.rate.save()
        self.user = User.objects.create_user("foo", password="bar")
        self.client.force_authenticate(user=self.user)

    def test_get_rates(self):
        response = self.client.get("/rates/USD/XDR/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            json.loads(response.content)["results"],
            [{"base": "USD", "target": "XDR", "rate": 0.1, "date": "2022-01-01"}],
        )    

    def tearDown(self):
        self.client.force_authenticate(user=None)
        self.rate.delete()
        self.user.delete()

class SeedTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("foo", password="bar")
        self.client.force_authenticate(user=self.user)

    @responses.activate
    def test_seed(self):
        responses.add(
            method=responses.GET,
            url='https://api.exchangerate.host/latest',
            json={'base': 'USD', "date": "2022-04-26", "rates": {"XDR": 0.929709}},
            match=[responses.matchers.query_param_matcher({"base": "USD"})],
        )
        responses.add(
            method=responses.GET,
            url='https://api.exchangerate.host/latest',
            json={'base': 'EUR', "date": "2022-04-26", "rates": {"BGN": 2.32394}},
            match=[responses.matchers.query_param_matcher({"base": "EUR"})],
        )
        responses.add(
            method=responses.GET,
            url='https://api.exchangerate.host/latest',
            json={'base': 'CHF', "date": "2022-04-26", "rates": {"IMP": 0.999867}},
            match=[responses.matchers.query_param_matcher({"base": "CHF"})],
        )
        responses.add(
            method=responses.GET,
            url='https://api.exchangerate.host/latest',
            json={'base': 'GBP', "date": "2022-04-26", "rates": {"JOD": 0.91045}},
            match=[responses.matchers.query_param_matcher({"base": "GBP"})],
        )
        response = self.client.post('/seed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Rate.objects.count(), 4)
        self.assertEqual(Rate.objects.get(base='USD', target='XDR').rate, 0.929709)
        self.assertEqual(Rate.objects.get(base='EUR', target='BGN').rate, 2.32394)
        self.assertEqual(Rate.objects.get(base='CHF', target='IMP').rate, 0.999867)
        self.assertEqual(Rate.objects.get(base='GBP', target='JOD').rate, 0.91045)

    def tearDown(self):
        self.client.force_authenticate(user=None)
        Rate.objects.all().delete()
        self.user.delete()
