from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Newsletter(Base):
    """Сущность рассылка"""
    __tablename__ = 'newsletters'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    message = Column(String)
    filter_operation_code = Column(String)
    filter_tag = Column(String)
    end_time = Column(DateTime)
    time_interval = Column(String)

    messages = relationship('Message', back_populates='newsletter')


class Client(Base):
    """Сущность клиент"""
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    phone_number = Column(String(11), nullable=False)
    operator_code = Column(String)
    tag = Column(String)
    timezone = Column(String)

    messages = relationship('Message', back_populates='client')


class Message(Base):
    """Сущность сообщение"""
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    text_msg = Newsletter.message
    send_time = Column(DateTime, nullable=False)
    status = Column(String)
    newsletter_id = Column(Integer, ForeignKey('newsletters.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)

    newsletter = relationship('Newsletter', back_populates='messages')
    client = relationship('Client', back_populates='messages')
