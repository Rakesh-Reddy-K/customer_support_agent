"""
Seed database with realistic test data for TechKart.
"""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import (
    Base, Customer, Product, Order, OrderItem, Payment, Shipment,
    Refund, SupportTicket, Approval,
    OrderStatus, PaymentStatus, ShipmentStatus, TicketStatus,
    ApprovalStatus, ApprovalActionType,
)
from app.config.settings import settings


# ---------- Customers ----------
CUSTOMERS = [
    {"id": "CUS1001", "email": "arjun.sharma@email.com", "phone": "+91-9876543210", "first_name": "Arjun", "last_name": "Sharma"},
    {"id": "CUS1002", "email": "priya.patel@email.com", "phone": "+91-9876543211", "first_name": "Priya", "last_name": "Patel"},
    {"id": "CUS1003", "email": "rahul.gupta@email.com", "phone": "+91-9876543212", "first_name": "Rahul", "last_name": "Gupta"},
    {"id": "CUS1004", "email": "sneha.reddy@email.com", "phone": "+91-9876543213", "first_name": "Sneha", "last_name": "Reddy"},
    {"id": "CUS1005", "email": "vikram.singh@email.com", "phone": "+91-9876543214", "first_name": "Vikram", "last_name": "Singh"},
    {"id": "CUS1006", "email": "meera.nair@email.com", "phone": "+91-9876543215", "first_name": "Meera", "last_name": "Nair"},
    {"id": "CUS1007", "email": "amit.kumar@email.com", "phone": "+91-9876543216", "first_name": "Amit", "last_name": "Kumar"},
    {"id": "CUS1008", "email": "divya.joshi@email.com", "phone": "+91-9876543217", "first_name": "Divya", "last_name": "Joshi"},
    {"id": "CUS1009", "email": "karthik.menon@email.com", "phone": "+91-9876543218", "first_name": "Karthik", "last_name": "Menon"},
    {"id": "CUS1010", "email": "ananya.das@email.com", "phone": "+91-9876543219", "first_name": "Ananya", "last_name": "Das"},
    {"id": "CUS1011", "email": "rohan.mehta@email.com", "phone": "+91-9876543220", "first_name": "Rohan", "last_name": "Mehta"},
    {"id": "CUS1012", "email": "kavita.jain@email.com", "phone": "+91-9876543221", "first_name": "Kavita", "last_name": "Jain"},
    {"id": "CUS1013", "email": "suresh.rao@email.com", "phone": "+91-9876543222", "first_name": "Suresh", "last_name": "Rao"},
    {"id": "CUS1014", "email": "pooja.iyer@email.com", "phone": "+91-9876543223", "first_name": "Pooja", "last_name": "Iyer"},
    {"id": "CUS1015", "email": "deepak.verma@email.com", "phone": "+91-9876543224", "first_name": "Deepak", "last_name": "Verma"},
    {"id": "CUS1016", "email": "neha.bhat@email.com", "phone": "+91-9876543225", "first_name": "Neha", "last_name": "Bhat"},
    {"id": "CUS1017", "email": "manoj.tiwari@email.com", "phone": "+91-9876543226", "first_name": "Manoj", "last_name": "Tiwari"},
    {"id": "CUS1018", "email": "shruti.kapoor@email.com", "phone": "+91-9876543227", "first_name": "Shruti", "last_name": "Kapoor"},
    {"id": "CUS1019", "email": "varun.chopra@email.com", "phone": "+91-9876543228", "first_name": "Varun", "last_name": "Chopra"},
    {"id": "CUS1020", "email": "ritu.sinha@email.com", "phone": "+91-9876543229", "first_name": "Ritu", "last_name": "Sinha"},
]

