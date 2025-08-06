from src.database import SessionLocal
from src.config import  pwd_context
from src.models import User, Broker, Portfolio, Stock

def create_examples():
    db = SessionLocal()
    try:
        # Create test user if not exists
        user_data = User(
            username="john_doe",
            email="example@example.dev",
            hashed_password=pwd_context.hash('123456'),
            balance=10000.0  # Increased balance for testing
        )
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if not existing_user:
            db.add(user_data)
            db.commit()
            db.refresh(user_data)
            print("✅ Created test user")
        else:
            user_data = existing_user
            print("⏩ Using existing user")

        # Create example brokers
        brokers = [
            Broker(broker="Interactive Brokers"),
            Broker(broker="Charles Schwab"),
            Broker(broker="Fidelity Investments")
        ]
        for broker in brokers:
            if not db.query(Broker).filter(Broker.broker == broker.broker).first():
                db.add(broker)
        db.commit()
        print("✅ Created brokers")

        # Create example portfolios for the user
        portfolios = [
            Portfolio(user_id=user_data.id, portafolio="Retirement Account"),
            Portfolio(user_id=user_data.id, portafolio="Trading Account"),
            Portfolio(user_id=user_data.id, portafolio="Long-Term Holdings")
        ]
        for portfolio in portfolios:
            if not db.query(Portfolio).filter(
                (Portfolio.user_id == portfolio.user_id) & 
                (Portfolio.portafolio == portfolio.portafolio)
            ).first():
                db.add(portfolio)
        db.commit()
        print("✅ Created portfolios")

        # Create example stocks
        stocks = [
            Stock(stock="AAPL", quantity=100, unit_value=175.50),
            Stock(stock="MSFT", quantity=50, unit_value=325.25),
            Stock(stock="TSLA", quantity=30, unit_value=250.75),
            Stock(stock="AMZN", quantity=20, unit_value=150.30),
            Stock(stock="GOOGL", quantity=15, unit_value=135.40)
        ]
        for stock in stocks:
            if not db.query(Stock).filter(Stock.stock == stock.stock).first():
                db.add(stock)
        db.commit()
        print("✅ Created stocks")

        print("🎉 Example data creation complete!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating examples: {str(e)}")
    finally:
        db.close()