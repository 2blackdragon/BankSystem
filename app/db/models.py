from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Один пользователь → много счетов
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_number = Column(String, unique=True, index=True)
    balance = Column(Float, default=0.0)
    currency = Column(String, default="RUB")

    # Связи
    user = relationship("User", back_populates="accounts")

    # Одна сторона транзакций (как отправитель и как получатель)
    outgoing_transactions = relationship(
        "Transaction",
        foreign_keys="[Transaction.from_account_id]",
        back_populates="from_account"
    )
    incoming_transactions = relationship(
        "Transaction",
        foreign_keys="[Transaction.to_account_id]",
        back_populates="to_account"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    amount = Column(Float)
    currency = Column(String, default="RUB")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="completed")

    # Связи (двусторонние)
    from_account = relationship(
        "Account",
        foreign_keys=[from_account_id],
        back_populates="outgoing_transactions"
    )
    to_account = relationship(
        "Account",
        foreign_keys=[to_account_id],
        back_populates="incoming_transactions"
    )
