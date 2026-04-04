from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.schemas import NotificationRequest, BudgetAlertRequest
from app.notifications import send_email, store_notification, get_user_notifications, send_budget_alert_email
from datetime import datetime

app = FastAPI(
    title="Notification Service",
    description="Handles email notifications and alerts for the finance tracker",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

@app.post("/api/notifications/send")
def send_notification(notification: NotificationRequest):
    notification_record = {
        "user_id": notification.user_id,
        "subject": notification.subject,
        "message": notification.message,
        "type": notification.notification_type,
        "timestamp": datetime.utcnow().isoformat(),
        "read": False
    }
    store_notification(notification.user_id, notification_record)

    if notification.email:
        success = send_email(notification.email, notification.subject, notification.message)
        return {"status": "sent" if success else "stored", "notification": notification_record}

    return {"status": "stored", "notification": notification_record}

@app.post("/api/notifications/budget-alert")
def send_budget_alert(alert: BudgetAlertRequest):
    success = send_budget_alert_email(alert)
    notification_record = {
        "user_id": alert.user_id,
        "subject": f"Budget Alert: {alert.budget_name}",
        "message": f"Your {alert.budget_name} budget is at {alert.usage_percentage:.1f}%",
        "type": "alert",
        "timestamp": datetime.utcnow().isoformat(),
        "read": False
    }
    store_notification(alert.user_id, notification_record)
    return {"status": "sent" if success else "stored", "usage_percentage": alert.usage_percentage}

@app.get("/api/notifications/{user_id}")
def get_notifications(user_id: int, limit: int = 20):
    notifications = get_user_notifications(user_id, limit)
    return {"user_id": user_id, "notifications": notifications, "count": len(notifications)}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "notification-service"}
