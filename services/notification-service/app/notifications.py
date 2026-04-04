import smtplib
import redis
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.schemas import NotificationRequest, BudgetAlertRequest
import logging

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.SMTP_USER:
        logger.info(f"Email simulation - To: {to_email}, Subject: {subject}")
        return True
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def store_notification(user_id: int, notification: dict):
    key = f"notifications:{user_id}"
    redis_client.lpush(key, json.dumps(notification))
    redis_client.ltrim(key, 0, 99)  # Keep last 100 notifications

def get_user_notifications(user_id: int, limit: int = 20) -> list:
    key = f"notifications:{user_id}"
    notifications = redis_client.lrange(key, 0, limit - 1)
    return [json.loads(n) for n in notifications]

def send_budget_alert_email(alert: BudgetAlertRequest) -> bool:
    subject = f"Budget Alert: {alert.budget_name} at {alert.usage_percentage:.1f}%"
    body = f"""
    <html><body>
    <h2>Budget Alert - Finance Tracker</h2>
    <p>Your budget <strong>{alert.budget_name}</strong> for category <strong>{alert.category}</strong> has reached <strong>{alert.usage_percentage:.1f}%</strong> of its limit.</p>
    <table>
        <tr><td>Budget Limit:</td><td>${alert.limit_amount:.2f}</td></tr>
        <tr><td>Amount Spent:</td><td>${alert.spent_amount:.2f}</td></tr>
        <tr><td>Remaining:</td><td>${(alert.limit_amount - alert.spent_amount):.2f}</td></tr>
    </table>
    <p>Please review your spending to stay within budget.</p>
    </body></html>
    """
    return send_email(alert.email, subject, body)
