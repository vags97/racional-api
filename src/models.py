from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Float)
    
    transactions = relationship("Transaction", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")

class Stock(Base):
    __tablename__ = 'stock'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock = Column(String, nullable=False)
    quantity = Column(Integer)
    hashed_password = Column(String)
    unit_value = Column(Float)
    
    portfolio_stocks = relationship("PortfolioStock", back_populates="stock")
    buy_orders = relationship("BuyOrder", back_populates="stock")
    sell_orders = relationship("SellOrder", back_populates="stock")

class Transaction(Base):
    __tablename__ = 'transaction'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime)
    
    user = relationship("User", back_populates="transactions")

class Portfolio(Base):
    __tablename__ = 'portafolio'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    portafolio = Column(String)
    
    user = relationship("User", back_populates="portfolios")
    portfolio_stocks = relationship("PortfolioStock", back_populates="portfolio")
    buy_orders = relationship("BuyOrder", back_populates="portfolio")
    sell_orders = relationship("SellOrder", back_populates="portfolio")

class PortfolioStock(Base):
    __tablename__ = 'portafolio_stock'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    portafolio_id = Column(Integer, ForeignKey('portafolio.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    quantity = Column(Integer)
    
    portfolio = relationship("Portfolio", back_populates="portfolio_stocks")
    stock = relationship("Stock", back_populates="portfolio_stocks")

class Broker(Base):
    __tablename__ = 'broker'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    broker = Column(String)
    
    buy_orders = relationship("BuyOrder", back_populates="broker")
    sell_orders = relationship("SellOrder", back_populates="broker")

class BuyOrder(Base):
    __tablename__ = 'buy_order'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    portafolio_id = Column(Integer, ForeignKey('portafolio.id'), nullable=False)
    broker_id = Column(Integer, ForeignKey('broker.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    amount = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    state = Column(String)
    timestamp = Column(DateTime)
    
    portfolio = relationship("Portfolio", back_populates="buy_orders")
    broker = relationship("Broker", back_populates="buy_orders")
    stock = relationship("Stock", back_populates="buy_orders")

class SellOrder(Base):
    __tablename__ = 'sell_order'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    portafolio_id = Column(Integer, ForeignKey('portafolio.id'), nullable=False)
    broker_id = Column(Integer, ForeignKey('broker.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    amount = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    state = Column(String)
    timestamp = Column(DateTime)
    
    portfolio = relationship("Portfolio", back_populates="sell_orders")
    broker = relationship("Broker", back_populates="sell_orders")
    stock = relationship("Stock", back_populates="sell_orders")