import requests

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from prometheus_fastapi_instrumentator import Instrumentator
from authlib.integrations.starlette_client import OAuth

from datetime import datetime
from threading import Timer

from models import Client, Message, Newsletter
from schemas import (ClientRequest, MessageRequest, NewsletterRequest,
                     MessageRequestOut, DeleteRequest, NewsletterRequestOut,
                     NewsletterRequestGetId, NewsletterRequestGetAll, ClientRequestOut)
from config import _get_db, HEADERS


app = FastAPI()
oauth = OAuth()
template = Jinja2Templates(directory="templates")
Instrumentator().instrument(app).expose(app)  # /metrics


def get_clients_for_newsletter(filter_tag: str, filter_operation_code: str) -> list:
    with _get_db() as db:
        query = db.query(Client).filter(Client.tag == filter_tag, Client.operator_code == filter_operation_code)
        clients = [client for client in query]

        return clients


def send_for_client(client: Client, text_msg: str, message_id: int) -> dict:
    payload = {
        "id": client.id,
        "phone": client.phone_number,
        "text": text_msg
    }

    url = f"https://probe.fbrq.cloud/v1/send/{message_id}"
    response = requests.post(url=url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"HTTP Error {response.status_code}: {response.reason}"}


def send_newsletter(newsletter: Newsletter) -> None:
    clients = get_clients_for_newsletter(newsletter.filter_tag, newsletter.filter_operation_code)
    for client in clients:
        message = Message(text_msg=newsletter.message, client_id=client.id, newsletter_id=newsletter.id)
        with _get_db() as db:
            db.add(message)
            db.flush()
            db.refresh(message)

        send_for_client(client, newsletter.message, Message.id)


@app.get("/")
async def root():
    return {"message": "Hello World"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API for Fabrique Studio",
        version="1.0",
        description="This is API for Fabrique Studio cases.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/webui", response_class=HTMLResponse)
def get_all_newsletters(request: Request):
    with _get_db() as db:
        newsletters = db.query(Newsletter).all()
        context = {
            "request": request,
            "newsletters": newsletters
        }

        return template.TemplateResponse("newsletters.html", context)


@app.post('/clients', tags=['Users'],
          responses={status.HTTP_200_OK: {"model": ClientRequestOut}})
def create_client(client: ClientRequest) -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой PUT-метод API, создает объект клиента и сохраняет его в базу данных.

        Аргумент client - объект класса ClientRequest, который содержит информацию о клиенте, которого нужно создать.
        Этот объект имеет следующие атрибуты:

        * phone_number: строка, содержащая телефон клиента
        * operator_code: строка, содержащая код оператора телефона клиета
        * tag: строка, содержащая индивидуальную короткую информацию о клиенте
        * timezone: строка, содержащая тайм-зону от МСК
    """
    with _get_db() as db:
        db_client = Client(phone_number=client.phone_number, operator_code=client.operator_code,
                           tag=client.tag, timezone=client.timezone)

        db.add(db_client)
        db.flush()
        db.refresh(db_client)

        _dict = {
            "id": db_client.id,
            "phone_number": db_client.phone_number,
            "operator_code": db_client.operator_code,
            "tag": db_client.tag,
            "timezone": db_client.timezone
        }

        return _dict


@app.put('/clients/{client_id}', tags=['Users'],
         responses={status.HTTP_200_OK: {"model": ClientRequestOut}})
def update_client(client_id: int, client: ClientRequest) -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой PUT-метод API, редактирует объект клиента и сохраняет его в базу данных.

        Аргумент client_id - это колонка сущности Client, соддержит информацию о id клиента - которую нужно редактировать

        Аргумент client - объект класса ClientRequest, который содержит информацию о клиенте, которого нужно редактировать.
        Этот объект имеет следующие атрибуты:

        * phone_number: строка, содержащая телефон клиента
        * operator_code: строка, содержащая код оператора телефона клиета
        * tag: строка, содержащая индивидуальную короткую информацию о клиенте
        * timezone: строка, содержащая тайм-зону от МСК
    """
    with _get_db() as db:
        db_client = db.query(Client).filter(Client.id == client_id).first()
        if not db_client:
            raise HTTPException(status_code=404, detail='[E] Client not found!')

        for key, value in client.dict(exclude_unset=True).items():
            setattr(db_client, key, value)

        db.flush()
        db.refresh(db_client)

        _dict = {
            "id": db_client.id,
            "phone_number": db_client.phone_number,
            "operator_code": db_client.operator_code,
            "tag": db_client.tag,
            "timezone": db_client.timezone
        }
        return _dict


