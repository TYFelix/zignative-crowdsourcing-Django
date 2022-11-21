import base64
import json
from django.conf import settings
from django.contrib.auth import authenticate, login as login_user, update_session_auth_hash, logout as logout_user
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail

from customer.models import SubCategory, Finalist, Contest
from designer.models import NDASigners, Work, Review
from home.models import InformationPage
from .forms import RegisterForm, LoginForm, PasswordResetForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile, Referral, PortfolioObject, ProfileTag
from .tokens import PasswordResetToken, password_reset_token, AccountVerificationToken


# USER VIEWS
def base64_to_image(data, user):
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]

    data = ContentFile(base64.b64decode(imgstr), name='user_cover_{}.'.format(user.username) + ext)
    return data


def logout(request):
    logout_user(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("home:index")


def login(request):
    form = LoginForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                if user.profile.is_verified:
                    login_user(request, user)
                    messages.success(request, "You have successfully logged in.")
                    next = request.GET.get("next",None)
                    if next:
                        return redirect(next)
                    if user.profile.role == "client":
                        return redirect("customer:index")
                    else:
                        return redirect("designer:index")
                else:
                    messages.warning(request, "You haven't verified your account yet. Please check your email.")

    return render(request, "user/login.html", {"form": form})


def register(request):
    form = RegisterForm(request.POST or None)
    # terms = InformationPage.objects.get(name="terms_of_use")
    if form.is_valid():
        ## User creation
        user = form.save(commit=True)

        ## Profile creation
        role = request.POST.get("radios")
        Profile.objects.create(user=user, role=role)
        send_verify_mail(user=user, request=request)
        ref = request.GET.get("ref", None)
        if ref:
            referral = force_text(urlsafe_base64_decode(ref))
            referral_user = User.objects.get(username=referral)
            Referral.objects.create(referred=user, referrer=referral_user)
            messages.info(request, "The referral link has been processed to your account")
        messages.success(request,
                         "To log in, you must confirm your account. We've sent a confirmation link to your email.")

        return redirect("user:login")
    return render(request, "user/register.html", {"form": form})
    # return render(request, "user/register.html", {"form": form, "terms": terms})


def send_verify_mail(user, request):
    ### Creating  Token
    account_verification_token = AccountVerificationToken()
    token = account_verification_token.make_token(user)

    ### Username base64 encode
    base64 = urlsafe_base64_encode(force_bytes(user.username))

    hostname = request.get_host()

    ### Mail content with verification link
    verify_link = "{}/members/account_verify/{}/{}".format(hostname, base64, token)
    message_html = render_to_string("email/verify.html", {"verify_link": verify_link})
    message = render_to_string("email/verify.txt", {"verify_link": verify_link})

    print(verify_link)
    send_mail(subject="Verify your account", message=message, html_message=message_html,
              from_email='testmest5398@gmail.com',
              recipient_list=[str(user.email)], fail_silently=False)


def account_verify(request, base64, token):
    account_verification_token = AccountVerificationToken()

    try:
        decoded_base64 = force_text(urlsafe_base64_decode(base64))
        user = User.objects.get(username=decoded_base64)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_verification_token.check_token(user, token):
        messages.success(request, "Perfect! Your account has been confirmed. You can now login.")
        user.profile.is_verified = True
        user.profile.save()
        return redirect("user:login")
    else:
        return HttpResponse("This link has expired. ")


def forgot_password(request):
    if request.method == "POST":

        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)

            ### Creating Reset Token
            password_reset_token = PasswordResetToken()
            token = password_reset_token.make_token(user)

            ### Username base64 encode
            base64 = urlsafe_base64_encode(force_bytes(user.username))

            hostname = request.get_host()

            ### Mail content with reset link
            message = "Click the link below to reset your password \n {}/members/reset_password/{}/{}".format(hostname,
                                                                                                              base64,
                                                                                                              token)

            send_mail(subject="Reset Password", message=message, from_email='testmest5398@gmail.com',
                      recipient_list=[str(email)])
            messages.success(request, "Perfect! You can check your email now.")
        except User.DoesNotExist:
            messages.error(request, "Sorry, That email address is not registered.")
        return render(request, "user/forgot_password.html", context={"done": True, "title": "Email Sent"})

    return render(request, "user/forgot_password.html", context={"done": False, "title": "Reset Password"})


