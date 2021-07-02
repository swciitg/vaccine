from typing import List
from django.db.models.fields import TimeField
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView
from .models import Addvaccines
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import traceback
from django.contrib.admin.views.decorators import staff_member_required
from registration.models import Benificial, User
from django.db.models import Q
from datetime import time,datetime
@staff_member_required
def index(request):
    return render(request,'home.html')

slot_dict = {
    '0': time(9),
    '1': time(11),
    '2': time(13)
}
@staff_member_required
def send_email(request):
    if request.method=="POST":
        name = request.POST.get('name')
        slot = request.POST.get('slot')
        doses = request.POST.get('doses')
        date = request.POST.get('date')
        print(name, slot, doses)
        s=["9 to 12", "12 to 3", "3 to 5"]
        benificials = Benificial.objects.filter(
            Q(is_registered=True) & Q(is_delivered=False)
        ).order_by('registration_timing')[:int(doses)]
        print(benificials)
        list_emails = []
        for benificial in benificials:
            benificial.is_delivered=True
            benificial.slot_timing=datetime.combine(datetime.strptime(date,"%Y-%m-%d"),slot_dict[slot])
            benificial.save()   
            list_emails.append(benificial.user.username)
        email = EmailMessage(
            subject='vaccine lag gyi?',
            body="your vaccine slot is "+s[int(slot)]+" "+date,
            from_email='swc@iitg.ac.in',
            to=list_emails,
        )
        Addvaccines.objects.create(
            name_of_vaccine=name,   
            slot=slot,
            date=date,
            numbers_of_vaccine=doses,
            extra_vaccine = int(doses)-len(benificials)
        )
        # 'satyendr@iitg.ac.in'
        email.content_subtype = 'html' 
        try:
            email.send(fail_silently=False)
            return HttpResponseRedirect(reverse('apply:success'))
        except Exception:
            print('errorr')
            # print traceback.format_exc() # you probably want to add a log here instead of console printout
        return redirect('index')