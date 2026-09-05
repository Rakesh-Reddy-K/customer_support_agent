"""
SQLAlchemy database models - Order related models.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from .models import Base, OrderStatus, PaymentStatus, ShipmentStatus


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(20), primary_key=True)
    customer_id = Column(String(20), ForeignKey("customers.id"), nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(Text, nullable=True)
    billing_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    shipment = relationship("Shipment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="order")
    tickets = relationship("SupportTicket", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(20), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String(20), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(20), primary_key=True)
    order_id = Column(String(20), ForeignKey("orders.id"), nullable=False, unique=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True, unique=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="payment")
    refunds = relationship("Refund", back_populates="payment")


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(String(20), primary_key=True)
    order_id = Column(String(20), ForeignKey("orders.id"), nullable=False, unique=True, index=True)
    tracking_number = Column(String(100), nullable=True, unique=True)
    carrier = Column(String(100), nullable=True)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PENDING, nullable=False)
    shipped_at = Column(DateTime, nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    tracking_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="shipment")


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String(20), primary_key=True)
    order_id = Column(String(20), ForeignKey("orders.id"), nullable=False, index=True)
    payment_id = Column(String(20), ForeignKey("payments.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    approved_by = Column(String(20), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="refunds")
    payment = relationship("Payment", back_populates="refunds")