def reset_password(request, base64, token):
    try:
        decoded_base64 = force_text(urlsafe_base64_decode(base64))
        user = User.objects.get(username=decoded_base64)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    form = PasswordResetForm(user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # Important!
        messages.success(request, 'Your password was successfully updated! You can login now.')
        return redirect("user:login")
    if user is not None and password_reset_token.check_token(user, token):
        return render(request, "user/reset_password.html", {"form": form})
    else:
        return HttpResponse("This link has expired. ")


def account(request):
    user = request.user
    domain = settings.DOMAIN
    works = PortfolioObject.objects.filter(user=request.user)
    return render(request, "user/account.html", context={"user": user, "domain": domain, "works": works})


def public_profile(request, username):
    username = username.lower()

    q = request.GET.get('service', "0")

    user = User.objects.get(username__iexact=username)
    if user.profile.role == "client":
        reviews = Review.objects.filter(writer=user).count()
        awards = Finalist.objects.filter(is_winner=True, contest__user=user).count()
        countest_count = Contest.objects.filter(user=user, is_paid=True, is_draft=False).count()
        total = 0
        for contest in user.contests.filter(is_paid=True):
            total+=contest.get_total_price()

        return render(request, "user/public_client_profile.html",
                      {"countest_count": countest_count, "reviews": reviews, "awards": awards, "user": user,"total":total})

    services = SubCategory.objects.all()
    if q and q != "0":
        works = PortfolioObject.objects.filter(user=user, entry__contest__category_id=q)
    else:
        works = PortfolioObject.objects.filter(user=user)

    contests = Contest.objects.filter(is_paid=True,is_draft=False,round="qualify",user=user,is_locked=False)
    return render(request, "user/public_profile.html",
                  {"user": user, "works": works, "services": services, "q": int(q),"contests":contests})


def profile_about(request, username):
    username = username.lower()
    user = User.objects.get(username__iexact=username)
    average = user.reviews.aggregate(Avg("rate"))['rate__avg']
    if average:
        average_int = int(average * 2) / 2
    else:
        average_int = 0

    contests_won = Finalist.objects.filter(entry__user=user, is_winner=True).count()
    runner_up_queryset = Finalist.objects.filter(entry__user=user, is_winner=False)
    runner_up = len(set([f.entry.contest for f in runner_up_queryset]))
    total = 0

    for work in Finalist.objects.filter(entry__user=user, is_winner=True):
        total += work.contest.get_prize()

    for work in Finalist.objects.filter(entry__user=user, is_winner=False):
        if work.contest.get_shared_prize():
            total += work.contest.get_shared_prize()

    for work in user.works.filter(user=user, is_declined=False, is_deleted=False):
        if work.contest.get_shared_prize() and work.contest.round == "qualify_end":
            total += work.contest.get_shared_prize()

    contests = Contest.objects.filter(is_paid=True,is_draft=False,round="qualify",user=request.user,is_locked=False)

    return render(request, "user/profile_about.html",
                  {"user": user, "contests_won": contests_won, "runner_up": runner_up,"contests":contests, "average": average, "total":total,
                   "average_int": average_int})


def edit_profile(request):
    u_form = UserUpdateForm(request.user, request.POST or None, instance=request.user)
    p_form = ProfileUpdateForm(request.user, request.POST or None, request.FILES or None, instance=request.user.profile)
    services = SubCategory.objects.all()
    if u_form.is_valid() and p_form.is_valid():
        u_form.save(commit=True)
        p_form.save(commit=True)
        tags = request.POST.getlist('tags', None)
        if tags:
            ProfileTag.objects.filter(user=request.user).delete()
            for tag in tags:
                ProfileTag.objects.create(user=request.user, service_id=int(tag))
        messages.success(request, "The information has been successfully saved")

        return redirect("user:account")

    return render(request, "user/edit_profile.html", context={"u_form": u_form, "p_form": p_form, "services": services})


def set_portfolio(request):
    works = Work.objects.filter(user=request.user)
    port_objects = PortfolioObject.objects.filter(user=request.user)
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        selected = body["selected"]
        selected = selected.replace("[", "").replace("]", "").replace("\"", "").split(",")
        PortfolioObject.objects.filter(user=request.user).delete()
        if selected != ['']:
            for select in selected:
                PortfolioObject.objects.create(entry_id=select, user=request.user)
        return JsonResponse({"message": "succesful"})
    return render(request, "user/set_portfolio.html", {"works": works, "port_objects": port_objects})


def upload_cover(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    base64_image = body["image"]
    image = base64_to_image(base64_image, request.user)
    request.user.profile.cover_photo = image
    request.user.profile.save()
    return JsonResponse({"message": "succesful"})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user:account')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/change_password.html', {
        'form': form
    })


def signed_ndas(request):
    ndas = NDASigners.objects.filter(user=request.user)
    return render(request, "user/signed_ndas.html", {"ndas": ndas})

def remove_or_add_portfolio(request,entry):
    entry = Work.objects.get(id=entry)
    if entry.in_portfolio():
        PortfolioObject.objects.filter(entry_id=entry.id).delete()
        messages.success(request,"Successfully added to your portfolio")
    else:
        PortfolioObject.objects.create(entry_id=entry.id,user=request.user)
        messages.success(request,"Successfully removed from your portfolio")

    return redirect("home:entry_detail",entry.contest.id,entry.id)
