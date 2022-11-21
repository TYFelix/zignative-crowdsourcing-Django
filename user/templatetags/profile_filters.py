from django import template

from customer.models import Contest
from home.models import Invite

register = template.Library()

@register.filter
def am_i_select(user,service):
    tags = user.tags.all()
    if service in [i.service for i in tags]:
        return True
    else: return False


@register.filter
def is_invited(contest,designer):
    # contest = Contest.objects.get(id=contest)
    i=Invite.objects.filter(contest=contest,designer__username=designer)
    return i.exists()

