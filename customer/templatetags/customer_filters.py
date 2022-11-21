from django import template

from customer.models import PollObject

register = template.Library()

@register.filter
def in_status(contests, status):
    if status=="all":
        return contests.filter(is_temp=False)
    return contests.filter(status=status,is_temp=False)


@register.filter
def is_deletable(contest):
    if contest.is_paid:
        return False
    elif contest.status=="completed":
        return False
    elif contest.status=="canceled":
        return False
    else:
        return True
@register.filter
def get_controlled_image(entry,request):
    if entry.user == request.user:
        return entry.get_image()
    elif entry.contest.user == request.user:
        return entry.get_image()
    else:
        try:
            if entry.contest.form_fields["is_hidden"]:
                return entry.get_hidden_image()
        except KeyError:
            return entry.get_image()

@register.filter
def get_controlled_main(entry,request):

    if entry.user == request.user:
        return entry.get_image()
    elif entry.contest.user == request.user:
        return entry.get_image()
    else:
        try:
            if entry.contest.form_fields["is_hidden"]:
                return entry.get_hidden_main()
        except KeyError:
            return entry.get_image()

@register.filter
def ranger(number):
    return range(1,number)

@register.filter
def get_obj_count(obj,number):
    obj = PollObject.objects.get(id=obj)
    return obj.get_rate_ratio()[number]["count"]

@register.filter
def get_obj_ratio(obj,number):
    obj = PollObject.objects.get(id=obj)
    return obj.get_rate_ratio()[number]["rate"]