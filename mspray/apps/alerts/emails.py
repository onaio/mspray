from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def weekly_update_email(recipient, district_list, totals):
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
