from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from mspray.apps.alerts.rapidpro import get_contacts
from mspray.apps.alerts.utils import get_district_summary


def send_weekly_update_email():
    """
    Gets weekly update data and contacts
    Then sends the data to each contact, via email
    """
    group_uuid = settings.RAPIDPRO_WEEKLY_UPDATE_CONTACT_GROUP
    contacts = get_contacts(group_uuid)
    district_list, totals = get_district_summary()
    address_list = []
    for contact in contacts:
        if contact.emails:
            # we just take the first email address
            address = "{name} <{email}>".format(name=contact.name,
                                                email=contact.emails[0])
            address_list.append(address)
    if address_list:
        weekly_update_email(address_list, district_list, totals)


def weekly_update_email(recipients, district_list, totals):
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
    to = recipients
    reply_to = settings.MSPRAY_REPLY_TO_EMAIL
    msg = EmailMultiAlternatives(subject=subject, body=text_content, to=to,
                                 from_email=from_email, reply_to=[reply_to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send(fail_silently=False)
