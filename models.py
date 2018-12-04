from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer'
    customerID = Column(Integer, primary_key=True)
    lastName = Column(String(32), nullable=False)
    firstName = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    #orderIDs = relationship("Order")

    @property
    def serialize(self):
        """
        Return object data in a serializeable format
        """
        return {
            'customerID': self.customerID,
            'lastName': self.lastName,
            'firstName': self.firstName,
            'email': self.email,
        }


class Order(Base):
    __tablename__ = 'order'
    orderID = Column(Integer, primary_key=True)
    item = Column(String(64), nullable=False)
    dob = Column(String(32))
    height = Column(Integer)
    weight = Column(Integer)
    message = Column(String(130))
    #customer_ID = Column(Integer, ForeignKey('customer.customerID'))

    @property
    def serialize(self):
        """
        Return object data in a serializeable format
        """
        return {
            'orderID': self.orderID,
            'item': self.item,
            'dob': self.dob,
            'height': self.height,
            'weight': self.weight,
            'message': self.message,
            # 'customer_ID': self.customer_ID
        }


engine = create_engine('sqlite:///models.db?check_same_thread=False')

Base.metadata.create_all(engine)
