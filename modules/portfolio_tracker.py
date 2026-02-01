"""
💼 Portfolio Tracker Module
===========================
Track and manage investment portfolios.
"""

import json
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import questionary
from questionary import Style

console = Console()

custom_style = Style([
    ('qmark', 'fg:yellow bold'),
    ('question', 'bold'),
    ('answer', 'fg:cyan bold'),
])

class PortfolioTracker:
    """Manage investment portfolio."""
    
    def __init__(self):
        self.console = Console()
        self.portfolio = {}
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.portfolio_file = os.path.join(self.data_dir, 'portfolio.json')
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing portfolio
        self.load_portfolio(silent=True)
    
    def view_portfolio(self):
        """Display current portfolio."""
        self.console.print(Panel("[bold cyan]💼 Your Portfolio[/bold cyan]", expand=False))
        
        if not self.portfolio:
            self.console.print("\n[yellow]Your portfolio is empty![/yellow]")
            self.console.print("[dim]Add investments using 'Add Investment' option.[/dim]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan")
        table.add_column("Shares", justify="right")
        table.add_column("Avg Cost", justify="right")
        table.add_column("Total Cost", justify="right")
        table.add_column("Current Value*", justify="right")
        table.add_column("Gain/Loss*", justify="right")
        table.add_column("Date Added", justify="center")
        
        total_cost = 0
        total_value = 0
        
        for symbol, data in self.portfolio.items():
            shares = data['shares']
            avg_cost = data['avg_cost']
            cost_basis = shares * avg_cost
            total_cost += cost_basis
            
            # Try to get current price
            current_price = self._get_current_price(symbol)
            if current_price:
                current_value = shares * current_price
                total_value += current_value
                gain_loss = current_value - cost_basis
                gain_loss_pct = (gain_loss / cost_basis) * 100
                color = "green" if gain_loss >= 0 else "red"
                
                table.add_row(
                    symbol,
                    f"{shares:,.2f}",
                    f"${avg_cost:,.2f}",
                    f"${cost_basis:,.2f}",
                    f"${current_value:,.2f}",
                    f"[{color}]${gain_loss:+,.2f} ({gain_loss_pct:+.1f}%)[/{color}]",
                    data.get('date_added', 'N/A')
                )
            else:
                total_value += cost_basis  # Assume no change if can't fetch
                table.add_row(
                    symbol,
                    f"{shares:,.2f}",
                    f"${avg_cost:,.2f}",
                    f"${cost_basis:,.2f}",
                    "[dim]N/A[/dim]",
                    "[dim]N/A[/dim]",
                    data.get('date_added', 'N/A')
                )
        
        self.console.print(table)
        
        # Portfolio summary
        self.console.print("\n[bold yellow]📊 Portfolio Summary[/bold yellow]")
        summary = Table(show_header=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", justify="right")
        
        summary.add_row("Total Cost Basis", f"${total_cost:,.2f}")
        summary.add_row("Current Value*", f"${total_value:,.2f}")
        
        total_gain = total_value - total_cost
        if total_cost > 0:
            total_gain_pct = (total_gain / total_cost) * 100
            color = "green" if total_gain >= 0 else "red"
            summary.add_row("Total Gain/Loss*", f"[{color}]${total_gain:+,.2f} ({total_gain_pct:+.1f}%)[/{color}]")
        
        summary.add_row("Positions", f"{len(self.portfolio)}")
        
        self.console.print(summary)
        self.console.print("\n[dim]*Current values require internet connection and OpenBB[/dim]")
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        try:
            from openbb import obb
            from datetime import datetime, timedelta
            
            data = obb.equity.price.historical(
                symbol=symbol,
                provider="yfinance",
                start_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
            ).to_df()
            
            if data is not None and not data.empty:
                return data['close'].iloc[-1]
        except:
            pass
        return None
    
    def add_investment(self):
        """Add a new investment to portfolio."""
        self.console.print(Panel("[bold cyan]➕ Add Investment[/bold cyan]", expand=False))
        
        symbol = questionary.text(
            "Enter stock/crypto symbol (e.g., AAPL, BTC):",
            style=custom_style
        ).ask()
        
        if not symbol:
            return
        
        symbol = symbol.upper()
        
        try:
            shares = float(questionary.text(
                "Number of shares/units:",
                style=custom_style
            ).ask())
            
            cost_per_share = float(questionary.text(
                "Cost per share/unit ($):",
                style=custom_style
            ).ask())
        except (ValueError, TypeError):
            self.console.print("[bold red]Invalid input. Please enter numbers.[/bold red]")
            return
        
        if symbol in self.portfolio:
            # Update existing position (average cost)
            existing = self.portfolio[symbol]
            total_shares = existing['shares'] + shares
            total_cost = (existing['shares'] * existing['avg_cost']) + (shares * cost_per_share)
            new_avg_cost = total_cost / total_shares
            
            self.portfolio[symbol] = {
                'shares': total_shares,
                'avg_cost': new_avg_cost,
                'date_added': existing['date_added']
            }
            self.console.print(f"\n[green]✅ Updated {symbol} position![/green]")
            self.console.print(f"   New total: {total_shares} shares @ ${new_avg_cost:.2f} avg cost")
        else:
            # Add new position
            self.portfolio[symbol] = {
                'shares': shares,
                'avg_cost': cost_per_share,
                'date_added': datetime.now().strftime("%Y-%m-%d")
            }
            self.console.print(f"\n[green]✅ Added {symbol} to portfolio![/green]")
            self.console.print(f"   {shares} shares @ ${cost_per_share:.2f} per share")
    
    def remove_investment(self):
        """Remove an investment from portfolio."""
        self.console.print(Panel("[bold cyan]➖ Remove Investment[/bold cyan]", expand=False))
        
        if not self.portfolio:
            self.console.print("[yellow]Your portfolio is empty![/yellow]")
            return
        
        choices = list(self.portfolio.keys()) + ["Cancel"]
        
        symbol = questionary.select(
            "Select investment to remove:",
            choices=choices,
            style=custom_style
        ).ask()
        
        if symbol == "Cancel":
            return
        
        # Ask for confirmation
        confirm = questionary.confirm(
            f"Are you sure you want to remove {symbol}?",
            style=custom_style
        ).ask()
        
        if confirm:
            del self.portfolio[symbol]
            self.console.print(f"\n[green]✅ Removed {symbol} from portfolio![/green]")
    
    def show_performance(self):
        """Show portfolio performance analysis."""
        self.console.print(Panel("[bold cyan]📊 Portfolio Performance[/bold cyan]", expand=False))
        
        if not self.portfolio:
            self.console.print("[yellow]Your portfolio is empty![/yellow]")
            return
        
        # Calculate allocation
        total_value = 0
        holdings = []
        
        for symbol, data in self.portfolio.items():
            current_price = self._get_current_price(symbol)
            if current_price:
                value = data['shares'] * current_price
            else:
                value = data['shares'] * data['avg_cost']
            
            total_value += value
            holdings.append({
                'symbol': symbol,
                'value': value,
                'shares': data['shares'],
                'avg_cost': data['avg_cost']
            })
        
        # Allocation table
        self.console.print("\n[bold yellow]📈 Asset Allocation[/bold yellow]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan")
        table.add_column("Value", justify="right")
        table.add_column("Allocation", justify="right")
        table.add_column("Chart", justify="left")
        
        for h in sorted(holdings, key=lambda x: x['value'], reverse=True):
            allocation = (h['value'] / total_value * 100) if total_value > 0 else 0
            bar_length = int(allocation / 5)  # Scale to max 20 chars
            bar = "█" * bar_length
            
            table.add_row(
                h['symbol'],
                f"${h['value']:,.2f}",
                f"{allocation:.1f}%",
                f"[cyan]{bar}[/cyan]"
            )
        
        self.console.print(table)
        
        # Diversification analysis
        self.console.print("\n[bold yellow]🎯 Diversification Analysis[/bold yellow]")
        
        num_positions = len(self.portfolio)
        max_allocation = max([(h['value'] / total_value * 100) for h in holdings]) if holdings else 0
        
        if num_positions < 5:
            diversity_rating = "⚠️ Low"
            advice = "Consider adding more positions for better diversification."
        elif max_allocation > 30:
            diversity_rating = "⚠️ Moderate"
            advice = "Your largest position is over 30%. Consider rebalancing."
        else:
            diversity_rating = "✅ Good"
            advice = "Your portfolio appears well-diversified!"
        
        self.console.print(f"   Diversification: {diversity_rating}")
        self.console.print(f"   Positions: {num_positions}")
        self.console.print(f"   Largest Position: {max_allocation:.1f}%")
        self.console.print(f"\n   💡 {advice}")
    
    def save_portfolio(self):
        """Save portfolio to file."""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
            self.console.print(f"\n[green]✅ Portfolio saved to {self.portfolio_file}[/green]")
        except Exception as e:
            self.console.print(f"[bold red]Error saving portfolio: {e}[/bold red]")
    
    def load_portfolio(self, silent=False):
        """Load portfolio from file."""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    self.portfolio = json.load(f)
                if not silent:
                    self.console.print(f"\n[green]✅ Portfolio loaded from {self.portfolio_file}[/green]")
                    self.console.print(f"   {len(self.portfolio)} positions loaded.")
            else:
                if not silent:
                    self.console.print("[yellow]No saved portfolio found. Starting fresh![/yellow]")
        except Exception as e:
            if not silent:
                self.console.print(f"[bold red]Error loading portfolio: {e}[/bold red]")


# For testing
if __name__ == "__main__":
    tracker = PortfolioTracker()
    tracker.view_portfolio()
