import base64
import json

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.base import ContentFile
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from . import contest_views
# Create your views here.
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from customer.models import Contest, MainCategory, SubCategory, Prices, Finalist, Announcement, Invoice, Attachment, \
    Discount, DiscountEvent, Poll, PollObject, PollComment
from designer.models import Work
from datetime import timedelta

from designer.views import inner_filtering
from home.models import Notification, Invite
from user.models import Earning, Wallet, ProfileTag
from .forms import PollForm

stripe.api_key = settings.STRIPE_SECRET_KEY


def base64_to_image(data,contest_id,user):
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]

    data = ContentFile(base64.b64decode(imgstr), name='{}_{}.'.format(contest_id,user.username) + ext)  # You can save this as file instance.
    return data

def clear_temp_contests(user):
    user.contests.filter(is_temp=True).delete()


@login_required(login_url="user:login")
def index(request):
    clear_temp_contests(request.user)
    contests = Contest.objects.filter(user=request.user).order_by("-created_date")
    context = {
        "contests": contests
    }
    return render(request, "customer/index.html", context=context)


@login_required(login_url="user:login")
def categories(request):
    main_categories = MainCategory.objects.all()

    context = {
        "main_categories": main_categories
    }

    return render(request, "customer/categories.html", context=context)

@login_required(login_url="user:login")
def create_contest(request,id):
    category = SubCategory.objects.get(id=id)
    contest = Contest.objects.create(user=request.user, title="{}'s contest".format(request.user), category=category)
    return redirect("customer:contest_step", contest.id, "step_1")

@login_required(login_url="user:login")
def teams(request):
    return render(request,"customer/teams.html")
@login_required(login_url="user:login")
def contest_step(request,contest,step):
    contest = Contest.objects.get(id=contest)
    if contest.category.template_name == "logo-design":return contest_views.logo_contest_step(request, contest.id, step)
    elif contest.category.template_name == "business-card-design":return contest_views.bc_contest_step(request,contest.id,step)
    elif contest.category.template_name == "web-page-design":return contest_views.wp_contest_step(request,contest.id,step)
    elif contest.category.template_name == "banner-ad-design":return contest_views.ba_contest_step(request,contest.id,step)
    elif contest.category.template_name == "email-template-design":return contest_views.et_contest_step(request,contest.id,step)
    elif contest.category.template_name == "social-media-assets-design":return contest_views.sm_contest_step(request,contest.id,step)
    elif contest.category.template_name == "company-product-name":return contest_views.cn_contest_step(request,contest.id,step)
    elif contest.category.template_name == "mobile-app-design":return contest_views.ma_contest_step(request,contest.id,step)
    elif contest.category.template_name == "landing-page-design":return contest_views.lp_contest_step(request,contest.id,step)
    elif contest.category.template_name == "t-shirt-design":return contest_views.td_contest_step(request,contest.id,step)
    elif contest.category.template_name == "merchandise-design":return contest_views.md_contest_step(request,contest.id,step)
    elif contest.category.template_name == "book-cover-design":return contest_views.bkc_contest_step(request,contest.id,step)
    elif contest.category.template_name == "magazine-cover-design":return contest_views.mgc_contest_step(request,contest.id,step)
    elif contest.category.template_name == "wordpress-design":return contest_views.wpd_contest_step(request,contest.id,step)


@login_required(login_url="user:login")
def draft_contest(request, contest):
    cont = Contest.objects.get(id=contest)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['contest']

    cont.title = content["contest_title"]
    cont.form_fields = content
    cont.is_temp = False

    if "price_plan" in content:
        cont.form_fields["price"] = str(Prices.objects.get(id=content["price_plan"]).price)

    cont.save()

    return JsonResponse({"cevap": "Success"})


@login_required(login_url="user:login")
def submit_contest(request, contest):
    cont = Contest.objects.get(id=contest)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['contest']

    cont.title = content["contest_title"]
    cont.form_fields = content
    cont.is_draft = False
    cont.is_temp = False
    cont.save()

    content = "Contest created by {}".format(request.user)
    Announcement.objects.create(contest=cont, content=content)

    return JsonResponse({"success": True})


