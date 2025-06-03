# main.py
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from api.v1.database import engine, Base, SessionLocal
from api.v1.services import PartnerRequestService, UserService
from api.v1.admin import setup_admin

app = FastAPI(title="FindMate API")

# Настройка админки
setup_admin(app)

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

# Подключаем роутеры
from api.v1.routers import users, games, usergames, partner_requests, userlogs, auth, notification_router, \
    payment_router

app.include_router(users.router)
app.include_router(games.router)
app.include_router(usergames.router)
app.include_router(partner_requests.router)
app.include_router(userlogs.router)
app.include_router(auth.router)
app.include_router(notification_router.router)
app.include_router(payment_router.router)

# Создаем экземпляр сервиса
partner_request_service = PartnerRequestService()

# Функция для выполнения задачи
def delete_expired_requests_task():
    db = SessionLocal()
    try:
        partner_request_service.delete_expired_requests(db)
    finally:
        db.close()

def downgrade_premium_users_task():
    db = SessionLocal()
    try:
        user_service = UserService()
        user_service.downgrade_expired_premium_users(db)
    finally:
        db.close()

# Создаем планировщик задач
scheduler = BackgroundScheduler()
scheduler.add_job(delete_expired_requests_task, 'interval', minutes=2)
scheduler.add_job(downgrade_premium_users_task, 'interval', minutes=10)

scheduler.start()

# Завершаем работу планировщика при завершении приложения
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)