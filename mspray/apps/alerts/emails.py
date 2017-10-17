from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from mspray.apps.alerts.rapidpro import get_contacts


def send_weekly_update_email():
    """
    Gets weekly update data and contacts
    Then sends the data to each contact, via email
    """
    from mspray.apps.main.utils import get_district_summary

    group_uuid = settings.RAPIDPRO_WEEKLY_UPDATE_CONTACT_GROUP
    contacts = get_contacts(group_uuid)
    district_list, totals = get_district_summary()
    for contact in contacts:
        if contact.emails:
            # we just take the first email address
            address = "{name} <{email}>".format(name=contact.name,
                                                email=contact.emails[0])
            weekly_update_email(address, district_list, totals)


def weekly_update_email(recipient, district_list, totals):
    """
    Creates and sends the weekly update email
    """
    c = {'district_list': district_list, 'totals': totals,
         'url': settings.MSPRAY_WEEKLY_DASHBOARD_UPDATE_URL}
    subject = render_to_string(
        'alerts/emails/weekly_update_subject.txt', c).replace('\n', '')
    text_content = render_to_string(
        'alerts/emails/weekly_update_body.txt', c)
    html_content = render_to_string(
        'alerts/emails/weekly_update_body.html', c).replace('\n', '')
    from_email = settings.MSPRAY_EMAIL
    to = recipient
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send(fail_silently=False)
