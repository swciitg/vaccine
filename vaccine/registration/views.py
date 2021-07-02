from django.http import request
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Benificial,User
from datetime import datetime, timedelta
from functools import wraps
from adminportal.models import Addvaccines
from django.db.models import Q
from adminportal.views import slot_dict
from django.core.mail import send_mail
from django.core.mail import EmailMessage
# Create your views here.

def is_verified(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        #not a first time user
        if Benificial.objects.filter(user=request.user).exists():
            benificial = Benificial.objects.get(user=request.user)
            #have registered for the vaccine
            if benificial.is_registered:
                if benificial.is_delivered and benificial.slot_timing<=datetime.now():
                   
                    # got vaccinated , for second dose after 60 days
                    if benificial.slot_timing + timedelta(60)<=datetime.now():
                        benificial.slot_timing = None
                        benificial.is_delivered = False
                        benificial.is_registered = False
                        benificial.registration_timing = None
                        benificial.save()

                    else:
                        expiry = benificial.slot_timing.date() + timedelta(60)
                        message = 'wait till '+ expiry.strftime("%d-%b-%Y ") + ' to register again'
                        return render(request,'error.html',{'message':message})
                #slot is not provided or upcoming        
                else:
                    return render(request,'error.html',{'message':'You Are already registered. You will get a mail when you are allotted a slot'})
        return function(request, *args, **kwargs)  
    return wrap
    
    
@login_required
@is_verified
def register(request):
    roll_number = request.user.last_name
    contact_1 = None
    contact_2 = None
    benificial = None
    try:
        benificial = Benificial.objects.get(user=request.user)
        roll_number = benificial.roll_number
        contact_1 = benificial.contact_1
        contact_2 = benificial.contact_2
    except:
        print("first time")
    if request.method=='POST':
        if benificial is not None:
            benificial.roll_number=request.POST['rollNumber']
            benificial.is_registered=True
            benificial.registration_timing=datetime.now()
            benificial.contact_1=request.POST['contact_1']
            benificial.contact_2=request.POST['contact_2'] 
            benificial.save()
        else:
            benificial=Benificial.objects.create(
                user=request.user,
                roll_number=request.POST['rollNumber'],
                is_registered=True,
                registration_timing=datetime.now(),
                contact_1=request.POST['contact_1'],
                contact_2=request.POST['contact_2']    
            )
        try: 
            available_slot = Addvaccines.objects.filter(
                Q(date__gt=datetime.now()) & Q(extra_vaccine__gte=1)
            ).order_by('date').order_by('slot')[0]
            benificial.is_delivered=True
            benificial.slot_timing=datetime.combine(available_slot.date,slot_dict[str(available_slot.slot)])
            benificial.save()
            available_slot.extra_vaccine=available_slot.extra_vaccine-1
            available_slot.save()
            s=["9 to 12", "12 to 3", "3 to 5"]
            email = EmailMessage(
                subject='vaccine lag gyi?',
                body="your vaccine slot is "+s[int(available_slot.slot)]+" "+str(available_slot.date),
                from_email='swc@iitg.ac.in',
                to=[benificial.user.username],
            )
            email.content_subtype = 'html' 
            try:
                email.send(fail_silently=False)
                return HttpResponseRedirect(reverse('apply:success'))
            except Exception:
                print('errorr')
            
        except:
            print("none")
    return render(request,'register.html',{'roll_number':roll_number,'contact_1':contact_1,'contact_2':contact_2})