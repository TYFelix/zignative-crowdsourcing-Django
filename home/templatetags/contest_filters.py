from django import template

register = template.Library()


@register.filter
def am_i_selected(user,contest):
    for finalist in contest.finalists.all():

        if user == finalist.entry.user:
            return True
    return False

@register.filter
def is_finalist(entry,contest):
    for finalist in contest.finalists.all():
        if entry == finalist.entry:
            return True
    return False

@register.filter
def is_winner(entry,contest):
    finalist=contest.finalists.filter(is_winner=True).first()
    if entry==finalist.entry:
        return True
    return False



@register.filter
def am_i_winner(user,contest):
    finalist = contest.finalists.filter(is_winner=True).first()
    if user == finalist.entry.user:
        return True
    return False

@register.filter
def get_my_finalist_entries(user,contest):
    liste=[]
    for finalist in contest.finalists.all():
        if user == finalist.entry.user:
            liste.append(finalist.entry)
    return liste

@register.filter
def times(number):
    return range(number)

@register.filter
def order_them(entries):
    return entries.order_by("-created_date")

@register.filter
def in_status(entries, status):
    if status == "all":
        return entries.filter(is_deleted=False)
    if status == "active":
        return entries.filter(is_declined=False,is_deleted=False)
    if status == "rated":
        return entries.filter(rate__gt=0,is_declined=False,is_deleted=False)
    if status == "declined":
        return entries.filter(is_declined=True,is_deleted=False)
    if status == "withdraw":
        return entries.filter(is_deleted=True)
    else:
        return entries

@register.filter
def get_withdraw(entries,request):
    return entries.filter(is_deleted=True,user=request.user)

@register.filter
def any_withdraw(entries,request):
    if entries.filter(is_deleted=True, user=request.user).exists():
        print("exis")
        return True
    else:
        return False

@register.filter
def is_entry_deletable(entry,user):
    if user == entry.user and entry.is_deleted==False:
       if entry.contest.status=="in_progress":
           if entry.contest.round=="qualify" or entry.contest.round=="qualify_end":
               return True
    else:
        return False

@register.filter
def is_empty(contest, status):
    if status == "all":
        if contest.entries.all().count() == 0:
            return True
        else:
            return False
    if status == "active":
        if contest.entries.filter(is_declined=False).count() == 0:
            return True
        else:
            return False
    if status == "rated":
        if contest.entries.filter(rate__gt=0,is_declined=False).count() == 0:
            return True
        else:
            return False
    if status == "declined":
        if contest.entries.filter(is_declined=True).count() == 0:
            return True
        else:
            return False
    if status == "withdraw":
        if contest.entries.filter(is_deleted=True).count() == 0:
            return True
        else:
            return False



@register.filter
def get_controlled_image(entry,request):

    if entry.user == request.user:
        return entry.get_display_image()
    elif entry.contest.user == request.user:
        return entry.get_display_image()
    else:
        try:
            if entry.contest.form_fields["is_hidden"]:
                return entry.get_hidden_image()
        except KeyError:
            return entry.get_display_image()

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
