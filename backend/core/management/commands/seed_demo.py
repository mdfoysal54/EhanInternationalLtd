from django.core.management.base import BaseCommand
from core.models import Organization,Service
class Command(BaseCommand):
    help='Seed sample public services (safe to rerun)'
    def handle(self,*args,**kwargs):
        org,_=Organization.objects.get_or_create(slug='ehan-international',defaults={'name':'Ehan International Ltd'})
        samples=[('Manpower Recruitment','manpower','Manpower'),('Work Visa Consultancy','work-visa','Work Visa'),('Travel and Tourism','travel-tourism','Tourism'),('Hajj and Umrah','hajj-umrah','Umrah'),('Student Consultancy','student','Student')]
        for title,slug,category in samples:
            Service.objects.get_or_create(organization=org,slug=slug,defaults={'title':title,'category':category,'description':'Contact our team for current eligibility, requirements and service details.','published':True})
        self.stdout.write(self.style.SUCCESS('Demo services ready'))