@login_required(login_url="user:login")
def start_poll(request,contest):
    if request.user.profile.role != "client":return redirect("home:index")

    contest = Contest.objects.get(id=contest)
    works = Work.objects.filter(contest_id=contest.id)
    context = {"contest":contest,"works":works,"range":range(8)}
    form = PollForm(request.POST or None)

    if form.is_valid():
        poll_object_list = request.POST.get("poll_objects",None).split(',')

        poll = form.save(commit=False)
        poll.contest = contest
        poll.save()
        if poll_object_list:
            for obj in poll_object_list:
                PollObject.objects.create(poll_id=poll.id,entry_id=int(obj))

        response = redirect("home:contest", contest.id)
        response['Location'] += '?tab=polls'
        messages.success(request,"Poll successfully created.")
        return response

    return render(request, "customer/poll_steps/start_poll.html", context=context)

@login_required(login_url="user:login")
def edit_poll(request,poll):
    if request.user.profile.role != "client":return redirect("home:index")

    poll = Poll.objects.get(id=poll)
    contest = Contest.objects.get(id=poll.contest.id)
    works = Work.objects.filter(contest_id=contest.id)
    context = {"contest":contest,"poll":poll,"works":works,"range":range(8)}
    form = PollForm(request.POST or None,instance=poll)
    if form.is_valid():
        poll_object_list = request.POST.get("poll_objects",None).split(',')

        poll = form.save(commit=False)
        poll.contest = contest
        poll.save()
        if poll_object_list:
            PollObject.objects.filter(poll_id=poll.id).delete()
            for obj in poll_object_list:
                PollObject.objects.create(poll_id=poll.id,entry_id=int(obj))

        response = redirect("home:contest", contest.id)
        response['Location'] += '?tab=polls'
        messages.success(request,"Changes saved successfully")
        return response


    return render(request, "customer/poll_steps/edit/edit_poll.html", context=context)

@login_required(login_url="user:login")
def poll_detail(request, poll):
    if request.user.profile.role != "client":return redirect("home:index")
    poll = Poll.objects.get(uid=poll)
    contest = Contest.objects.get(id=poll.contest.id)
    domain = settings.DOMAIN
    return render(request,"customer/poll_detail.html",{"poll":poll,"contest":contest,"range":range(5),"domain":domain})

@login_required(login_url="user:login")
def add_poll_comment(request,poll_obj):
    poll_obj = PollObject.objects.get(id=poll_obj)
    poll = Poll.objects.get(id=poll_obj.poll.id)
    messages.success(request,"Your vote saved successfully")
    if request.method == "POST":
        rate = request.POST.get('rate')
        review = request.POST.get('review')
        PollComment.objects.create(content=review,poll_id=poll.id,rate=rate,  user=request.user,poll_object=poll_obj)
    return redirect("customer:poll_detail",poll.uid)

@login_required(login_url="user:login")
def delete_comment(request,poll_comment):
    p=PollComment.objects.get(id=poll_comment)
    poll = Poll.objects.get(id=p.poll.id)
    p.delete()

    return redirect("customer:poll_detail", poll.uid)

@login_required(login_url="user:login")
def delete_poll(request,poll):
    p=Poll.objects.get(id=poll)
    c=p.contest
    p.delete()
    response = redirect("home:contest", c.id)
    response['Location'] += '?tab=polls'
    messages.success(request, "Poll deleted successfully")
    return response

@login_required(login_url="user:login")
def add_attachment(request,contest):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    base64 = body["img"]
    detail = body["detail"]
    image = base64_to_image(base64, contest, request.user)

    a = Attachment.objects.create(contest_id=contest,content=detail,image=image)

    attachment =  render_to_string("includes/contest/attachment.html", context={
        "attachment": a,
    },request=request)

    return JsonResponse({"attachment":attachment})

@login_required(login_url="user:login")
def delete_attachment(request,attach_id):
    a=Attachment.objects.get(id=attach_id)
    contest=a.contest.id
    a.delete()
    where = request.GET.get("where",None)
    if where:
        return redirect("customer:edit_contest", contest, "step_3")

    return redirect("customer:contest_step",contest,"step_3")

