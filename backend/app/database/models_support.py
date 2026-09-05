"""
SQLAlchemy database models - Support and Approval models.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship

from .models import Base, TicketStatus, ApprovalStatus, ApprovalActionType


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(String(20), primary_key=True)
    customer_id = Column(String(20), ForeignKey("customers.id"), nullable=False, index=True)
    order_id = Column(String(20), ForeignKey("orders.id"), nullable=True, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False, index=True)
    assigned_team = Column(String(100), nullable=True)
    assigned_agent = Column(String(20), nullable=True)
    priority = Column(String(20), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="tickets")
    order = relationship("Order", back_populates="tickets")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(20), primary_key=True)
    thread_id = Column(String(100), nullable=False, index=True)
    customer_id = Column(String(20), ForeignKey("customers.id"), nullable=False, index=True)
    order_id = Column(String(20), ForeignKey("orders.id"), nullable=True, index=True)
    action_type = Column(Enum(ApprovalActionType), nullable=False)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, index=True)

    requested_amount = Column(Float, nullable=True)
    requested_reason = Column(String(255), nullable=True)
    requested_data = Column(Text, nullable=True)

    decision = Column(String(20), nullable=True)
    edited_amount = Column(Float, nullable=True)
    edited_reason = Column(String(255), nullable=True)
    edited_data = Column(Text, nullable=True)
    decided_by = Column(String(20), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    decision_notes = Column(Text, nullable=True)

    executed_at = Column(DateTime, nullable=True)
    execution_result = Column(Text, nullable=True)
    execution_error = Column(Text, nullable=True)

    ai_reasoning_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer")
    order = relationship("Order")


# Indexes
Index("ix_orders_customer_status", "customer_id", "status")
Index("ix_approvals_status_created", Approval.status, Approval.created_at)
Index("ix_tickets_customer_status", SupportTicket.customer_id, SupportTicket.status)