# ---------- Products ----------
PRODUCTS = [
    {"id": "PRD1001", "name": "iPhone 15 Pro Max", "category": "smartphone", "brand": "Apple", "price": 159900.00, "stock_quantity": 50, "warranty_months": 12, "description": "Apple iPhone 15 Pro Max with A17 Pro chip."},
    {"id": "PRD1002", "name": "Samsung Galaxy S24 Ultra", "category": "smartphone", "brand": "Samsung", "price": 134999.00, "stock_quantity": 45, "warranty_months": 12, "description": "Samsung Galaxy S24 Ultra with Galaxy AI."},
    {"id": "PRD1003", "name": "OnePlus 12", "category": "smartphone", "brand": "OnePlus", "price": 64999.00, "stock_quantity": 60, "warranty_months": 12, "description": "OnePlus 12 with Snapdragon 8 Gen 3."},
    {"id": "PRD1004", "name": "Google Pixel 8 Pro", "category": "smartphone", "brand": "Google", "price": 89999.00, "stock_quantity": 30, "warranty_months": 24, "description": "Google Pixel 8 Pro with Tensor G3."},
    {"id": "PRD1005", "name": "Xiaomi 14", "category": "smartphone", "brand": "Xiaomi", "price": 49999.00, "stock_quantity": 80, "warranty_months": 12, "description": "Xiaomi 14 with Leica optics."},
    {"id": "PRD1006", "name": "MacBook Pro 14 M3 Pro", "category": "laptop", "brand": "Apple", "price": 199900.00, "stock_quantity": 25, "warranty_months": 12, "description": "Apple MacBook Pro 14-inch with M3 Pro chip."},
    {"id": "PRD1007", "name": "Dell XPS 15", "category": "laptop", "brand": "Dell", "price": 149999.00, "stock_quantity": 30, "warranty_months": 12, "description": "Dell XPS 15 with Intel Core i9, OLED display."},
    {"id": "PRD1008", "name": "Lenovo ThinkPad X1 Carbon", "category": "laptop", "brand": "Lenovo", "price": 169999.00, "stock_quantity": 20, "warranty_months": 36, "description": "Lenovo ThinkPad X1 Carbon Gen 11, business laptop."},
    {"id": "PRD1009", "name": "ASUS ROG Strix G16", "category": "laptop", "brand": "ASUS", "price": 129999.00, "stock_quantity": 35, "warranty_months": 12, "description": "ASUS ROG Strix G16 gaming laptop, RTX 4070."},
    {"id": "PRD1010", "name": "HP Spectre x360", "category": "laptop", "brand": "HP", "price": 134999.00, "stock_quantity": 25, "warranty_months": 12, "description": "HP Spectre x360 2-in-1 laptop, touchscreen."},
    {"id": "PRD1011", "name": "AirPods Pro 2nd Gen", "category": "headphones", "brand": "Apple", "price": 24900.00, "stock_quantity": 100, "warranty_months": 12, "description": "Apple AirPods Pro 2nd generation with USB-C."},
    {"id": "PRD1012", "name": "Sony WH-1000XM5", "category": "headphones", "brand": "Sony", "price": 29990.00, "stock_quantity": 75, "warranty_months": 12, "description": "Sony WH-1000XM5 wireless noise cancelling headphones."},
    {"id": "PRD1013", "name": "Bose QuietComfort Ultra", "category": "headphones", "brand": "Bose", "price": 34990.00, "stock_quantity": 50, "warranty_months": 12, "description": "Bose QC Ultra headphones with spatial audio."},
    {"id": "PRD1014", "name": "Sennheiser Momentum 4", "category": "headphones", "brand": "Sennheiser", "price": 27990.00, "stock_quantity": 40, "warranty_months": 24, "description": "Sennheiser Momentum 4 Wireless, 60-hour battery."},
    {"id": "PRD1015", "name": "JBL Tune 770NC", "category": "headphones", "brand": "JBL", "price": 7999.00, "stock_quantity": 120, "warranty_months": 12, "description": "JBL Tune 770NC wireless headphones."},
    {"id": "PRD1016", "name": "Apple Watch Series 9", "category": "smartwatch", "brand": "Apple", "price": 44900.00, "stock_quantity": 60, "warranty_months": 12, "description": "Apple Watch Series 9 with S9 chip."},
    {"id": "PRD1017", "name": "Samsung Galaxy Watch 6", "category": "smartwatch", "brand": "Samsung", "price": 29999.00, "stock_quantity": 55, "warranty_months": 12, "description": "Samsung Galaxy Watch 6 with health monitoring."},
    {"id": "PRD1018", "name": "Garmin Venu 3", "category": "smartwatch", "brand": "Garmin", "price": 42990.00, "stock_quantity": 30, "warranty_months": 12, "description": "Garmin Venu 3 AMOLED smartwatch."},
    {"id": "PRD1019", "name": "Fitbit Charge 6", "category": "smartwatch", "brand": "Fitbit", "price": 14999.00, "stock_quantity": 90, "warranty_months": 12, "description": "Fitbit Charge 6 advanced fitness tracker."},
    {"id": "PRD1020", "name": "OnePlus Watch 2", "category": "smartwatch", "brand": "OnePlus", "price": 22999.00, "stock_quantity": 45, "warranty_months": 12, "description": "OnePlus Watch 2 with Wear OS."},
    {"id": "PRD1021", "name": "Anker 65W GaN Charger", "category": "accessories", "brand": "Anker", "price": 3499.00, "stock_quantity": 200, "warranty_months": 18, "description": "Anker 65W GaN USB-C charger."},
    {"id": "PRD1022", "name": "Spigen Case for iPhone 15 Pro", "category": "accessories", "brand": "Spigen", "price": 1299.00, "stock_quantity": 150, "warranty_months": 6, "description": "Spigen Ultra Hybrid case for iPhone 15 Pro."},
    {"id": "PRD1023", "name": "Belkin 3-in-1 Wireless Charger", "category": "accessories", "brand": "Belkin", "price": 8999.00, "stock_quantity": 60, "warranty_months": 12, "description": "Belkin 3-in-1 MagSafe wireless charging pad."},
    {"id": "PRD1024", "name": "Samsung 256GB USB-C Flash Drive", "category": "accessories", "brand": "Samsung", "price": 2499.00, "stock_quantity": 300, "warranty_months": 60, "description": "Samsung BAR Plus 256GB USB-C flash drive."},
    {"id": "PRD1025", "name": "Logitech MX Master 3S Mouse", "category": "accessories", "brand": "Logitech", "price": 8995.00, "stock_quantity": 80, "warranty_months": 12, "description": "Logitech MX Master 3S wireless mouse."},
]


