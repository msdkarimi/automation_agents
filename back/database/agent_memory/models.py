from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


__all__ = ['Base', 'Item', 'ItemSchema', 'ItemCreateSchema',
           'Purchase', 'PurchaseSchema', 'PurchaseCreateSchema', 
           'Ticket', 'TicketSchema', 'TicketCreateSchema']

Base = declarative_base()  # ONE base shared by all models

# here define your required model(s)...

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    item_id = Column(String, unique=True, nullable=False)
    item_name = Column(String, nullable=False)
    item_description = Column(String, nullable=False)  

    # Backref
    orders = relationship("Orders", back_populates="item")
    purchases = relationship("Purchase", back_populates="item")
    # payment = relationship("Payment", back_populates="payedItem")

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, unique=True, nullable=False)
    customer_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    last_purchase_date = Column(String, nullable=True)
    total_orders = Column(Integer, nullable=True)
    total_spent = Column(Integer, nullable=True)

    # Backref
    orders = relationship("Orders", back_populates="customer")
    purchases = relationship("Purchase", back_populates="customer")

class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    purchase_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=True)
    purchase_status = Column(String, nullable=False)
    purchased_item_id = Column(String, ForeignKey("items.item_id"), nullable=True)

        # Relationships
    customer = relationship("Customer", back_populates="purchases")
    item = relationship("Item", back_populates="purchases")
    orders = relationship("Orders", back_populates="purchase")

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=True)
    customer_comment = Column(String, nullable=False)
    status = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    date_received = Column(String, nullable=False)
    date_addressed = Column(String, nullable=True)


    
    ticket_links = relationship("TicketLink", back_populates="ticket", uselist=False)




class SOPCatalog(Base):
    __tablename__ = 'sopcatalogs'
    id = Column(Integer, primary_key=True)
    sopid = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String,ForeignKey("customers.customer_id"), nullable=True)
    purchase_id = Column(String, ForeignKey("purchases.purchase_id"), nullable=True)
    purchased_item_id = Column(String, ForeignKey("items.item_id"), nullable=True)
    order_number = Column(String, nullable=True)
    order_status = Column(String, nullable=False)
    order_date = Column(String, nullable=False)
    item_price = Column(Integer, nullable=False)

        # Relationships
    customer = relationship("Customer", back_populates="orders")
    purchase = relationship("Purchase", back_populates="orders")
    item = relationship("Item", back_populates="orders")


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    payment_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=True)
    purchase_id = Column(String, ForeignKey("purchases.purchase_id"), nullable=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=True)
    payment_amount = Column(Integer, nullable=False)
    payment_status = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    payment_date = Column(String, nullable=False)

    # Add these relationships
    purchase = relationship("Purchase")
    order = relationship("Orders")



class TicketLink(Base):
    __tablename__ = 'ticket_links'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)

    # One of the following will be filled
    purchase_id = Column(String, ForeignKey("purchases.purchase_id"), nullable=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=True)
    payment_id = Column(String, ForeignKey("payments.payment_id"), nullable=True)
    sop_id = Column(String, ForeignKey("sopcatalogs.sopid"), nullable=True)

    ticket = relationship("Ticket", back_populates="ticket_links")

class ItemSchema(BaseModel):
    id:int
    item_id: str
    item_name: str
    item_description: str
    
    model_config = ConfigDict(from_attributes=True)


class NewTicket(BaseModel):
    customer_id: str
    customer_comment: str
    status: str
    subject: str
    date_received: str
    date_addressed: str

    model_config = ConfigDict(from_attributes=True)


class SOPCatalogSchema(BaseModel):
    id: int
    sopid: str
    title: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class CustomerSchema(BaseModel):
    id:int
    customer_id: str
    customer_name: str
    email: str
    phone: str
    last_purchase_date: str
    total_orders: int
    total_spent: int

    model_config = ConfigDict(from_attributes=True)




class PurchaseSchema(BaseModel):
    id:int
    purchase_id: str
    customer_id: str
    purchase_status: str
    purchased_item_id: str

    # Relationships
    customer: Optional[CustomerSchema] = None
    item: Optional[ItemSchema] = None

    model_config = ConfigDict(from_attributes=True)


class OrdersSchema(BaseModel):
    id: int
    order_id: str
    customer_id: str
    purchase_id: str
    purchased_item_id: str
    order_number: Optional[str] = None
    order_status: str
    order_date: str
    item_price: int

    # Relationships
    customer: Optional[CustomerSchema] = None
    item: Optional[ItemSchema] = None
    purchase: Optional[PurchaseSchema] = None


    model_config = ConfigDict(from_attributes=True)


class PaymentSchema(BaseModel):
    id: int
    payment_id: str
    customer_id: str
    purchase_id: str
    order_id: str
    payment_amount: int
    payment_status: str
    payment_method: str
    payment_date: str

    # Relationships
    customer: Optional[CustomerSchema] = None
    item: Optional[OrdersSchema] = None
    purchase: Optional[PurchaseSchema] = None

    model_config = ConfigDict(from_attributes=True)


class TicketLinkSchema(BaseModel):

    id: int
    ticket_id:int 

    purchase_id:  Optional[str] = None
    order_id:  Optional[str] = None
    payment_id:  Optional[str] = None
    sop_id:  Optional[str] = None

    purchase: Optional[PurchaseSchema] = None
    order: Optional[OrdersSchema] = None
    payment: Optional[PaymentSchema] = None
    sop: Optional[SOPCatalogSchema] = None


    model_config = ConfigDict(from_attributes=True)



class TicketSchema(BaseModel):
    id: int
    customer_id: str
    customer_comment: str
    status: str
    subject: str
    date_received: str
    date_addressed: str

    ticket_links: Optional[TicketLinkSchema] = None
    
    model_config = ConfigDict(from_attributes=True)


class IgniteCaseContextAgentSchema(BaseModel):
    ticket_id: int
    customer_id: str
    customer_comment: str
