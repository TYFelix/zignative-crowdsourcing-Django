import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse

from customer.models import Contest, SubCategory, Finalist
from designer.models import Work, FinalWork
from home.forms import WorkForm
import base64
import io
from PIL import Image

import base64

from django.core.files.base import ContentFile

from home.models import InformationPage


def base64_to_image(data,contest_id,user):
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]

    data = ContentFile(base64.b64decode(imgstr), name='{}_{}.'.format(contest_id,user.username) + ext)  # You can save this as file instance.
    return data

@login_required(login_url="user:login")
def index(request):
    works=Work.objects.filter(user=request.user,is_deleted=False)
    contests=Contest.objects.filter(entries__in=works)
    return render(request,"designer/index.html",context={"works":works,"contests":contests})

@login_required(login_url="user:login")
def browse_contests(request):
    services=SubCategory.objects.all()
    page = request.GET.get('page', 1)
    filter = request.GET.get('filter', 'in_progress')
    innering = inner_filtering(request, page, filter)
    return render(request,"designer/browse_contests.html",context={"contests":innering["contests"],
                                             "services":services,
                                             "param_string":innering["param_string"],
                                             "filter":filter})
def inner_filtering(request,page,filter):
    body = dict(request.GET)
    bag = {}
    if filter == "in_progress":
        qs = Contest.objects.filter(is_draft=False, is_temp=False,is_paid=True,status="in_progress").exclude(status="canceled").order_by("-created_date")
    elif filter == "completed":
        qs = Contest.objects.filter(is_draft=False, is_temp=False,is_paid=True,status="completed").exclude(status="canceled").order_by("-created_date")

    try:
        body_srvc = body["service_select"][0]
    except KeyError:
        body_srvc = "All Categories"
    try:
        body_ind = body["industry_select"][0]
    except KeyError:
        body_ind = "All Industries"

    service = False if body_srvc == "All Categories" else True
    industry = False if body_ind == "All Industries" else True

    if service and industry:
        qs = qs.filter(form_fields__contest_industry=body_ind, category_id=body_srvc)
        bag.update({"industry_select": body_ind, "service_select": body_srvc})
    elif service:
        qs = qs.filter(category_id=body_srvc)
        bag.update({"service_select": body_srvc})

    elif industry:
        qs = qs.filter(form_fields__contest_industry=body_ind)
        bag.update({"industry_select": body_ind})

    if "order_select" in body:
        temp = body["order_select"][0]

        if temp.split("_")[0] == "old":
            if temp.split("_")[1] == "1": qs = qs.order_by("created_date")

        if temp.split("_")[0] == "prize":
            if temp.split("_")[1] == "0": qs = qs.order_by("-form_fields__price")

        if temp.split("_")[0] == "time":
            if temp.split("_")[1] == "0":
                qs = qs.order_by("finish_date")
            else:
                qs = qs.order_by("-finish_date")

        if temp.split("_")[0] == "entry":
            if temp.split("_")[1] == "0":
                qs = sorted(qs, key=lambda t: t.get_entry_count())[::-1]
            else:
                qs = sorted(qs, key=lambda t: t.get_entry_count())

        bag.update({"order_select": temp})
    paginator = Paginator(qs, 5)
    try:
        contests = paginator.page(page)
    except PageNotAnInteger:
        contests = paginator.page(1)
    except EmptyPage:
        contests = paginator.page(paginator.num_pages)

    param_string = ""

    for i in bag:
        param_string += "&{}={}".format(i, bag[i])

    return {"param_string":param_string,"contests":contests,"bag":bag}
def get_by_filter(request):
    context = {}
    filter = request.GET.get('filter', 'in_progress')

    innering = inner_filtering(request, "1", filter)

    contests_html = render_to_string("includes/designer/contest_list.html", context={
        "request": request,
        "contests": innering["contests"],
        "param_string": innering["param_string"]
    })

    context.update({"contests_html": contests_html})
    return JsonResponse(context)
def check_extension(name):
    extension=name.split(".")[1]

    if "jpg" == extension or "png" == extension or "jpeg" == extension or "svg" == extension:
        return True
    else:return False

def is_secure_extension(name):
    extension=name.split(".")[1]

    bad_extension=["exe","py","vbs","bat","dll","vb","dat"]


    if extension in bad_extension:
        return False
    else:
        return True

def submit_design(request,contest_id):

    contest = Contest.objects.get(id=contest_id)
    terms=InformationPage.objects.get(name="terms_of_use")

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        cropped_base64=body["cropped_blob"]
        original_base64=body["original_blob"]

        cropped_image=base64_to_image(cropped_base64,contest_id,request.user)
        original_image=base64_to_image(original_base64,contest_id,request.user)

        Work.objects.create(contest_id=contest_id,user=request.user,image=original_image,display_image=cropped_image)

        return JsonResponse({"ali":"ata bak"})

    return render(request,"designer/submit_entry.html",{"contest":contest,"terms":terms})

def submit_final_design(request,contest_id):

    contest=Contest.objects.get(id=contest_id)
    for i in request.FILES:
        if not check_extension(str(request.FILES.get(i))):
            messages.warning(request, "Please upload an image in valid format. (png, jpg, svg).")
            return redirect("home:contest", contest_id)


    for finalist in contest.finalists.all():
        if request.user == finalist.entry.user:
            if request.FILES.get(str(finalist.entry.id)):


                finalist.entry.image=request.FILES.get(str(finalist.entry.id))
                finalist.entry.save()

    return redirect("home:contest",contest_id)


def submit_all_files(request,contest_id):
    contest=Contest.objects.get(id=contest_id)
    contest.is_submitted=True
    contest.save()
    return redirect("home:contest",contest.id)

def delete_entry(request,entry):
    work=Work.objects.get(id=entry)
    work.is_deleted=True
    work.save()
    messages.success(request, "Design successfully deleted")

    return redirect("home:contest",work.contest.id)


def submit_final_works(request,contest_id,entry_id):
    for file in request.FILES.getlist("files"):
        if not is_secure_extension(str(file)):
            messages.error(request, "Disallowed file type.")
            return redirect("home:contest", contest_id)
    for file in request.FILES.getlist("files"):
        FinalWork.objects.create(file=file,contest_id=contest_id,entry_id=entry_id)

    print("noldi la")
    response = redirect("home:contest", contest_id)
    response['Location'] += '?tab=files'
    return response


def delete_final_work(request,contest_id,work_id):
    FinalWork.objects.get(contest_id=contest_id,id=work_id).delete()
    return redirect("home:contest", contest_id)

def approve_files(request,contest_id):
    contest=Contest.objects.get(id=contest_id)
    contest.status="completed"
    messages.success(request, "Files approved.")
    contest.save()
    return redirect("home:contest", contest_id)
