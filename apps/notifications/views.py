from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Create your views here.
def password_restore_email(request, receiver_email, code, url):
    subject = 'Password Restore'
    # message = f"Your password restore code: {code}\nRestore your password here: link\nIf it wasn't you, you may just ignore this message."
    context = {'code': code, 'url': url}
    html_message = render_to_string('email_templates/password_restore_HTML.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [receiver_email]
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
