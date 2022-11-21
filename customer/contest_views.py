from django.conf import settings
from django.contrib import messages

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect

from customer.forms import CountryForm
from customer.models import Contest, SubCategory, Attachment, \
    DiscountEvent


def handle_payment_context(contest):
    contest_object = Contest.objects.get(id=contest)
    country_form = CountryForm()
    context = {
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
        "contest_object": contest_object,
        "country_form": country_form
    }

    event = DiscountEvent.objects.filter(contest_id=contest)
    if DiscountEvent.objects.filter(contest_id=contest).exists():
        discount = event.first().discount
        context.update({"is_applied": True, "discount": discount})
    return context


def logo_contest_step(request, contest, step):
    category = SubCategory.objects.filter(template_name="logo-design").first()
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}

    if step == "step_2":
        logo_list = category.logos.all()
        page_num = request.GET.get('page', 1)

        if int(page_num) == 1:
            count = 15
        else:
            count = 15 + ((int(page_num) - 1) * 30)

        paginator = Paginator(logo_list, count)
        try:
            logos = paginator.page(1)

        except PageNotAnInteger:
            logos = paginator.page(1)
        except EmptyPage:
            logos = paginator.page(paginator.num_pages)
        context.update({
            "logos": logos,
            "page_num": int(page_num) + 1
        })
    if step == "step_5":
        country_form = CountryForm()
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            "contest_object": contest_object,
            "country_form": country_form
        })
        event = DiscountEvent.objects.filter(contest_id=contest)
        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})

    if step == "step_3":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_4":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    return render(request, "customer/contest_steps/{}.html".format(step), context=context)


def edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_3":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/contest_steps/edit/{}.html".format(step), context=context)


def bc_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/bc_contest_steps/edit/{}.html".format(step), context=context)


def bc_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        contest_object = Contest.objects.get(id=contest)
        country_form = CountryForm()
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            "contest_object": contest_object,
            "country_form": country_form
        })
        event = DiscountEvent.objects.filter(contest_id=contest)
        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
    return render(request, "customer/bc_contest_steps/{}.html".format(step), context=context)


def wp_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/wp_contest_steps/edit/{}.html".format(step), context=context)


def wp_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
        page_count = contest_object.form_fields.get("web_pages", None)
        if page_count: context.update({"page_price": len(page_count) * 100})
        context.update({"page_count": page_count})
    return render(request, "customer/wp_contest_steps/{}.html".format(step), context=context)


def ba_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/ba_contest_steps/edit/{}.html".format(step), context=context)


def ba_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        contest_object = Contest.objects.get(id=contest)
        country_form = CountryForm()
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            "contest_object": contest_object,
            "country_form": country_form
        })
        event = DiscountEvent.objects.filter(contest_id=contest)
        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})

    return render(request, "customer/ba_contest_steps/{}.html".format(step), context=context)


def et_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/et_contest_steps/{}.html".format(step), context=context)


def et_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/et_contest_steps/edit/{}.html".format(step), context=context)


def delete_contest(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    contest.status = "canceled"
    contest.save()
    messages.success(request, "Contest successfully deleted")

    return redirect("customer:index")


def sm_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/sm_contest_steps/{}.html".format(step), context=context)


def sm_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/sm_contest_steps/edit/{}.html".format(step), context=context)


def cn_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/cn_contest_steps/{}.html".format(step), context=context)


def cn_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/cn_contest_steps/edit/{}.html".format(step), context=context)


def ma_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/ma_contest_steps/{}.html".format(step), context=context)


def ma_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/ma_contest_steps/edit/{}.html".format(step), context=context)


def lp_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/lp_contest_steps/{}.html".format(step), context=context)


def lp_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/lp_contest_steps/edit/{}.html".format(step), context=context)


def td_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    list_of_ils = ["Hand-drawn", "Children", "Comic", "Medical", "Fashion", "Conceptual", "Paper Art", "Retro", "Pop",
                   "Line", "Technical", "Storyboard", "Vector", "Icon", "Lettering", "Cartographic"]
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "list_of_ils": list_of_ils, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/td_contest_steps/{}.html".format(step), context=context)


def td_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    list_of_ils = ["Hand-drawn", "Children", "Comic", "Medical", "Fashion", "Conceptual", "Paper Art", "Retro", "Pop",
                   "Line", "Technical", "Storyboard", "Vector", "Icon", "Lettering", "Cartographic"]
    context = {"category": category, "contest": contest, "form_fields": form_fields, "list_of_ils": list_of_ils}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/td_contest_steps/edit/{}.html".format(step), context=context)

def md_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    list_of_ils = ["Hand-drawn", "Children", "Comic", "Medical", "Fashion", "Conceptual", "Paper Art", "Retro", "Pop",
                   "Line", "Technical", "Storyboard", "Vector", "Icon", "Lettering", "Cartographic"]
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "list_of_ils": list_of_ils, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/md_contest_steps/{}.html".format(step), context=context)

def md_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    list_of_ils = ["Hand-drawn", "Children", "Comic", "Medical", "Fashion", "Conceptual", "Paper Art", "Retro", "Pop",
                   "Line", "Technical", "Storyboard", "Vector", "Icon", "Lettering", "Cartographic"]
    context = {"category": category, "contest": contest, "form_fields": form_fields, "list_of_ils": list_of_ils}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/md_contest_steps/edit/{}.html".format(step), context=context)


def bkc_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/bkc_contest_steps/{}.html".format(step), context=context)

def bkc_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/bkc_contest_steps/edit/{}.html".format(step), context=context)

def mgc_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
    return render(request, "customer/mgc_contest_steps/{}.html".format(step), context=context)

def mgc_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/mgc_contest_steps/edit/{}.html".format(step), context=context)


def wpd_edit_contest(request, contest, step):
    contest_object = Contest.objects.get(id=contest)
    category = SubCategory.objects.filter(template_name=contest_object.category.template_name).first()
    form_fields = Contest.objects.get(id=contest).form_fields
    context = {"category": category, "contest": contest, "form_fields": form_fields}
    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})

    return render(request, "customer/wpd_contest_steps/edit/{}.html".format(step), context=context)


def wpd_contest_step(request, contest, step):
    category = Contest.objects.get(id=contest).category
    form_fields = Contest.objects.get(id=contest).form_fields
    contest_object = Contest.objects.get(id=contest)

    context = {"category": category, "contest": contest, "form_fields": form_fields, "contest_object": contest_object}
    if step == "step_5": step = "step_4"

    if step == "step_2":
        attachments = Attachment.objects.filter(contest_id=contest)
        context.update({"attachments": attachments})
    if step == "step_3":
        event = DiscountEvent.objects.filter(contest_id=contest)
        contest_object = Contest.objects.get(id=contest)

        if DiscountEvent.objects.filter(contest_id=contest).exists():
            discount = event.first().discount
            context.update({"is_applied": True, "discount": discount})
        context.update({"contest_object": contest_object})
    if step == "step_4":
        context.update(handle_payment_context(contest))
        page_count = contest_object.form_fields.get("web_pages", None)
        if page_count: context.update({"page_price": len(page_count) * 100})
        context.update({"page_count": page_count})
    return render(request, "customer/wpd_contest_steps/{}.html".format(step), context=context)