@login_required(login_url="user:login")
def apply_discount(request,contest):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    contest  = Contest.objects.get(id = contest)
    try:
        discount = Discount.objects.get(code=body['code'])


        if timezone.now() < discount.start_time:
            return JsonResponse({"not_yet": True,'start_date':discount.start_time})
        if discount.end_time:
            if timezone.now() > discount.end_time:
                return JsonResponse({"not_found": True})


        if discount.emails.exists():
            if not discount.emails.filter(email=request.user.email).exists():
                return JsonResponse({"not_in": True})

        event_count=DiscountEvent.objects.filter(discount__code=body['code'],contest__user=request.user).count()
        if discount.count <= event_count:
            return JsonResponse({"enough": True})
    except Discount.DoesNotExist:
        return JsonResponse({"not_found":True})


    discount_event = DiscountEvent.objects.create(discount=discount,contest=contest)


    return JsonResponse({"applied":True,"free_private":discount.free_private
                                        ,"free_hidden":discount.free_hidden
                                        ,"modify_fee":discount_event.contest.discount()["percentage"]})


@login_required(login_url="user:login")
def browse_contests(request):
    # contests=Contest.objects.filter(is_draft=False,is_temp=False,is_paid=True).exclude(status="canceled").order_by("-created_date")
    services = SubCategory.objects.all()
    page = request.GET.get('page', 1)
    filter = request.GET.get('filter', 'in_progress')
    innering = inner_filtering(request, page, filter)
    return render(request, "designer/browse_contests.html", context={"contests": innering["contests"],
                                                                     "services": services,
                                                                     "param_string": innering["param_string"],
                                                                     "filter": filter})


@login_required(login_url="user:login")
def decline_entry(request, contest, entry):
    ent = Work.objects.get(id=entry, contest_id=contest)
    if ent.is_declined:
        ent.is_declined = False
    else:
        Notification.objects.create(user=ent.user, notify_type="D", entry=ent)

        ent.is_declined = True
    ent.save()
    cont = Contest.objects.get(id=contest)
    entries_html = render_to_string("includes/contest/contest_entries.html", context={
        "request": request,
        "contest": cont
    })
    context = {
        "all_count": cont.entries.all().count(),
        "active_count": cont.entries.filter(is_declined=False).count(),
        "rated_count": cont.entries.filter(rate__gt=0).count(),
        "declined_count": cont.entries.filter(is_declined=True).count(),
        "entries_html": entries_html

    }
    return JsonResponse(context)


def notify_all_designers(contest, round):
    entries = contest.entries.all()
    users = []
    for entry in entries:
        users.append(entry.user)
    users = list(set(users))

    for user in users:
        Notification.objects.create(user=user, contest=contest, contest_round=round, notify_type="R")


@login_required(login_url="user:login")
def confirm_finalists(request, contest_id):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    finalists = body['finalists']

    contest = Contest.objects.get(id=contest_id)

    for finalist in finalists:
        f=Finalist.objects.create(contest_id=contest_id, entry_id=finalist)
        if not ProfileTag.objects.filter(user=f.entry.user,service=f.entry.contest.category).exists():
            ProfileTag.objects.create(user=f.entry.user, service=f.entry.contest.category)
    for entry in contest.entries.all():
        if str(entry.id) not in finalists:
            entry.is_declined = True
            entry.save()
    contest.finish_date = timezone.now()
    contest.finish_date = contest.finish_date + timedelta(days=3)
    contest.round = "final_round"
    contest.is_locked = False
    contest.save()
    Announcement.objects.create(contest=contest, content="The client has selected finalists.")
    notify_all_designers(contest, "final_round")
    return JsonResponse({"hello": str(finalists)})


def confirm_winner(request, contest_id):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    winner = body['winner']
    entry = Finalist.objects.filter(entry__contest_id=contest_id, entry_id=winner).first()
    entry.is_winner = True
    entry.save()

    contest = Contest.objects.get(id=contest_id)
    contest.round = "winner_selected"
    contest.is_locked = False
    contest.save()

    Announcement.objects.create(contest=contest, content="The client has awarded a winner!")
    notify_all_designers(contest, "winner_selected")
    try :
        if request.user.referal:
            referal = request.user.referal
            e=Earning.objects.create(contest= contest, user = referal.referrer)

            wallet = Wallet.objects.filter(user=referal.referrer)
            if not wallet.exists():
                wallet = Wallet.objects.create(user=referal.referrer)
            else:wallet=wallet.first()
            wallet.balance += e.get_earning()
            wallet.save()
    except:pass
    return JsonResponse({"winner": str(winner)})


