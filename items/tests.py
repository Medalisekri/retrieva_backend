# items/tests.py
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Item


class ItemListTests(APITestCase):
    """GET /items/item/ — expiry and filtering."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner_uid', email='owner@test.com'
        )
        self.item = Item.objects.create(
            type='lost',
            category='Wallet',
            name='Brown wallet',
            lat=35.0,
            long=9.5,
            status='active',
            user=self.owner,
        )
        # Authenticate so we focus on the logic, not auth
        self.client.force_authenticate(user=self.owner)

    def test_active_item_appears_in_list(self):
        response = self.client.get('/items/item/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [i['name'] for i in response.data['results']]
        self.assertIn('Brown wallet', names)

    def test_expired_item_is_hidden(self):
        Item.objects.create(
            type='found',
            category='Phone',
            name='Old phone',
            lat=36.0,
            long=10.0,
            status='active',
            user=self.owner,
            expires_at=timezone.now().date() - timedelta(days=1),  # expired yesterday
        )
        response = self.client.get('/items/item/')
        names = [i['name'] for i in response.data['results']]
        self.assertNotIn('Old phone', names)

    def test_resolved_item_is_hidden(self):
        self.item.status = 'resolved'
        self.item.save()
        response = self.client.get('/items/item/')
        names = [i['name'] for i in response.data['results']]
        self.assertNotIn('Brown wallet', names)

    def test_filter_by_type(self):
        response = self.client.get('/items/item/', {'type': 'found'})
        names = [i['name'] for i in response.data['results']]
        # Our item is 'lost', so it should NOT appear when filtering for 'found'
        self.assertNotIn('Brown wallet', names)


class ItemPermissionTests(APITestCase):
    """Only the owner can edit or delete their item."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner_uid', email='owner@test.com'
        )
        self.stranger = User.objects.create_user(
            username='stranger_uid', email='stranger@test.com'
        )
        self.item = Item.objects.create(
            type='lost',
            category='Wallet',
            name='Brown wallet',
            lat=35.0,
            long=9.5,
            status='active',
            user=self.owner,
        )
        self.url = f'/items/item/{self.item.id}/'

    def test_owner_can_update(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.url, {'name': 'Updated wallet'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated wallet')

    def test_stranger_cannot_update(self):
        self.client.force_authenticate(user=self.stranger)
        response = self.client.patch(self.url, {'name': 'Hacked!'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_delete(self):
        self.client.force_authenticate(user=self.stranger)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Item.objects.filter(id=self.item.id).exists())

    def test_owner_can_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.url)
        # Your view returns 201 on delete; 200/204 would also be acceptable
        self.assertIn(response.status_code, [200, 201, 204])
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())