from pydantic import BaseModel

from typing import Optional, Dict
from datetime import datetime


class DeleteRequest(BaseModel):
    message: str


class MessageRequest(BaseModel):
    text_msg: str
    send_time: datetime
    status: Optional[str]
    newsletter_id: int
    client_id: int


class MessageRequestOut(BaseModel):
    id: int
    text_msg: str
    send_time: datetime
    status: Optional[str]
    newsletter_id: int
    client_id: int
    create_to: datetime


class ClientRequest(BaseModel):
    phone_number: str
    operator_code: str
    tag: Optional[str]
    timezone: str


class NewsletterRequest(BaseModel):
    start_time: datetime
    message: str
    filter_operation_code: Optional[str]
    filter_tag: Optional[str]
    end_time: Optional[datetime]
    time_interval: Optional[str]


class NewsletterRequestOut(BaseModel):
    id: int
    start_time: datetime
    message: str
    filter_operation_code: Optional[str]
    filter_tag: Optional[str]
    end_time: Optional[datetime]
    time_interval: Optional[str]


class NewsletterRequestGetId(BaseModel):
    id: int
    start_time: datetime
    message: str
    filter_operation_code: Optional[str]
    filter_tag: Optional[str]
    end_time: Optional[datetime]
    message_count: int
    messages: list


class NewsletterRequestGetAll(BaseModel):
    id: str
    start_time: datetime
    statuses: Dict


class ClientRequestOut(BaseModel):
    id: int
    phone_number: str
    operator_code: str
    tag: Optional[str]
    timezone: str