@app.delete('/clients/{client_id}', tags=['Users'],
            responses={status.HTTP_200_OK: {"model": DeleteRequest}})
def delete_client(client_id: int) -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой DELETE-метод API, удаляет клиента из базы данных.

        Аргумент client_id - это колонка сущности Client, соддержит информацию о id клиент - которого нужно удалить
    """
    with _get_db() as db:
        db_client = db.query(Client).filter(Client.id == client_id).first()
        if not db_client:
            raise HTTPException(status_code=404, detail='[E] Client not found!')

        db.delete(db_client)
        db.flush()

        _dict = {
            "message": "Client deleted successfully"
        }

        return _dict


@app.post('/newsletters', tags=['Newsletters'],
          responses={status.HTTP_200_OK: {"model": NewsletterRequestOut}})
def create_newsletter(newsletter: NewsletterRequest) -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой POST-метод API, создает объект рассылкы и сохраняет его в базу данных.

        Аргумент newsletter_id - это колонка сущности Newsletter, соддержит информацию о id рассылки - которую нужно создать

        Аргумент newsletter - объект класса NewsletterRequest, который содержит информацию о рассылке, которое нужно создать.
        Этот объект имеет следующие атрибуты:

        * start_time: дата и время, когда рассылка должна быть отправлена
        * message: строка, содержащая текст рассылки
        * filter_operation_code: строка, содержащая код оператора телефона для фильтра
        * filter_tag: статус сообщения (например, "отправлено", "не отправлено" и т.д.) для фильтра
        * end_time: дата и время, когда рассылка должна быть закончена
        * time_interval: None пока не разработал :(
    """
    with _get_db() as db:
        db_newsletter = Newsletter(start_time=newsletter.start_time, message=newsletter.message,
                                   filter_operation_code=newsletter.filter_operation_code,
                                   filter_tag=newsletter.filter_tag, end_time=newsletter.end_time,
                                   time_interval=newsletter.time_interval)

        db.add(db_newsletter)
        db.flush()
        db.refresh(db_newsletter)

        if db_newsletter.start_time < datetime.now() < db_newsletter.end_time:
            Timer((db_newsletter.start_time - datetime.now()).total_seconds(), send_newsletter,
                  args=(db_newsletter,)).start()

        _dict = {
            "id": db_newsletter.id,
            "start_time": db_newsletter.start_time,
            "message": db_newsletter.message,
            "filter_operation_code": db_newsletter.filter_operation_code,
            "filter_tag": db_newsletter.filter_tag,
            "end_time": db_newsletter.end_time,
            "time_interval": db_newsletter.time_interval
        }

        return _dict


@app.get('/newsletters/stats', tags=['Newsletters'],
         responses={status.HTTP_200_OK: {"model": NewsletterRequestGetAll}})
def get_newsletters_stats() -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой GET-метод API, демострирует объекты рассылкы.
    """
    with _get_db() as db:
        result = db.query(
            Newsletter.id, Newsletter.start_time, Message.status,
            func.count(Message.newsletter_id).label('count')
        ).outerjoin(Message, Newsletter.id == Message.newsletter_id).group_by(
            Newsletter.id, Newsletter.start_time, Message.status).all()

        stats = {}
        for newsletter_id, start_time, status, count in result:
            if newsletter_id not in stats:
                stats[newsletter_id] = {
                    "start_time": start_time,
                    "statuses": {}
                }
            stats[newsletter_id]['statuses'][status] = count

        return stats


@app.get('/newsletters/stats/{newsletter_id}', tags=['Newsletters'],
         responses={status.HTTP_200_OK: {"model": NewsletterRequestGetId}})
def get_newsletter_stats(newsletter_id: int) -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой GET-метод API, демострирует конкретный объект рассылкы.

        Аргумент newsletter_id - это колонка сущности Newsletter, соддержит информацию о id рассылки - которую нужно посмотреть
    """
    with _get_db() as db:
        newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
        if not newsletter:
            raise HTTPException(status_code=404, detail='[E] Newsletter not found!')

        messages = db.query(Message).filter(Message.newsletter_id == newsletter_id).all()

        stats = {
            "id": newsletter.id,
            "time_interval": newsletter.time_interval,
            "message": newsletter.message,
            "filter_operation_code": newsletter.filter_operation_code,
            "filter_tag": newsletter.filter_tag,
            "start_time": newsletter.start_time,
            "end_time": newsletter.end_time,
            "message_count": len(messages),
            "messages": []
        }
        for message in messages:
            stats["messages"].append({
                "send_time": message.send_time,
                "status": message.status,
                "client": {
                    "id": message.client.id,
                    "phone_number": message.client.phone_number,
                    "operator_code": message.client.operator_code,
                    "tag": message.client.tag,
                    "timezone": message.client.timezone
                }
            })

        return stats


