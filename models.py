from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer'
    customerID = Column(Integer, primary_key=True)
    lastName = Column(String(64), index=True)
    firstName = Column(String(64), index=True)
    title = Column(String(32))
    email = Column(String(120), nullable=False, index=True, unique=True)
    orderID = relationship("Order", backref="customer")

    @property
    def serialize(self):
        """
        Return object data in a serializeable format
        """
        return {
            'customerID': self.customerID,
            'lastName': self.lastName,
            'firstName': self.firstName,
            'title': self.title,
            'email': self.email,
            'orderID': self.orderID
        }


class Order(Base):
    __tablename__ = 'order'
    orderID = Column(Integer, primary_key=True)
    item = Column(String(64), nullable=False)
    name = Column(String(64))
    dob = Column(String(32))
    height = Column(Integer)
    weight = Column(Integer)
    message = Column(String(300))
    #isOrdered = Column(Boolean, unique=False, default=False)
    #dateOrdered = Column(TIMESTAMP(timezone=True))
    customer_ID = Column(Integer, ForeignKey(
        "customer.customerID"))

    @property
    def serialize(self):
        """
        Return object data in a serializeable format
        """
        return {
            'orderID': self.orderID,
            'item': self.item,
            'name': self.name,
            'dob': self.dob,
            'height': self.height,
            'weight': self.weight,
            'message': self.message,
            # 'isOrdered': self.isOrdered,
            # 'dateOrdered': self.dateOrdered,
            'customer_ID': self.customer_ID
        }


engine = create_engine('sqlite:///models.db?check_same_thread=False')

Base.metadata.create_all(engine)
