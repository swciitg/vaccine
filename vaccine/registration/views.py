from django.http import request
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Benificial,User
from datetime import datetime, timedelta
from functools import wraps
# Create your views here.

def is_verified(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        #not a first time user
        if Benificial.objects.filter(user=request.user).exists():
            beneficial = Benificial.objects.get(user=request.user)
            #have registered for the vaccine
            if beneficial.is_registered:
                if beneficial.is_delivered and beneficial.slot_timing<=datetime.now():
                    #missed the slot , have to register again
                    if not beneficial.is_vaccinated:
                        beneficial.slot_timing = None
                        beneficial.is_delivered = False
                        beneficial.is_registered = False
                        beneficial.registration_timing = None
                        beneficial.save()
                    # got vaccinated , for second dose after 60 days
                    elif beneficial.dose_num == 2 and beneficial.slot_timings + timedelta(60)<=datetime.now():
                        beneficial.slot_timing = None
                        beneficial.is_delivered = False
                        beneficial.is_registered = False
                        beneficial.registration_timing = None
                        beneficial.save()
                    # got vaccinated 2 times , cant do again    
                    elif beneficial.dose_num != 2:
                        return render(request,'error.html',{'message':'You cant register again'})
                    # have to wait until 60 days is over
                    else:
                        message = 'wait till '+ string(beneficial.slot_timings.date() + timedelta(60))+ ' to register again'
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
    beneficial = None
    try:
        beneficial = Benificial.objects.get(user=request.user)
        roll_number = beneficial.roll_number
        contact_1 = beneficial.contact_1
        contact_2 = beneficial.contact_2
    except:
        print("first time")
    if request.method=='POST':
        if beneficial is not None:
            beneficial.roll_number=request.POST['rollNumber']
            beneficial.is_registered=True
            beneficial.registration_timing=datetime.now()
            beneficial.contact_1=request.POST['contact_1']
            beneficial.contact_2=request.POST['contact_2'] 
            beneficial.save()
        else:
            Benificial.objects.create(
                user=request.user,
                roll_number=request.POST['rollNumber'],
                is_registered=True,
                registration_timing=datetime.now(),
                contact_1=request.POST['contact_1'],
                contact_2=request.POST['contact_2']    
            )
    print("hm return me aa gye")
    return render(request,'register.html',{'roll_number':roll_number,'contact_1':contact_1,'contact_2':contact_2})