import datetime
import json
import os
import random
from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt

from customer.models import Contest, Feedback, Announcement, SubCategory, Attachment
from designer.models import Work, NDASigners, Review
from home.forms import WorkForm, RequestForm, AnonUserRequestForm
from datetime import timedelta

from home.models import InformationPage, Notification, Contact, PayoutRequest


def in_30_days():
    return timezone.now() + timedelta(days=30)


def check_rounds(request, contest):
    if contest.finish_date < timezone.now():

        if contest.round == "qualify":
            contest.round = "qualify_end"
            contest.finish_date = contest.finish_date + timedelta(days=3)
            contest.save()
            Notification.objects.create(user=contest.user, contest=contest,
                                        contest_round="qualify_end",
                                        notify_type="R")
            Announcement.objects.create(contest=contest, content="qualify_end")


        elif contest.round == "qualify_end" and not contest.is_locked:
            contest.is_locked = True
            contest.locked_date = timezone.now()
            contest.lock_finish_date = in_30_days()
            contest.save()
            Announcement.objects.create(contest=contest,
                                        content=f"Contest locked. Because {contest.user} didn't choose any finalist. ")
            Notification.objects.create(user=contest.user, contest=contest,
                                        notify_type="L",
                                        contest_round="qualify_end")

            entries = contest.entries.all()
            users = []
            for entry in entries:
                users.append(entry.user)
            users = list(set(users))

            for user in users:
                Notification.objects.create(user=user, contest=contest, notify_type="L",
                                            contest_round="qualify_end")

        elif contest.round == "final_round":
            contest.round = "selecting_winner"
            contest.finish_date = contest.finish_date + timedelta(days=5)
            contest.save()
            Notification.objects.create(user=contest.user, contest=contest,
                                        contest_round="selecting_winner",
                                        notify_type="R")

            Announcement.objects.create(contest=contest, content="Final round ended.")

        elif contest.round == "selecting_winner" and not contest.is_locked:
            contest.is_locked = True
            contest.locked_date = timezone.now()
            contest.lock_finish_date = in_30_days()

            contest.save()
            Announcement.objects.create(contest=contest,
                                        content=f"Contest locked. Because {contest.user} didn't choose any winner. ")
            Notification.objects.create(user=contest.user, contest=contest,
                                        notify_type="L",
                                        contest_round="selecting_winner")

            entries = contest.entries.all()
            users = []
            for entry in entries:
                users.append(entry.user)
            users = list(set(users))

            for user in users:
                Notification.objects.create(user=user, contest=contest, notify_type="L",
                                            contest_round="selecting_winner")


def inner_filtering(request, page, filter):
    body = dict(request.GET)
    bag = {}
    if filter == "in_progress":
        qs = Contest.objects.filter(is_draft=False, is_temp=False, is_paid=True,
                                    status="in_progress").exclude(
            status="canceled").order_by("-created_date")
    elif filter == "completed":
        qs = Contest.objects.filter(is_draft=False, is_temp=False, is_paid=True,
                                    status="completed").exclude(
            status="canceled").order_by("-created_date")

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

    return {"param_string": param_string, "contests": contests, "bag": bag}


def react(request):
    return render(request, "react/index.html")


def index(request):
    if request.user.is_authenticated:
        if request.user.profile.role == "client":
            return redirect("customer:index")
        else:
            return redirect("designer:index")
    return redirect("user:login")
    # services = SubCategory.objects.all()
    # page = request.GET.get('page', 1)
    # filter = request.GET.get('filter', 'in_progress')
    # innering = inner_filtering(request, page, filter)
    #
    # return render(request, "home/index.html", {"contests": innering["contests"],
    #                                            "services": services,
    #                                            "param_string": innering["param_string"],
    #                                            "filter": filter})

    # services = SubCategory.objects.all()
    # page = request.GET.get('page', 1)
    # filter = request.GET.get('filter', 'in_progress')
    # innering = inner_filtering(request, page, filter)
    #
    #
    #
    # items = list(Work.objects.filter(contest__round="winner_selected",finalist__is_winner=True))
    # contests = Contest.objects.filter(round="winner_selected")[:4]
    # # change 3 to how many random items you want
    # random_items = random.sample(items, 1)
    # # if you want only a single random item
    # random_item = random.choice(items)
    # return render(request, "new/home/new_index.html",
    #               {"contests": contests,
    #                "services": services,
    #                "param_string": innering["param_string"],
    #                "filter": filter,
    #                "random_item": random_item})


