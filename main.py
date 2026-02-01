"""
💰 CAS Financial Literacy App
============================
IB CAS Project - Financial Education & Market Analysis

A comprehensive financial literacy application that teaches students 
about stocks, investing, and market analysis using real-world data.
"""

import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich import print as rprint
import questionary
from questionary import Style

# Initialize Rich console
console = Console()

# Custom style for questionary
custom_style = Style([
    ('qmark', 'fg:yellow bold'),
    ('question', 'bold'),
    ('answer', 'fg:cyan bold'),
    ('pointer', 'fg:yellow bold'),
    ('highlighted', 'fg:yellow bold'),
    ('selected', 'fg:green'),
])

def display_banner():
    """Display the app banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   💰 CAS FINANCIAL LITERACY APP 💰                               ║
║                                                                  ║
║   Learn Stocks • Investing • Market Analysis                     ║
║   Powered by OpenBB - Your Free Bloomberg Alternative            ║
║                                                                  ║
║   IB CAS Project - Financial Education                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def main_menu():
    """Display the main menu and handle user selection."""
    choices = [
        "📚 Financial Education Modules",
        "📈 Stock Analysis (OpenBB)",
        "💼 Portfolio Tracker",
        "🎯 Knowledge Quiz",
        "₿  Crypto Analysis",
        "📊 Stock Screener",
        "ℹ️  About OpenBB",
        "❌ Exit"
    ]
    
    return questionary.select(
        "What would you like to explore?",
        choices=choices,
        style=custom_style
    ).ask()

def education_menu():
    """Display education module menu."""
    from modules.education import EducationModule
    edu = EducationModule()
    
    while True:
        console.clear()
        display_banner()
        
        choices = [
            "📖 Module 1: Stock Market Basics",
            "💡 Module 2: Investment Fundamentals",
            "📊 Module 3: Technical Analysis",
            "📋 Module 4: Fundamental Analysis",
            "🏦 Module 5: Types of Investments",
            "⚠️  Module 6: Risk Management",
            "🔙 Back to Main Menu"
        ]
        
        selection = questionary.select(
            "Select a learning module:",
            choices=choices,
            style=custom_style
        ).ask()
        
        if "Module 1" in selection:
            edu.stock_market_basics()
        elif "Module 2" in selection:
            edu.investment_fundamentals()
        elif "Module 3" in selection:
            edu.technical_analysis()
        elif "Module 4" in selection:
            edu.fundamental_analysis()
        elif "Module 5" in selection:
            edu.types_of_investments()
        elif "Module 6" in selection:
            edu.risk_management()
        elif "Back" in selection:
            break
        
        if "Back" not in selection:
            input("\n\nPress Enter to continue...")

def stock_analysis_menu():
    """Display stock analysis menu using OpenBB."""
    from modules.stock_analysis import StockAnalyzer
    analyzer = StockAnalyzer()
    
    while True:
        console.clear()
        display_banner()
        
        choices = [
            "🔍 Analyze a Stock",
            "📊 Compare Multiple Stocks",
            "📈 Technical Analysis Dashboard",
            "📰 Latest Market News",
            "🔙 Back to Main Menu"
        ]
        
        selection = questionary.select(
            "Stock Analysis Options:",
            choices=choices,
            style=custom_style
        ).ask()
        
        if "Analyze a Stock" in selection:
            symbol = questionary.text(
                "Enter stock ticker (e.g., AAPL, MSFT, TSLA):",
                style=custom_style
            ).ask()
            if symbol:
                analyzer.analyze_stock(symbol.upper())
        elif "Compare Multiple Stocks" in selection:
            symbols = questionary.text(
                "Enter stock tickers separated by comma (e.g., AAPL, MSFT, GOOGL):",
                style=custom_style
            ).ask()
            if symbols:
                symbol_list = [s.strip().upper() for s in symbols.split(',')]
                analyzer.compare_stocks(symbol_list)
        elif "Technical Analysis Dashboard" in selection:
            symbol = questionary.text(
                "Enter stock ticker for technical analysis:",
                style=custom_style
            ).ask()
            if symbol:
                analyzer.technical_dashboard(symbol.upper())
        elif "Market News" in selection:
            analyzer.get_market_news()
        elif "Back" in selection:
            break
        
        if "Back" not in selection:
            input("\n\nPress Enter to continue...")

def portfolio_menu():
    """Display portfolio tracker menu."""
    from modules.portfolio_tracker import PortfolioTracker
    tracker = PortfolioTracker()
    
    while True:
        console.clear()
        display_banner()
        
        choices = [
            "📋 View Portfolio",
            "➕ Add Investment",
            "➖ Remove Investment",
            "📊 Portfolio Performance",
            "💾 Save Portfolio",
            "📂 Load Portfolio",
            "🔙 Back to Main Menu"
        ]
        
        selection = questionary.select(
            "Portfolio Options:",
            choices=choices,
            style=custom_style
        ).ask()
        
        if "View Portfolio" in selection:
            tracker.view_portfolio()
        elif "Add Investment" in selection:
            tracker.add_investment()
        elif "Remove Investment" in selection:
            tracker.remove_investment()
        elif "Portfolio Performance" in selection:
            tracker.show_performance()
        elif "Save Portfolio" in selection:
            tracker.save_portfolio()
        elif "Load Portfolio" in selection:
            tracker.load_portfolio()
        elif "Back" in selection:
            break
        
        if "Back" not in selection:
            input("\n\nPress Enter to continue...")

def quiz_menu():
    """Display quiz menu."""
    from modules.quiz import FinanceQuiz
    quiz = FinanceQuiz()
    
    while True:
        console.clear()
        display_banner()
        
        choices = [
            "🎯 Stock Market Basics Quiz",
            "🎯 Investment Fundamentals Quiz",
            "🎯 Technical Analysis Quiz",
            "🎯 Complete Assessment",
            "📊 View Quiz Scores",
            "🔙 Back to Main Menu"
        ]
        
        selection = questionary.select(
            "Quiz Options:",
            choices=choices,
            style=custom_style
        ).ask()
        
        if "Stock Market Basics" in selection:
            quiz.run_quiz("basics")
        elif "Investment Fundamentals" in selection:
            quiz.run_quiz("fundamentals")
        elif "Technical Analysis" in selection:
            quiz.run_quiz("technical")
        elif "Complete Assessment" in selection:
            quiz.run_quiz("complete")
        elif "View Quiz Scores" in selection:
            quiz.view_scores()
        elif "Back" in selection:
            break
        
        if "Back" not in selection:
            input("\n\nPress Enter to continue...")

def crypto_analysis():
    """Crypto analysis using OpenBB."""
    from modules.stock_analysis import StockAnalyzer
    analyzer = StockAnalyzer()
    
    while True:
        console.clear()
        display_banner()
        
        choices = [
            "₿  Bitcoin (BTC) Analysis",
            "Ξ  Ethereum (ETH) Analysis",
            "🔍 Analyze Other Crypto",
            "📊 Crypto Comparison",
            "🔙 Back to Main Menu"
        ]
        
        selection = questionary.select(
            "Cryptocurrency Analysis:",
            choices=choices,
            style=custom_style
        ).ask()
        
        if "Bitcoin" in selection:
            analyzer.analyze_crypto("BTC")
        elif "Ethereum" in selection:
            analyzer.analyze_crypto("ETH")
        elif "Other Crypto" in selection:
            crypto = questionary.text(
                "Enter crypto symbol (e.g., SOL, ADA, XRP):",
                style=custom_style
            ).ask()
            if crypto:
                analyzer.analyze_crypto(crypto.upper())
        elif "Comparison" in selection:
            analyzer.crypto_comparison()
        elif "Back" in selection:
            break
        
        if "Back" not in selection:
            input("\n\nPress Enter to continue...")

def stock_screener():
    """Stock screener functionality."""
    from modules.stock_analysis import StockAnalyzer
    analyzer = StockAnalyzer()
    
    while True:
        console.clear()
        display_banner()
        
        choices = [
            "🔝 Top Gainers Today",
            "📉 Top Losers Today",
            "📊 Most Active Stocks",
            "💰 Dividend Champions",
            "🚀 Growth Stocks",
            "🔙 Back to Main Menu"
        ]
        
        selection = questionary.select(
            "Stock Screener Options:",
            choices=choices,
            style=custom_style
        ).ask()
        
        if "Top Gainers" in selection:
            analyzer.screen_stocks("gainers")
        elif "Top Losers" in selection:
            analyzer.screen_stocks("losers")
        elif "Most Active" in selection:
            analyzer.screen_stocks("active")
        elif "Dividend" in selection:
            analyzer.screen_stocks("dividend")
        elif "Growth" in selection:
            analyzer.screen_stocks("growth")
        elif "Back" in selection:
            break
        
        if "Back" not in selection:
            input("\n\nPress Enter to continue...")

def about_openbb():
    """Display information about OpenBB."""
    console.clear()
    display_banner()
    
    info = """
