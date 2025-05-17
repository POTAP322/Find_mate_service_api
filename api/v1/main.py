from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from api.v1.database import engine, Base, SessionLocal
from api.v1.services import PartnerRequestService

app = FastAPI(title="FindMate API")

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

# Подключаем роутеры
from api.v1.routers import users, games, usergames, partner_requests, userlogs
app.include_router(users.router)
app.include_router(games.router)
app.include_router(usergames.router)
app.include_router(partner_requests.router)
app.include_router(userlogs.router)

# Создаем экземпляр сервиса
partner_request_service = PartnerRequestService()

# Функция для выполнения задачи
def delete_expired_requests_task():
    db = SessionLocal()
    try:
        partner_request_service.delete_expired_requests(db)
    finally:
        db.close()

# Создаем планировщик задач
scheduler = BackgroundScheduler()
scheduler.add_job(delete_expired_requests_task, 'interval', minutes=2)
scheduler.start()

# Завершаем работу планировщика при завершении приложения
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
