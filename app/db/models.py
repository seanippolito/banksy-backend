from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text
)
import uuid

class Base(DeclarativeBase):
    pass


class ApplicationLogger(Base):
    __tablename__ = "application_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    error_code = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)  # module/route/function name
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="logs")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clerk_user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    logs = relationship("ApplicationLogger", back_populates="user")
    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    account_holders = relationship("AccountHolder", back_populates="user")

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    holders = relationship("AccountHolder", back_populates="account")
    cards = relationship("Card", back_populates="account")

class AccountHolder(Base):
    __tablename__ = "account_holders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    holder_type = Column(String, nullable=False)  # "Primary", "Joint", "Trust", etc.

    # Relationships
    user = relationship("User", back_populates="account_holders")
    account = relationship("Account", back_populates="holders")

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    card_number_last4 = Column(String(4), nullable=False)
    card_type = Column(String, nullable=False)  # "Debit", "Credit", "Virtual"
    expiration_month = Column(Integer, nullable=False)
    expiration_year = Column(Integer, nullable=False)
    status = Column(String, default="Active")  # "Active", "Blocked", "Expired"

    # Relationships
    account = relationship("Account", back_populates="cards")

class TransactionType:
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    amount: Mapped[int] = mapped_column(Integer)  # store in cents for precision
    type: Mapped[str] = mapped_column(String(10))  # "DEBIT" or "CREDIT"
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # NEW: link transactions belonging to the same transfer
    transfer_id = Column(String, index=True, nullable=True, default=lambda: str(uuid.uuid4()))
    account: Mapped["Account"] = relationship(back_populates="transactions")