@app.put('/newsletters/{newsletter_id}', tags=['Newsletters'],
         responses={status.HTTP_200_OK: {"model": NewsletterRequestOut}})
def update_newsletter(newsletter_id: int, newsletter: NewsletterRequest) -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой PUT-метод API, редактирует объект рассылкы и сохраняет его в базу данных.

        Аргумент newsletter_id - это колонка сущности Newsletter, соддержит информацию о id рассылки - которую нужно отредактировать

        Аргумент newsletter - объект класса NewsletterRequest, который содержит информацию о рассылке, которое нужно отредактировать.
        Этот объект имеет следующие атрибуты:

        * start_time: дата и время, когда рассылка должна быть отправлена
        * message: строка, содержащая текст рассылки
        * filter_operation_code: строка, содержащая код оператора телефона для фильтра
        * filter_tag: статус сообщения (например, "отправлено", "не отправлено" и т.д.) для фильтра
        * end_time: дата и время, когда рассылка должна быть закончена
        * time_interval: None пока не разработал :(
    """
    with _get_db() as db:
        db_newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
        if not db_newsletter:
            raise HTTPException(status_code=404, detail='[E] Newsletter not found!')

        for key, value in newsletter.dict(exclude_unset=True).items():
            setattr(db_newsletter, key, value)

        db.flush()
        db.refresh(db_newsletter)

        _dict = {
            "id": db_newsletter.id,
            "start_time": db_newsletter.start_time,
            "message": db_newsletter.message,
            "filter_operation_code": db_newsletter.filter_operation_code,
            "filter_tag": db_newsletter.filter_tag,
            "end_time": db_newsletter.end_time,
            "time_interval": db_newsletter.time_interval
        }

        return _dict


@app.delete('/newsletters/{newsletter_id}', tags=['Newsletters'],
            responses={status.HTTP_200_OK: {"model": DeleteRequest}})
def delete_newsletter(newsletter_id: int) -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой DELETE-метод API, удаляет рассылку из базы данных.

        Аргумент newsletter_id - это колонка сущности Newsletter, соддержит информацию о id рассылки - которую нужно удалить
    """
    with _get_db() as db:
        db_newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
        if not db_newsletter:
            raise HTTPException(status_code=404, detail='[E] Newsletter not found!')

        db.delete(db_newsletter)
        db.flush()

        _dict = {
            "message": "Newsletter deleted successfully"
        }

        return _dict


@app.post('/messages', tags=['Messages'],
          responses={status.HTTP_200_OK: {"model": MessageRequestOut}})
def send_message(message: MessageRequest) -> dict:
    # noinspection SpellCheckingInspection
    """
        Данная функция представляет собой POST-метод API, который отправляет сообщение клиенту и сохраняет его в базе данных.

        Аргумент message - объект класса MessageRequest, который содержит информацию о сообщении, которое нужно отправить.
        Этот объект имеет следующие атрибуты:

        * text_msg: строка, содержащая текст сообщения
        * send_time: дата и время, когда сообщение должно быть отправлено
        * status: статус сообщения (например, "отправлено", "не отправлено" и т.д.)
        * newsletter_id: ID новостной рассылки, связанной с сообщением
        * client_id: ID клиента, которому отправляется сообщение
    """
    with _get_db() as db:
        db_message = Message(text_msg=message.text_msg, send_time=message.send_time,
                             status=message.status, newsletter_id=message.newsletter_id,
                             client_id=message.client_id)
        db.add(db_message)
        db.flush()
        db.refresh(db_message)

        send_for_client(db_message.client, db_message.text_msg, db_message.id)

        _dict = {
            "id": db_message.id,
            "text_msg": db_message.text_msg,
            "send_time": db_message.send_time,
            "status": db_message.status,
            "newsletter_id": db_message.newsletter_id,
            "client_id": db_message.client_id,
            "create_to": datetime.now()
        }

        return _dict