def get_by_filter(request):
    context = {}
    filter = request.GET.get('filter', 'in_progress')

    innering = inner_filtering(request, "1", filter)

    contests_html = render_to_string("includes/home/contest_list.html", context={
        "request": request,
        "contests": innering["contests"],
        "param_string": innering["param_string"]
    })

    context.update({"contests_html": contests_html})
    return JsonResponse(context)


@login_required(login_url="user:login")
def contest(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    if contest.user != request.user:
        try:
            if contest.form_fields["is_private"]:
                if not NDASigners.objects.filter(user=request.user,
                                                 contest=contest).exists():
                    if contest.status != "completed":
                        return redirect("home:nda", contest_id)
        except KeyError:
            pass

    feedbacks = Feedback.objects.filter(entry__contest_id=contest.id)

    if contest.round != "winner_selected":
        check_rounds(request, contest)

    form = WorkForm(request.POST or None)
    entries = contest.entries.all().order_by("-created_date")
    return render(request, "home/contest.html",
                  context={"contest": contest, "form": form, "entries": entries,
                           "feedbacks": feedbacks})


@login_required(login_url="user:login")
def find_a_designer(request):
    services = SubCategory.objects.all()
    industries = [' Accounting', 'Automotive', 'Beauty', 'Construction', 'Consulting',
                  'Dental', 'Education',
                  'Entertainment', 'Events', 'Financial', 'Home & Garden',
                  'Insurance', 'Internet', 'Legal', 'Manufacturing & Wholesale',
                  'Media', 'Medical', 'Miscellaneous',
                  'Natural Resources', 'Non-Profit',
                  'Real Estate', 'Religious', 'Restaurant', 'Retail',
                  'Service Industries', 'Sport', 'Technology',
                  'Travel & Hospitality']
    languages = settings.LANGUAGES
    logo_designers = User.objects.filter(profile__role="designer",
                                         tags__service__title="Logo Design")
    web_designers = User.objects.filter(profile__role="designer",
                                        tags__service__title="Web Page Design")
    online_designers = User.objects.filter(
        profile__last_activity__gt=timezone.now() - timedelta(minutes=1),
        profile__role="designer")

    q = request.GET.get("q", None)
    srv = request.GET.getlist("srv", None)
    ind = request.GET.getlist("ind", None)
    lang = request.GET.get("lang", None)
    online = request.GET.get("online", None)
    designers = User.objects.filter(profile__role="designer")
    context = {"services": services, "industries": industries,
               "languages": languages, "logo_designers": logo_designers,
               "logo_id": SubCategory.objects.get(title="Logo Design"),
               "web_id": SubCategory.objects.get(title="Web Page Design"),
               "web_designers": web_designers, "online_designers": online_designers
               }
    if q or srv or ind or lang or online:
        context.update({"query": True})
    if q:
        designers = designers.filter(
            Q(username__icontains=q) | Q(username__icontains=q))
        context.update({"q": q})
    if srv:
        designers = designers.filter(tags__service_id__in=srv)
        context.update({"srv": srv})
    if ind:
        designers = designers.filter(
            works__contest__form_fields__contest_industry__in=ind)
        context.update({"ind": ind})
    if lang:
        designers = designers.filter(Q(profile__languages__contains=lang))
        context.update({"lang": lang})
    if online:
        designers = designers.filter(
            profile__last_activity__gt=timezone.now() - timedelta(minutes=1))
        context.update({"online": "online"})
    context.update({"designers": set(designers)})
    return render(request, "home/find_a_designer.html", context=context)


@login_required(login_url="user:login")
def discover(request):
    entries = Work.get_showables().order_by("-last_activity",
                                            "-user__profile__last_activity")

    industry = request.GET.get("industry", None)
    service = request.GET.get("service", None)
    if industry and service:
        entries = entries.filter(contest__category_id=service,
                                 contest__form_fields__contest_industry=industry)
    elif industry:
        entries = entries.filter(contest__form_fields__contest_industry=industry)
    elif service:
        entries = entries.filter(contest__category_id=service)

    page = request.GET.get('page', 1)
    paginator = Paginator(entries, 10)
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    services = SubCategory.objects.all()

    return render(request, "home/discover.html",
                  context={"entries": entries, "services": services})


def nda(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    if request.method == "POST":
        NDASigners.objects.create(user=request.user, contest=contest)
        return redirect("home:contest", contest.id)
    return render(request, "home/nda.html")


def entry_detail(request, contest_id, entry_id):
    entry = Work.objects.get(id=entry_id, contest_id=contest_id)
    entry.last_activity = timezone.now()
    entry.save()
    context = {"entry": entry}
    alert = request.GET.get("alert")
    if request.method == "POST":
        rate = request.POST.get('rate')
        review = request.POST.get('review')
        r = Review.objects.create(content=review, entry=entry, rate=int(rate),
                                  user=entry.user,
                                  writer=entry.contest.user)
        context.update({"r": r})
    else:
        r = Review.objects.filter(user=entry.user, entry=entry,
                                  writer=entry.contest.user)
        if r.exists():
            context.update({"r": r.first()})
    if alert == "eliminated" and request.user == entry.user and entry.is_declined:
        context.update({"eliminated": True})

    return render(request, "home/entry_detail.html", context)


def delete_review(request, id):
    review = Review.objects.get(id=id)
    entry = Work.objects.get(id=review.entry.id)
    review.delete()

    return redirect("home:entry_detail", entry.contest.id, entry.id)


def add_comment(request, contest_id, entry_id):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    entry = Work.objects.get(id=entry_id, contest_id=contest_id)

    if body["typ"] == "main":
        f = Feedback.objects.create(entry_id=entry_id, user=request.user,
                                    content=body["content"])
        Notification.objects.create(user=entry.user, notify_type="F", entry=entry,
                                    feedback=f)

    else:
        f = Feedback.objects.create(entry_id=entry_id, user=request.user,
                                    content=body["content"],
                                    parent_id=int(body["for_what"]))
        if f.user == f.parent.user:
            Notification.objects.create(user=entry.user, notify_type="F", entry=entry,
                                        feedback=f)
        else:
            Notification.objects.create(user=entry.contest.user, notify_type="FR",
                                        entry=entry, feedback=f)

    comment_list = render_to_string("includes/contest/comment_list.html", context={
        "entry": entry
    }, request=request)
    return JsonResponse({"comment_list": comment_list})


def delete_comment(request, comment_id):
    feedback = Feedback.objects.get(id=comment_id)
    entry = Work.objects.get(id=feedback.entry.id)

    feedback.delete()

    comment_list = render_to_string("includes/contest/comment_list.html", context={
        "request": request,
        "entry": entry
    })

    return JsonResponse({"comment_list": comment_list})


def edit_comment(request, comment_id):
    feedback = Feedback.objects.get(id=comment_id)
    entry = Work.objects.get(id=feedback.entry.id)

    if feedback.is_editable():

        content = request.POST.get('content')
        feedback.content = content
        feedback.save()
    else:
        messages.warning(request,
                         "Sorry. Feedbacks can only be edited within 3 minutes from the time they are first published.")

    return redirect("home:entry_detail", entry.contest.id, entry.id)


def apply_filters(request, contest_id):
    body = dict(request.GET)
    context = {}
    qs = Work.objects.filter(contest_id=contest_id)

    body_designer = body["designer_select"][0]

    designer = False if body_designer == "All Designers" else True

    if designer:
        qs = qs.filter(user__username=body_designer)

    if "order_select" in body:
        temp = body["order_select"][0]

        if temp.split("_")[0] == "old":
            if temp.split("_")[1] == "1":
                qs = qs.order_by("created_date")
            else:
                qs = qs.order_by("-created_date")

        if temp.split("_")[0] == "rate":
            if temp.split("_")[1] == "0":
                qs = qs.order_by("-rate")
            else:
                qs = qs.order_by("rate")

    entries_html = render_to_string("includes/contest/entries_tab.html", context={
        "request": request,
        "entries": qs,
        "contest": Contest.objects.get(id=contest_id)
    })

    context.update({"entries_html": entries_html})
    return JsonResponse(context)


def notifications(request):
    return render(request, "home/notifications.html")


def read_notifications(request):
    notis = request.user.notifications.filter(is_unread=True)
    for noti in notis:
        noti.is_unread = False
        noti.save()
    return JsonResponse({"okundu mu?": "okundu"})


@login_required(login_url="user:login")
def check_notifications(request):
    noti_count = Notification.objects.filter(user=request.user, is_unread=True).count()
    return JsonResponse({"noti_count": noti_count})


def get_nots_list(request):
    notis_html = render_to_string("includes/home/notify_list_included.html",
                                  request=request)
    return JsonResponse({"notis_html": notis_html})


def submit_request(request):
    if request.user.is_authenticated:
        form = RequestForm(request.POST or None, request.FILES or None)
    else:
        form = AnonUserRequestForm(request.POST or None, request.FILES or None)

    if form.is_valid():

        if request.user.is_authenticated:
            contact = form.save(commit=False)
            contact.user = request.user
            contact.role = request.user.profile.role
            contact.email = request.user.email
            contact.save()
            messages.success(request, "Your request has reached us successfully")
        else:
            contact = form.save(commit=False)

            contact.save()
            messages.success(request, "Your request has reached us successfully")

        message_html = render_to_string("email/contact.html", {"contact": contact})
        message = render_to_string("email/contact.txt", {"contact": contact})

        send_mail(subject="Your Request", message=message, html_message=message_html,
                  from_email='testmest5398@gmail.com',
                  recipient_list=[str(contact.email)], fail_silently=False)

        return redirect("home:index")

    return render(request, "home/submit_request.html", {"form": form})


def terms(request):
    document = InformationPage.objects.get(name="terms_of_use")
    return render(request, "home/terms.html", {"document": document})


def privacy(request):
    document = InformationPage.objects.get(name="privacy_policy")
    ats = Attachment.objects.last()
    return render(request, "home/privacy.html", {"document": document, "ats": ats})


def refferal_link(request, link):
    if request.user.is_authenticated:
        try:
            user = force_text(urlsafe_base64_decode(link))
            return redirect("home:index")
        except:
            return HttpResponse("Bad Link")
    else:
        messages.info(request,
                      "You need to be registered to benefit from the reference. If you leave the page without registering, the link will be invalidated. The fee discount provided by the referral link is valid for clients.")
        response = redirect("user:register")
        response['Location'] += f'?ref={link}'
        return response


def wallet(request):
    return render(request, "home/wallet.html")


def create_payout_request(request, user):
    user = User.objects.get(username=user)
    if request.method == "POST":
        amount = request.POST.get("request-inp")
        PayoutRequest.objects.create(user=user, amount=request.POST.get("request-inp"))
        user.wallet.balance -= int(amount)
        user.wallet.save()
    messages.success(request,
                     "Your payment request has been successfully received. We'll contact you")
    return redirect("home:wallet")


def serve_protected_document(request, file):
    document = get_object_or_404(Contact, file="requests/" + file)
    if request.user.is_superuser or document.user == request.user:
        response = FileResponse(document.file, )
        return response

    else:
        return HttpResponse(status=403)


def serve_protected_entry(request, file):
    entry = get_object_or_404(Work, image="works/" + file)
    stat = entry.contest.form_fields.get("is_hidden", False)
    response = FileResponse(entry.image, )
    if stat:
        if entry.user == request.user or entry.contest.user == request.user:
            return response
        if entry.contest.round == "winner_selected":
            return response

        return FileResponse(open("static/dashboard/images/hidden_design.png", 'rb'))
    else:
        return response


def serve_protected_entry_display(request, file):
    entry = get_object_or_404(Work, display_image="works/display/" + file)
    stat = entry.contest.form_fields.get("is_hidden", False)
    response = FileResponse(entry.display_image, )
    print("handled")
    if stat:
        if entry.user == request.user or entry.contest.user == request.user:
            return response
        if entry.contest.round == "winner_selected":
            return response

        return FileResponse(open("static/dashboard/images/hidden_design.png", 'rb'))
    else:
        return response
