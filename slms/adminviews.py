from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from slmsapp.models import CustomUser, Staff, Staff_Leave
import re


def send_email(stf_email, status):
    if status == 1:
        stat = "Accepted!"
    else:
        stat = "rejected."
        
    subject = "Regarding your leave request"
    message = f"This is to inform you that your leave request has been {stat}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["chaitanyajly0904@gmail.com"]
    send_email(subject, message, from_email, recipient_list)

@login_required(login_url='/')
def HOME(request):
    staff_count = Staff.objects.all().count()
    leave_count = Staff_Leave.objects.all().count()
    context = {
        'staff_count': staff_count,
        'leave_count': leave_count
    }
    return render(request, 'admin/home.html', context)


def ADD_STAFF(request):
    if request.method == "POST": 
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')

        # Validate first name
        if not first_name or len(first_name) < 2 or not re.match("^[A-Za-z]+$", first_name):
            messages.success(request, 'Invalid name')
            return redirect('add_staff')

        # Validate last name
        if not last_name or len(last_name) < 2 or not re.match("^[A-Za-z]+$", last_name):
            messages.success(request, 'Invalid name')
            return redirect('add_staff')

        # Validate username
        if not username or len(username) != 4 or not username.isdigit():
            messages.success(request, 'Username is invalid (exact 4 digits)')
            return redirect('add_staff')

        try:
            validate_email(email)
            domain = email.split('@')[1]
            if domain not in ['gmail.com', 'yahoo.com']:
                raise ValidationError("Invalid email. Please provide a Gmail or Yahoo email.")
        except ValidationError as e:
            messages.success(request, 'Email is invalid. It should be in the form of @gmail or @yahoo')
            return redirect('add_staff')

        if CustomUser.objects.filter(email=email).exists():
            messages.success(request, 'Email is already exist')
            return redirect('add_staff')

        if CustomUser.objects.filter(username=username).exists():
            messages.success(request, 'Username is already exist')
            return redirect('add_staff')

        if len(password) <= 8 or not re.match(r"^(?=.*\d)(?=.*[a-zA-Z])(?=.*[@#$%^&+=]).{8,}$", password):
            messages.success(request, 'Password must be greater than 8 characters and contain numbers, letters, and at least one special character')
            return redirect('add_staff')

        else:
            user = CustomUser(first_name=first_name, last_name=last_name, email=email, profile_pic=profile_pic,
                              user_type=2, username=username)
            user.set_password(password)
            user.save()
            staff = Staff(
                admin=user,
                address=address,
                gender=gender
            )
            staff.save()
            messages.success(request, 'Staff details have been added successfully')
            return redirect('add_staff')

    return render(request, 'admin/add_staff.html')


def VIEW_STAFF(request):
    staff = Staff.objects.all()
    context = {
        "staff": staff,
    }
    return render(request, 'admin/view_staff.html', context)


def EDIT_STAFF(request, id):
    staff = Staff.objects.get(id=id)
    context = {
        "staff": staff,
    }
    return render(request, 'admin/edit_staff.html', context)


def UPDATE_STAFF(request):
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')

        user = CustomUser.objects.get(id=staff_id)
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password != None and password != "":
            user.set_password(password)
        if profile_pic != None and profile_pic != "":
            user.profile_pic = profile_pic
        user.save()
        staff = Staff.objects.get(admin=staff_id)
        staff.gender = gender
        staff.address = address
        staff.save()
        messages.success(request, 'Staff details have been successfully updated')
        return redirect('view_staff')

    return render(request, 'admin/edit_staff.html')


def DELETE_STAFF(request, admin):
    staff = CustomUser.objects.get(id=admin)
    staff.delete()
    messages.success(request, "Staff record has been deleted successfully.")
    return redirect('view_staff')


def STAFF_LEAVE_VIEW(request):
    staff_leave = Staff_Leave.objects.all()
    context = {
        "staff_leave": staff_leave,
    }
    return render(request, 'admin/staff_leave.html', context)



def STAFF_APPROVE_LEAVE(request, id):
    
    
    leave = Staff_Leave.objects.get(id=id)
    leave.status = 1
    leave.save()

    # send_email(CustomUser.email,status=1)
    return redirect('staff_leave_view_admin')


def STAFF_DISAPPROVE_LEAVE(request, id):
    leave = Staff_Leave.objects.get(id=id)
    leave.status = 2
    leave.save()

    # send_email(CustomUser.email,status=0)
    return redirect('staff_leave_view_admin')
