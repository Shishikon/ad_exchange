from django.test import TestCase
from django.contrib.auth.models import User
from django.views.decorators.http import condition
from unicodedata import category

from .models import Ad, ExchangeProposal


class AdTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester_user', password='tester123')
        self.client.login(username='tester_user', password='tester123')


    def test_create_ad(self):
        response = self.client.post('/ads/new/', {
            'title': 'first test' ,
            'description': 'test',
            'category': 'clothes',
            'condition':'used',

        })



        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.count(), 1)

    def test_edit_ad(self):
        ad = Ad.objects.create(
            user = self.user,
            title = 'old title',
            description = 'old description',
            category='books',
            condition = 'new',

        )

        response = self.client.post(f'/ads/{ad.pk}/edit/', {
            'title':'new title',
            'description':'new description',
            'category': 'clothes',
            'condition': 'used',
        })
        ad.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ad.title, 'new title')
        self.assertEqual(ad.condition, 'used')


    def test_delete_ad(self):
        ad = Ad.objects.create(
            user=self.user,
            title='delete title',
            description='description',
            category='new',
            condition='books',

        )

        response = self.client.post(f'/ads/{ad.pk}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(pk=ad.pk).exists())


    def test_search_ad(self):
        Ad.objects.create(
            user=self.user,
            title='Under Armour',
            description='Under Armour Clothes',
            category='clothes',
            condition='new',
        )
        Ad.objects.create(
            user=self.user,
            title='Dolce Gabanna',
            description='Dolce Gabanna Clothes',
            category='clothes',
            condition='new',
        )
        response = self.client.get('/?q=Under')
        self.assertContains(response, 'Under Armour')
        self.assertNotContains(response, 'Dolce Gabanna')


    def test_proposal_accept_and_reject(self):
        user2 = User.objects.create_user(username='user_2', password='user_2_123')
        ad_sender = Ad.objects.create(user=self.user, title='first ad', description='description', category='tech', condition='new')
        ad_receiver = Ad.objects.create(user=user2, title='second ad', description='description', category='clothes', condition='used')


        self.client.login(username='tester_user', password='tester123')

        response = self.client.post(f'/proposals/{ad_receiver.pk}/new/', {
            'ad_sender': ad_sender.pk,
            'ad_receiver': ad_receiver.pk,
            'comment': 'lets barter',
        })


        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExchangeProposal.objects.count(), 1)


        self.client.logout()
        self.client.login(username='user_2', password='user_2_123')
        proposal = ExchangeProposal.objects.first()

        response = self.client.post(f'/proposals/{proposal.pk}/accept/')
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')

        # self.client.logout()
        # self.client.login(username='user_2', password='user_2_123')
        # proposal = ExchangeProposal.objects.second()
        #
        # response = self.client.post(f'/proposals/{proposal.pk}/reject/')
        # response.refresh_from_db()
        # self.assertEqual(proposal.status, 'rejected')