import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    # We added this serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
        }

class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    # We added this serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
        }


engine = create_engine('sqlite:///suzymakeup.db')


Base.metadata.create_all(engine)
