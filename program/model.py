from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Date, Time, ForeignKey, Boolean, Table, DateTime
from sqlalchemy.orm import relationship
from flask_login import UserMixin

Base = declarative_base()


class Archetype(Base):
    __tablename__ = 'archetype'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    person = relationship('Person', backref='archetype')


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    author = Column(String(32))
    person = relationship('Person', backref='book')


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    prec = Column(Float)
    book_id = Column(Integer, ForeignKey('book.id'))
    archetype_id = Column(Integer, ForeignKey('archetype.id'))

class User(UserMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(256))
