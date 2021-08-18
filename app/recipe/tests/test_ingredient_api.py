from django.contrib.auth import get_user_model
from django.core.exceptions import AppRegistryNotReady
from django.http import response
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """
        Test the publicly available ingredients API
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
            Test that login is required to access the endpoint
        """
        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class PrivateIngredientApiTests(TestCase):
    """
        Test the private ingredient API
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@testakinon.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """
            Test retrieving a list of ingredients
        """
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        response = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data,
            serializer.data
        )

    def test_ingredients_limited_to_user(self):
        """
            Test that ingredients for the authenticated user are returned
        """
        user2 = get_user_model().objects.create_user(
            'other@testakinon.com',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data),
            1
        )
        self.assertEqual(
            response.data[0]['name'],
            ingredient.name
        )
