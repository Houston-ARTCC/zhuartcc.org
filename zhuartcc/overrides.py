from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils.html import strip_tags

from zhuartcc.decorators import run_async


@run_async
def send_mail(subject, html, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None, connection=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(subject, strip_tags(html), from_email, recipient_list, connection=connection)
    mail.attach_alternative(html, 'text/html')

    return mail.send()


@run_async
def send_mass_mail(datatuple, fail_silently=False, auth_user=None,
                   auth_password=None, connection=None):
    """
    Given a datatuple of (subject, html, from_email, recipient_list), send
    each message to each recipient list. Return the number of emails sent.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user and auth_password are set, use them to log in.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    messages = []
    for subject, html, sender, recipient in datatuple:
        email = EmailMultiAlternatives(subject, strip_tags(html), sender, recipient, connection=connection)
        email.attach_alternative(html, 'text/html')
        messages += [email]

    return connection.send_messages(messages)