def split_prize(request, contest):
    contest = Contest.objects.get(id=contest)
    contest.status = "completed"
    contest.save()
    users = set([finalist.entry.user for finalist in contest.finalists.all()])
    for user in users:
        Notification.objects.create(user=user, contest=contest, notify_type="R")
    Notification.objects.create(user=contest.user, contest=contest, notify_type="R")
    Announcement.objects.create(contest=contest,
                                content="The prize was shared among the finalists. Because the client didn't choose a winner.")
    where = request.GET.get("on", "contest")

    if where == "admin":
        messages.success(request, "Your transaction has been completed successfully")
        return redirect("/admin/customer/contest/")
    return redirect("home:contest", contest.id)


def split_prize_to_designers(request, contest):
    contest = Contest.objects.get(id=contest)
    contest.status = "completed"
    contest.save()
    entries = contest.entries.filter(is_declined=False)
    users = []
    for entry in entries:
        users.append(entry.user)
    users = list(set(users))

    for user in users:
        Notification.objects.create(user=user, contest=contest, notify_type="R")

    Notification.objects.create(user=contest.user, contest=contest, notify_type="R")

    Announcement.objects.create(contest=contest,
                                content="The prize was shared among the designers. Because the client didn't choose any finalist.")
    where = request.GET.get("on", "contest")
    if where == "admin":
        messages.success(request, "Your transaction has been completed successfully")
        return redirect("/admin/customer/contest/")

    return redirect("home:contest", contest.id)


def add_anouncement(request, contest_id):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    contest = Contest.objects.get(id=contest_id)
    Announcement.objects.create(contest=contest, content=body["content"], is_general=False)

    anouns_list = render_to_string("includes/contest/anouns_list.html", context={
        "request": request,
        "contest": contest
    })
    entries = contest.entries.all()
    users = []
    for entry in entries:
        users.append(entry.user)
    users = list(set(users))

    for user in users:
        Notification.objects.create(user=user, contest=contest, notify_type="A")

    return JsonResponse({"anouns_list": anouns_list})


def delete_announcement(request, anouns_id):
    anouns = Announcement.objects.get(id=anouns_id)
    contest = anouns.contest
    anouns.delete()

    anouns_list = render_to_string("includes/contest/anouns_list.html", context={
        "request": request,
        "contest": contest
    })
    return JsonResponse({"anouns_list": anouns_list})

@login_required(login_url="user:login")
def invite_designer(request,user,contest):
    user = User.objects.get(username=user)
    contest = Contest.objects.get(id=contest)
    i=Invite.objects.create(client=request.user,designer=user,contest=contest)
    Notification.objects.create(user=user,invite=i,contest=contest,notify_type="IV")
    return JsonResponse({"success":"success"})


@login_required(login_url="user:login")
def rate_entry(request, contest, entry):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        rate = body['rate']
        work = Work.objects.get(id=entry, contest_id=contest)
        work.last_activity = timezone.now()
        work.rate = rate
        work.save()

        Notification.objects.create(user=work.user, entry=work, notify_type="RT")

    return JsonResponse({"hello": rate})


@login_required(login_url="user:login")
def invoice(request, invoice):

    invoice = get_object_or_404(Invoice,id = invoice)
    if request.user != invoice.user:
        return redirect("customer:index")
    total = invoice.contest.get_price().price

    try:
        if invoice.contest.form_fields["is_private"]:
            if  invoice.contest.discount().get("discount",None):
                if invoice.contest.discountevents.first().discount.free_private:
                    pass
            else:
                total += 50
    except KeyError: pass

    try:
        if invoice.contest.form_fields["is_hidden"]:
            if invoice.contest.discount().get("discount", None):
                if invoice.contest.discountevents.first().discount.free_hidden:
                    pass
            else:
                total += 59
    except KeyError: pass

    total += invoice.contest.get_transaction_fee().get("last")

    return render(request, "customer/invoice.html", context={"jsonfield": invoice.json, "total":total, "invoice":invoice})


