from arspace import settings
from utils.constants import DATA, ERROR, FALSE, TRUE, SUCCESS
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import render


# Send email using gmail smtp
def send_email_using_gmail_smtp(recipient, subject, plain_text, html_template):
    try:
        email = EmailMessage(subject, plain_text, to=[recipient])
        email.content_subtype = "html"
        email.body = html_template
        is_sent = email.send()
        return {SUCCESS: TRUE, DATA: is_sent}
    except Exception as ex:
        return {SUCCESS: FALSE, ERROR: str(ex)}
