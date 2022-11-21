### su an kullanilmiyor
from django import template

register = template.Library()

@register.filter
def in_status(contests, status):

    if status=="all":

        return contests
    return contests.filter(status=status)


@register.filter
def in_status_set(contests, status):
    if status=="all":
        return set(contests)
    return set(contests.filter(status=status))


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
def get_first_3(qs):
    return qs[0:3]