# 🔷 About OpenBB

## What is OpenBB?

OpenBB is an **open-source financial data platform** that serves as a free alternative 
to Bloomberg Terminal (which costs $30,000/year!).

## Features:
- **Real-time and historical market data** from multiple sources
- **Comprehensive macro and microeconomic indicators**
- **Technical analysis tools** and charting capabilities
- **Portfolio analytics** and risk management features
- **Full Python integration** for custom analysis and automation

## Why Use OpenBB?

| Feature | Bloomberg Terminal | OpenBB |
|---------|-------------------|--------|
| Cost | $30,000/year | **FREE** |
| Data Sources | Proprietary | Multiple (Yahoo, Alpha Vantage, etc.) |
| Customization | Limited | **Full Python Access** |
| Open Source | No | **Yes** |

## Getting Started:

```python
from openbb import obb

# Get stock data
data = obb.equity.price.historical(symbol="AAPL")

# Get crypto data
btc = obb.crypto.price.historical(symbol="BTCUSD")
```

## Resources:
- Website: https://openbb.co
- Documentation: https://docs.openbb.co
- GitHub: https://github.com/OpenBB-finance/OpenBB
    """
    
    console.print(Markdown(info))

def main():
    """Main application loop."""
    console.clear()
    display_banner()
    
    console.print("\n[bold green]Welcome to the CAS Financial Literacy App![/bold green]")
    console.print("[dim]Learn about stocks, investing, and market analysis[/dim]\n")
    
    while True:
        console.clear()
        display_banner()
        
        selection = main_menu()
        
        if selection is None or "Exit" in selection:
            console.print("\n[bold cyan]Thank you for using the CAS Financial Literacy App![/bold cyan]")
            console.print("[dim]Keep learning and investing wisely! 📈[/dim]\n")
            break
        elif "Education" in selection:
            education_menu()
        elif "Stock Analysis" in selection:
            stock_analysis_menu()
        elif "Portfolio" in selection:
            portfolio_menu()
        elif "Quiz" in selection:
            quiz_menu()
        elif "Crypto" in selection:
            crypto_analysis()
        elif "Screener" in selection:
            stock_screener()
        elif "About OpenBB" in selection:
            about_openbb()
            input("\n\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]Goodbye! Keep learning about finance! 💰[/bold cyan]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]An error occurred: {e}[/bold red]")
        console.print("[dim]Make sure all dependencies are installed: pip install -r requirements.txt[/dim]")
        sys.exit(1)
