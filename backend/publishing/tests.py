from django.test import TestCase
from core.models import Organization
from .models import Article
class PublishingTests(TestCase):
    def test_draft_not_public(self):
        org=Organization.objects.create(name='Public Agency',slug='public-agency')
        Article.objects.create(organization=org,slug='private',title='Draft',body='Not public')
        response=self.client.get('/site/public-agency/')
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,'Not public')