async def seed_database():
    """Populate the database with demo data (idempotent - safe to run multiple times)."""
    import random as _random
    from datetime import timedelta
    from app.database.database import db_manager
    from app.database import (
        Order, OrderItem, Payment, Shipment, Refund,
        SupportTicket, Approval, Customer, Product,
        OrderStatus, PaymentStatus, ShipmentStatus,
        TicketStatus, ApprovalStatus, ApprovalActionType,
    )
    from sqlalchemy import select, func
    await db_manager.initialize()
    async with db_manager.session() as session:
        # Check if already seeded
        result = await session.execute(select(func.count(Customer.id)))
        if result.scalar() > 0:
            print("Database already seeded, skipping.")
            return

        for c in CUSTOMERS:
            session.add(Customer(**c))
        for p in PRODUCTS:
            session.add(Product(**p))
        await session.flush()
        now = datetime.utcnow()
        counter = [0]
        prod_map = {p["id"]: p for p in PRODUCTS}

        def _order(cid, pids, status, days, ship_st, pay_meth, addr, notes=None, delivered=False, shipped=True):
            counter[0] += 1
            oid = f"TK{10000 + counter[0]}"
            created = now - timedelta(days=days)
            plist = [prod_map[pid] for pid in pids]
            total = sum(p["price"] for p in plist)
            order = Order(id=oid, customer_id=cid, status=OrderStatus(status), total_amount=total,
                          shipping_address=addr, billing_address=addr, notes=notes, created_at=created,
                          shipped_at=created + timedelta(days=2) if shipped else None,
                          delivered_at=created + timedelta(days=5) if delivered else None)
            session.add(order)
            for p in plist:
                session.add(OrderItem(order_id=oid, product_id=p["id"], quantity=1,
                                      unit_price=p["price"], total_price=p["price"]))
            pid = f"PAY{1000 + counter[0]}"
            ps = PaymentStatus.COMPLETED if shipped else PaymentStatus.PENDING
            if "refunded" in status.lower():
                ps = PaymentStatus.REFUNDED
            session.add(Payment(id=pid, order_id=oid, amount=total, status=ps,
                                payment_method=pay_meth, transaction_id=f"TXN{100000+counter[0]}",
                                paid_at=created if shipped else None))
            ship_st_map = {"delivered": ShipmentStatus.DELIVERED, "in_transit": ShipmentStatus.IN_TRANSIT,
                           "out_for_delivery": ShipmentStatus.OUT_FOR_DELIVERY, "pending": ShipmentStatus.PENDING}
            session.add(Shipment(id=f"SHP{1000+counter[0]}", order_id=oid,
                                 tracking_number=f"TT{200000+counter[0]}", carrier="TechKart Express",
                                 status=ship_st_map.get(ship_st, ShipmentStatus.PENDING),
                                 shipped_at=created+timedelta(days=1) if shipped else None,
                                 estimated_delivery=created+timedelta(days=5),
                                 delivered_at=created+timedelta(days=5) if delivered else None,
                                 tracking_url=f"https://track.techkart.com/{oid}"))
            return oid, pid, total

        # CUS1001 orders (demo customer - various scenarios)
        o1, p1, t1 = _order("CUS1001", ["PRD1001"], "SHIPPED", 3, "in_transit", "credit_card", "12 MG Road, Bengaluru 560001")
        o2, p2, t2 = _order("CUS1001", ["PRD1006"], "DELIVERED", 15, "delivered", "credit_card", "12 MG Road, Bengaluru 560001")
        o3, p3, t3 = _order("CUS1001", ["PRD1011", "PRD1021"], "SHIPPED", 2, "in_transit", "upi", "12 MG Road, Bengaluru", notes="Gift wrap requested")
        o4, p4, t4 = _order("CUS1001", ["PRD1005"], "REFUNDED", 10, "delivered", "credit_card", "12 MG Road, Bengaluru")
        o5, p5, t5 = _order("CUS1001", ["PRD1016"], "DELIVERED", 45, "delivered", "credit_card", "12 MG Road, Bengaluru")

        # Other customers
        _order("CUS1002", ["PRD1002"], "SHIPPED", 1, "in_transit", "upi", "45 Park Street, Kolkata")
        _order("CUS1002", ["PRD1012", "PRD1023"], "CONFIRMED", 0, "pending", "netbanking", "45 Park Street, Kolkata")
        _order("CUS1003", ["PRD1009"], "DELIVERED", 20, "delivered", "credit_card", "78 Civil Lines, Delhi")
        _order("CUS1003", ["PRD1013"], "CANCELLED", 5, "pending", "credit_card", "78 Civil Lines, Delhi")
        _order("CUS1004", ["PRD1003", "PRD1015", "PRD1024"], "SHIPPED", 4, "out_for_delivery", "upi", "23 Jubilee Hills, Hyderabad")
        _order("CUS1005", ["PRD1007"], "PROCESSING", 1, "pending", "credit_card", "90 Banjara Hills, Hyderabad")
        _order("CUS1006", ["PRD1017", "PRD1019"], "DELIVERED", 30, "delivered", "upi", "15 Marine Drive, Mumbai")
        _order("CUS1007", ["PRD1004"], "SHIPPED", 2, "in_transit", "credit_card", "34 Koramangala, Bengaluru")
        _order("CUS1008", ["PRD1010"], "CONFIRMED", 0, "pending", "cod", "56 Anna Nagar, Chennai")
        _order("CUS1009", ["PRD1014"], "DELIVERED", 60, "delivered", "credit_card", "78 Ernakulam, Kochi")
        _order("CUS1010", ["PRD1008"], "SHIPPED", 1, "in_transit", "netbanking", "12 Salt Lake, Kolkata")
        _order("CUS1011", ["PRD1022"], "DELIVERED", 12, "delivered", "upi", "33 Andheri West, Mumbai")
        _order("CUS1012", ["PRD1001", "PRD1021"], "SHIPPED", 3, "in_transit", "credit_card", "89 Gurgaon, Haryana")
        _order("CUS1013", ["PRD1018"], "DELIVERED", 25, "delivered", "netbanking", "45 Jaipur, Rajasthan")
        _order("CUS1014", ["PRD1002"], "REFUNDED", 20, "delivered", "credit_card", "67 Pune, Maharashtra")
        _order("CUS1015", ["PRD1006", "PRD1025"], "SHIPPED", 1, "in_transit", "credit_card", "23 Noida, UP")
        _order("CUS1016", ["PRD1011"], "CANCELLED", 7, "pending", "upi", "11 Chandigarh")
        _order("CUS1017", ["PRD1003", "PRD1016"], "CONFIRMED", 0, "pending", "cod", "55 Lucknow, UP")
        _order("CUS1018", ["PRD1012"], "DELIVERED", 40, "delivered", "credit_card", "78 Indore, MP")
        _order("CUS1019", ["PRD1020", "PRD1024"], "SHIPPED", 2, "out_for_delivery", "upi", "90 Ahmedabad, Gujarat")
        _order("CUS1020", ["PRD1009", "PRD1013", "PRD1023"], "PROCESSING", 1, "pending", "credit_card", "45 Nagpur, Maharashtra")
        await session.flush()

        # Refunds
        session.add(Refund(id="REF1001", order_id="TK10004", payment_id="PAY10004", amount=49999.00,
                           reason="Damaged product received", status=PaymentStatus.COMPLETED,
                           approved_by="AGENT001", approved_at=now-timedelta(days=5), processed_at=now-timedelta(days=4)))
        session.add(Refund(id="REF1002", order_id="TK10014", payment_id="PAY10014", amount=134999.00,
                           reason="Product not as described", status=PaymentStatus.COMPLETED,
                           approved_by="AGENT001", approved_at=now-timedelta(days=3), processed_at=now-timedelta(days=2)))

        # Support Tickets
        tickets = [
            ("TCK1001", "CUS1001", "TK10001", "Damaged iPhone received", "Screen has scratches from delivery", "OPEN", "high"),
            ("TCK1002", "CUS1001", "TK10004", "Refund not received", "Returned item but no refund", "IN_PROGRESS", "medium"),
            ("TCK1003", "CUS1002", None, "Payment failed but debited", "Payment debited but order pending", "WAITING_FOR_CUSTOMER", "high"),
            ("TCK1004", "CUS1003", "TK10008", "Cancellation not reflected", "Cancelled order but status unchanged", "RESOLVED", "medium"),
            ("TCK1005", "CUS1004", None, "Warranty claim - OnePlus 12", "Battery draining fast", "OPEN", "medium"),
            ("TCK1006", "CUS1005", None, "Order not shipped", "No shipping update after 2 days", "OPEN", "low"),
            ("TCK1007", "CUS1006", "TK10006", "Wrong product delivered", "Received wrong watch model", "IN_PROGRESS", "urgent"),
            ("TCK1008", "CUS1009", "TK10009", "Headphone warranty", "Left ear stopped working", "OPEN", "medium"),
            ("TCK1009", "CUS1010", None, "Bulk order inquiry", "Need 10 ThinkPads for office", "OPEN", "low"),
            ("TCK1010", "CUS1014", "TK10014", "Refund status inquiry", "When will refund arrive?", "WAITING_FOR_CUSTOMER", "medium"),
        ]
        for tid, cid, oid, subj, desc, st, pri in tickets:
            session.add(SupportTicket(id=tid, customer_id=cid, order_id=oid, subject=subj,
                                      description=desc, status=TicketStatus(st), priority=pri,
                                      created_at=now-timedelta(days=_random.randint(1,15))))

        # Approvals
        approvals = [
            ("APR1001", "thread-cus1001-1", "CUS1001", "TK10001", ApprovalActionType.REFUND, 159900.00, "Damaged product", ApprovalStatus.EXECUTED, "Damaged iPhone. Within refund window."),
            ("APR1002", "thread-cus1001-3", "CUS1001", "TK10004", ApprovalActionType.REFUND, 49999.00, "Damaged Xiaomi 14", ApprovalStatus.EXECUTED, "Refund already processed."),
            ("APR1003", "thread-cus1014-1", "CUS1014", "TK10014", ApprovalActionType.REFUND, 134999.00, "Product not as described", ApprovalStatus.EXECUTED, "Refund processed."),
            ("APR1004", "thread-demo-pending", "CUS1001", "TK10005", ApprovalActionType.REFUND, 44900.00, "Apple Watch malfunction", ApprovalStatus.PENDING, "Product malfunction within warranty. Eligible for refund."),
        ]
        for aid, thid, cid, oid, atype, amt, reason, st, summary in approvals:
            session.add(Approval(id=aid, thread_id=thid, customer_id=cid, order_id=oid, action_type=atype,
                                 requested_amount=amt, requested_reason=reason, status=st,
                                 ai_reasoning_summary=summary, created_at=now-timedelta(days=_random.randint(1,5))))

        await session.flush()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())