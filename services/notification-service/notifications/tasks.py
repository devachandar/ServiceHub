from celery import shared_task

from . import mailer


@shared_task(bind=True, max_retries=5, default_retry_delay=15)
def send_email_task(self, template_name, to_email, context):
    try:
        return mailer.send(template_name, to_email, context)
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc)
