from src.database import SessionLocal
from src.config import pwd_context
from src.models import User, Broker, Portfolio, Stock, PortfolioStock

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
        portfolio_names = ["Retirement Account", "Trading Account", "Long-Term Holdings"]
        created_portfolios = []
        
        for name in portfolio_names:
            portfolio = db.query(Portfolio).filter(
                (Portfolio.user_id == user_data.id) & 
                (Portfolio.portfolio == name)
            ).first()
            
            if not portfolio:
                portfolio = Portfolio(user_id=user_data.id, portfolio=name)
                db.add(portfolio)
                db.commit()
                db.refresh(portfolio)
                print(f"✅ Created portfolio: {name}")
            else:
                print(f"⏩ Using existing portfolio: {name}")
            
            created_portfolios.append(portfolio)
        
        # Create example stocks
        stocks_data = [
            {"stock": "AAPL", "quantity": 100, "unit_value": 175.50},
            {"stock": "MSFT", "quantity": 50, "unit_value": 325.25},
            {"stock": "TSLA", "quantity": 30, "unit_value": 250.75},
            {"stock": "AMZN", "quantity": 20, "unit_value": 150.30},
            {"stock": "GOOGL", "quantity": 15, "unit_value": 135.40}
        ]
        
        created_stocks = []
        for data in stocks_data:
            stock = db.query(Stock).filter(Stock.stock == data["stock"]).first()
            
            if not stock:
                stock = Stock(
                    stock=data["stock"],
                    quantity=data["quantity"],
                    unit_value=data["unit_value"]
                )
                db.add(stock)
                db.commit()
                db.refresh(stock)
                print(f"✅ Created stock: {data['stock']}")
            else:
                print(f"⏩ Using existing stock: {data['stock']}")
            
            created_stocks.append(stock)
        
        # Add stocks to first portfolio (Retirement Account)
        if created_portfolios and created_stocks:
            first_portfolio = created_portfolios[0]
            
            # Add AAPL and MSFT to the portfolio with different quantities
            stocks_to_add = [
                {"stock": created_stocks[0], "quantity": 10, "average_price": 170.00},  # AAPL
                {"stock": created_stocks[1], "quantity": 5, "average_price": 320.00},   # MSFT
                {"stock": created_stocks[2], "quantity": 3, "average_price": 245.50}    # TSLA
            ]
            
            for item in stocks_to_add:
                # Check if stock already exists in portfolio
                existing = db.query(PortfolioStock).filter(
                    (PortfolioStock.portfolio_id == first_portfolio.id) &
                    (PortfolioStock.stock_id == item["stock"].id)
                ).first()
                
                if not existing:
                    portfolio_stock = PortfolioStock(
                        portfolio_id=first_portfolio.id,
                        stock_id=item["stock"].id,
                        quantity=item["quantity"]
                    )
                    db.add(portfolio_stock)
                    print(f"✅ Added {item['stock'].stock} to {first_portfolio.portfolio}")
                else:
                    print(f"⏩ {item['stock'].stock} already in {first_portfolio.portfolio}")
            
            db.commit()
        
        print("🎉 Example data creation complete!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating examples: {str(e)}")
        raise
    finally:
        db.close()