def check_out_session(request, pk):
    contest = Contest.objects.get(id=pk)
    price = contest.get_total_price()
    billing_info = json.loads(request.body.decode("utf-8"))
    YOUR_DOMAIN = settings.DOMAIN
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {

                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(price) * 100,
                    'product_data': {
                        'name': contest.category.title + " Contest",
                        'images': [
                            'https://cdn.wallpapersafari.com/2/42/UI1DrK.jpg',
                        ],
                    },
                },
                'quantity': 1,
            },
        ],
        metadata={
            "product_id": contest.id,
            "user": request.user.username,
            "billing_info":json.dumps(billing_info, indent = 4)
        },
        mode='payment',
        customer_email=f'{request.user.email}',
        success_url=YOUR_DOMAIN + '/payment/success/',
        cancel_url=YOUR_DOMAIN + f'/payment/cancel/{contest.id}',
    )
    return JsonResponse({
        'id': checkout_session.id
    })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event["type"] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        contest_id = session["metadata"]["product_id"]
        user = session["metadata"]["user"]
        billing_info = session["metadata"]["billing_info"]
        contest = Contest.objects.get(id=contest_id)
        contest.is_paid = True
        contest.is_draft = False
        contest.save()

        send_mail(
            subject="Congratulations",
            message=f"Thanks for your purchase, your payment has been successfully received",
            recipient_list=[customer_email],
            from_email="testmest5398@gmail.com"
        )
        if settings.MODE == "production":
            connection = mail.get_connection()
            connection.open()
            messages = list()
            users = User.objects.filter(profile__role="designer").exclude(username=request.user)
            user_emails = [user.email for user in users]
            domain = settings.DOMAIN
            message_html = render_to_string("email/contest.html", {"contest": contest, "domain": domain})
            message = render_to_string("email/verify.txt", {"verify_link": "verify_link"})

            for email in user_emails:
                msg = EmailMultiAlternatives("Zignative Crowsourcing", message, settings.SERVER_EMAIL, [email])
                msg.attach_alternative(message_html, "text/html")
                messages.append(msg)

            connection.send_messages(messages)
            connection.close()
        billing_info = json.loads(billing_info)
        try:

            contest.invoice.delete()
        except :
            pass

        invoice = Invoice.objects.create(user=contest.user, contest=contest, billing_json=billing_info)

        handle_invoice(invoice,contest)

    return HttpResponse(status=200)


@csrf_exempt
def payment_succesful(request):
    messages.success(request, "Your payment has been successfully received")

    return redirect("customer:index")


def payment_canceled(request, contest):
    messages.error(request, "Payment canceled")
    return redirect("customer:contest_step", contest, "step_5")


def send_celery_mail(request):
    print(settings.MODE == "development")
    return redirect("customer:index")


def handle_invoice(invoice,contest):
    counter = 1
    jsonfield = {
        f"{counter}": {
            "title": f"{contest.category} Contest - {contest.get_price().title} Plan",
            "detail": f"{contest.category} Contest  - {contest.get_price().title} Plan",
            "subtotal": f"{contest.get_price().price}",

        }
    }
    try:
        if contest.form_fields["is_private"]:
            counter += 1
            free = False
            if contest.discount().get("discount",None):
                if contest.discountevents.first().discount.free_private:
                    free = True
            jsonfield.update({
                f"{counter}": {
                    "title": "Private Contest",
                    "detail": "Hide your contest from Google and competitors. Only registered designers will see your "
                              "contest. Designers must agree with the NDA.",
                    "subtotal": f"50.0",
                    "free":free
                }

            })
    except KeyError:
        pass

    try:
        if contest.form_fields["is_hidden"]:
            counter += 1
            free = False
            if contest.discount().get("discount", None):
                if contest.discountevents.first().discount.free_private:
                    free = True
            jsonfield.update({
                f"{counter}": {
                    "title": "Hidden Contest",
                    "detail": "Hide designs from other designs. ",
                    "subtotal": f"59.0",
                    "free":free,
                }

            })


    except KeyError:
        pass
    counter += 1
    jsonfield.update({
        f"{counter}": {
            "title": "Transaction Fee",
            "detail": "",
            "subtotal": f"{contest.get_transaction_fee().get('last',None)}",
            "free": False,
        }

    })
    invoice.json = jsonfield
    invoice.save()
    n=Notification.objects.create(notify_type="I",user=contest.user,contest=contest,invo=invoice)
    print(n)
