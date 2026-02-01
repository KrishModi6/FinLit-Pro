"""
📈 Stock Analysis Module
========================
Real market data analysis using OpenBB.
"""

import warnings
warnings.filterwarnings('ignore')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

console = Console()

class StockAnalyzer:
    """Stock analysis using OpenBB."""
    
    def __init__(self):
        self.console = Console()
        self.obb = None
        self._initialize_openbb()
    
    def _initialize_openbb(self):
        """Initialize OpenBB connection."""
        try:
            from openbb import obb
            self.obb = obb
        except ImportError:
            self.console.print("[bold red]OpenBB not installed![/bold red]")
            self.console.print("[dim]Run: pip install openbb[/dim]")
    
    def _fetch_stock_data(self, symbol: str, days: int = 365):
        """Fetch historical stock data."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                progress.add_task(f"Fetching data for {symbol}...", total=None)
                
                data = self.obb.equity.price.historical(
                    symbol=symbol,
                    provider="yfinance",
                    start_date=(datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                ).to_df()
                
                return data
        except Exception as e:
            self.console.print(f"[bold red]Error fetching data: {e}[/bold red]")
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators."""
        # Moving Averages
        df['SMA_20'] = df['close'].rolling(20).mean()
        df['SMA_50'] = df['close'].rolling(50).mean()
        df['SMA_200'] = df['close'].rolling(200).mean()
        
        # Bollinger Bands
        df['BB_middle'] = df['close'].rolling(20).mean()
        df['BB_std'] = df['close'].rolling(20).std()
        df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
        df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # ATR
        df['TR'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift()),
                abs(df['low'] - df['close'].shift())
            )
        )
        df['ATR'] = df['TR'].rolling(14).mean()
        
        # Returns
        df['daily_return'] = df['close'].pct_change()
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        
        return df
    
    def analyze_stock(self, symbol: str):
        """Comprehensive stock analysis."""
        self.console.clear()
        self.console.print(Panel(f"[bold cyan]📈 Analyzing {symbol}[/bold cyan]", expand=False))
        
        if not self.obb:
            self.console.print("[bold red]OpenBB not available. Please install it first.[/bold red]")
            return
        
        # Fetch data
        df = self._fetch_stock_data(symbol)
        if df is None or df.empty:
            self.console.print(f"[bold red]Could not fetch data for {symbol}[/bold red]")
            return
        
        # Calculate indicators
        df = self._calculate_indicators(df)
        
        # Current price info
        current_price = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        # Price summary
        self.console.print("\n[bold yellow]📊 Price Summary[/bold yellow]")
        
        price_table = Table(show_header=True, header_style="bold magenta")
        price_table.add_column("Metric", style="cyan")
        price_table.add_column("Value", justify="right")
        
        price_table.add_row("Current Price", f"${current_price:,.2f}")
        color = "green" if change >= 0 else "red"
        price_table.add_row("Daily Change", f"[{color}]{'+' if change >= 0 else ''}{change:.2f} ({change_pct:+.2f}%)[/{color}]")
        price_table.add_row("52-Week High", f"${df['high'].max():,.2f}")
        price_table.add_row("52-Week Low", f"${df['low'].min():,.2f}")
        price_table.add_row("Average Volume", f"{df['volume'].mean():,.0f}")
        
        self.console.print(price_table)
        
        # Moving Averages
        self.console.print("\n[bold yellow]📈 Moving Averages[/bold yellow]")
        
        ma_table = Table(show_header=True, header_style="bold magenta")
        ma_table.add_column("Period", style="cyan")
        ma_table.add_column("Value", justify="right")
        ma_table.add_column("Signal", justify="center")
        
        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        sma_200 = df['SMA_200'].iloc[-1]
        
        ma_table.add_row("SMA 20", f"${sma_20:,.2f}", "🟢 Bullish" if current_price > sma_20 else "🔴 Bearish")
        ma_table.add_row("SMA 50", f"${sma_50:,.2f}", "🟢 Bullish" if current_price > sma_50 else "🔴 Bearish")
        if not np.isnan(sma_200):
            ma_table.add_row("SMA 200", f"${sma_200:,.2f}", "🟢 Bullish" if current_price > sma_200 else "🔴 Bearish")
        
        self.console.print(ma_table)
        
        # Technical Indicators
        self.console.print("\n[bold yellow]🔧 Technical Indicators[/bold yellow]")
        
        tech_table = Table(show_header=True, header_style="bold magenta")
        tech_table.add_column("Indicator", style="cyan")
        tech_table.add_column("Value", justify="right")
        tech_table.add_column("Interpretation", justify="center")
        
        rsi = df['RSI'].iloc[-1]
        if rsi > 70:
            rsi_signal = "🔴 Overbought"
        elif rsi < 30:
            rsi_signal = "🟢 Oversold"
        else:
            rsi_signal = "⚪ Neutral"
        
        macd = df['MACD'].iloc[-1]
        macd_signal_val = df['MACD_signal'].iloc[-1]
        macd_interpretation = "🟢 Bullish" if macd > macd_signal_val else "🔴 Bearish"
        
        tech_table.add_row("RSI (14)", f"{rsi:.2f}", rsi_signal)
        tech_table.add_row("MACD", f"{macd:.4f}", macd_interpretation)
        tech_table.add_row("MACD Signal", f"{macd_signal_val:.4f}", "")
        tech_table.add_row("ATR (14)", f"${df['ATR'].iloc[-1]:.2f}", "Volatility measure")
        
        # Bollinger Bands position
        bb_upper = df['BB_upper'].iloc[-1]
        bb_lower = df['BB_lower'].iloc[-1]
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) * 100
        
        if bb_position > 80:
            bb_signal = "🔴 Near upper band"
        elif bb_position < 20:
            bb_signal = "🟢 Near lower band"
        else:
            bb_signal = "⚪ Middle range"
        
        tech_table.add_row("BB Position", f"{bb_position:.1f}%", bb_signal)
        
        self.console.print(tech_table)
        
        # Performance metrics
        self.console.print("\n[bold yellow]📊 Performance[/bold yellow]")
        
        perf_table = Table(show_header=True, header_style="bold magenta")
        perf_table.add_column("Period", style="cyan")
        perf_table.add_column("Return", justify="right")
        
        returns = {
            "1 Week": df['close'].iloc[-1] / df['close'].iloc[-5] - 1 if len(df) >= 5 else None,
            "1 Month": df['close'].iloc[-1] / df['close'].iloc[-21] - 1 if len(df) >= 21 else None,
            "3 Months": df['close'].iloc[-1] / df['close'].iloc[-63] - 1 if len(df) >= 63 else None,
            "6 Months": df['close'].iloc[-1] / df['close'].iloc[-126] - 1 if len(df) >= 126 else None,
            "1 Year": df['close'].iloc[-1] / df['close'].iloc[0] - 1 if len(df) >= 252 else None,
        }
        
        for period, ret in returns.items():
            if ret is not None:
                color = "green" if ret >= 0 else "red"
                perf_table.add_row(period, f"[{color}]{ret*100:+.2f}%[/{color}]")
        
        self.console.print(perf_table)
        
        # Overall signal
        self.console.print("\n[bold yellow]🎯 Overall Analysis[/bold yellow]")
        
        bullish_signals = 0
        total_signals = 0
        
        # Count signals
        if current_price > sma_20: bullish_signals += 1
        total_signals += 1
        
        if current_price > sma_50: bullish_signals += 1
        total_signals += 1
        
        if not np.isnan(sma_200):
            if current_price > sma_200: bullish_signals += 1
            total_signals += 1
        
        if macd > macd_signal_val: bullish_signals += 1
        total_signals += 1
        
        if rsi < 70 and rsi > 30: bullish_signals += 0.5
        elif rsi < 30: bullish_signals += 1
        total_signals += 1
        
        score = bullish_signals / total_signals * 100
        
        if score >= 70:
            overall = "[bold green]🟢 BULLISH[/bold green]"
        elif score >= 40:
            overall = "[bold yellow]⚪ NEUTRAL[/bold yellow]"
        else:
            overall = "[bold red]🔴 BEARISH[/bold red]"
        
        self.console.print(f"Signal Score: {score:.0f}% - {overall}")
        
        # Ask to show chart
        show_chart = input("\n\nWould you like to see the interactive chart? (y/n): ")
        if show_chart.lower() == 'y':
            self._create_chart(df, symbol)
    
    def _create_chart(self, df: pd.DataFrame, symbol: str):
        """Create interactive plotly chart."""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.15, 0.15, 0.2],
                subplot_titles=(f'{symbol} Price Action', 'Volume', 'RSI', 'MACD')
            )
            
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=symbol,
                increasing_line_color='#00ff41',
                decreasing_line_color='#ff4444'
            ), row=1, col=1)
            
            # Moving averages
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', 
                                    line=dict(color='cyan', width=1)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', 
                                    line=dict(color='yellow', width=1)), row=1, col=1)
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], name='BB Upper', 
                                    line=dict(color='gray', dash='dash', width=1)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], name='BB Lower', 
                                    line=dict(color='gray', dash='dash', width=1), 
                                    fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
            
            # Volume
            fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume', 
                                marker_color='rgba(255,165,0,0.5)'), row=2, col=1)
            
            # RSI
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', 
                                    line=dict(color='orange', width=2)), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
            
            # MACD
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', 
                                    line=dict(color='blue', width=1.5)), row=4, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], name='Signal', 
                                    line=dict(color='red', width=1.5)), row=4, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['MACD_hist'], name='Histogram', 
                                marker_color='gray'), row=4, col=1)
            
            fig.update_layout(
                title=f'{symbol} Technical Analysis Dashboard',
                template='plotly_dark',
                height=1000,
                showlegend=True,
                xaxis_rangeslider_visible=False
            )
            
            fig.show()
            
        except ImportError:
            self.console.print("[yellow]Install plotly for charts: pip install plotly[/yellow]")
    
    def compare_stocks(self, symbols: list):
        """Compare multiple stocks."""
        self.console.clear()
        self.console.print(Panel(f"[bold cyan]📊 Comparing: {', '.join(symbols)}[/bold cyan]", expand=False))
        
        if not self.obb:
            self.console.print("[bold red]OpenBB not available.[/bold red]")
            return
        
        comparison_data = []
        
        for symbol in symbols:
            df = self._fetch_stock_data(symbol, days=365)
            if df is not None and not df.empty:
                df = self._calculate_indicators(df)
                
                current_price = df['close'].iloc[-1]
                year_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
                volatility = df['daily_return'].std() * np.sqrt(252) * 100
                rsi = df['RSI'].iloc[-1]
                
                comparison_data.append({
                    'Symbol': symbol,
                    'Price': current_price,
                    'YTD Return': year_return,
                    'Volatility': volatility,
                    'RSI': rsi
                })
        
        if comparison_data:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Symbol", style="cyan")
            table.add_column("Price", justify="right")
            table.add_column("1Y Return", justify="right")
            table.add_column("Volatility", justify="right")
            table.add_column("RSI", justify="right")
            
            for data in comparison_data:
                ret_color = "green" if data['YTD Return'] >= 0 else "red"
                table.add_row(
                    data['Symbol'],
                    f"${data['Price']:,.2f}",
                    f"[{ret_color}]{data['YTD Return']:+.2f}%[/{ret_color}]",
                    f"{data['Volatility']:.2f}%",
                    f"{data['RSI']:.1f}"
                )
            
            self.console.print(table)
    
    def technical_dashboard(self, symbol: str):
        """Full technical analysis dashboard."""
        self.console.clear()
        self.console.print(Panel(f"[bold cyan]📊 Technical Dashboard: {symbol}[/bold cyan]", expand=False))
        
        if not self.obb:
            return
        
        df = self._fetch_stock_data(symbol)
        if df is None:
            return
        
        df = self._calculate_indicators(df)
        self._create_chart(df, symbol)
    
    def analyze_crypto(self, symbol: str):
        """Analyze cryptocurrency."""
        self.console.clear()
        self.console.print(Panel(f"[bold cyan]₿ Analyzing {symbol}[/bold cyan]", expand=False))
        
        if not self.obb:
            self.console.print("[bold red]OpenBB not available.[/bold red]")
            return
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                progress.add_task(f"Fetching data for {symbol}...", total=None)
                
                data = self.obb.crypto.price.historical(
                    symbol=f"{symbol}USD",
                    provider="yfinance",
                    start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                ).to_df()
            
            if data is None or data.empty:
                self.console.print(f"[bold red]Could not fetch data for {symbol}[/bold red]")
                return
            
            # Calculate indicators
            data = self._calculate_indicators(data)
            
            current_price = data['close'].iloc[-1]
            prev_close = data['close'].iloc[-2]
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            # Display summary
            self.console.print("\n[bold yellow]📊 Crypto Summary[/bold yellow]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right")
            
            table.add_row("Current Price", f"${current_price:,.2f}")
            color = "green" if change >= 0 else "red"
            table.add_row("24h Change", f"[{color}]{'+' if change >= 0 else ''}{change:.2f} ({change_pct:+.2f}%)[/{color}]")
            table.add_row("52-Week High", f"${data['high'].max():,.2f}")
            table.add_row("52-Week Low", f"${data['low'].min():,.2f}")
            table.add_row("RSI (14)", f"{data['RSI'].iloc[-1]:.2f}")
            
            macd = data['MACD'].iloc[-1]
            signal = data['MACD_signal'].iloc[-1]
            table.add_row("MACD Signal", "🟢 Bullish" if macd > signal else "🔴 Bearish")
            
            self.console.print(table)
            
            # Show chart
            show_chart = input("\n\nWould you like to see the chart? (y/n): ")
            if show_chart.lower() == 'y':
                self._create_chart(data, f"{symbol}/USD")
                
        except Exception as e:
            self.console.print(f"[bold red]Error: {e}[/bold red]")
    
    def crypto_comparison(self):
        """Compare top cryptocurrencies."""
        cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA']
        self.console.print(Panel("[bold cyan]₿ Comparing Top Cryptocurrencies[/bold cyan]", expand=False))
        
        comparison_data = []
        
        for symbol in cryptos:
            try:
                data = self.obb.crypto.price.historical(
                    symbol=f"{symbol}USD",
                    provider="yfinance",
                    start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                ).to_df()
                
                if data is not None and not data.empty:
                    data = self._calculate_indicators(data)
                    current_price = data['close'].iloc[-1]
                    year_return = (data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100
                    volatility = data['daily_return'].std() * np.sqrt(365) * 100
                    
                    comparison_data.append({
                        'Symbol': symbol,
                        'Price': current_price,
                        'YTD Return': year_return,
                        'Volatility': volatility,
                        'RSI': data['RSI'].iloc[-1]
                    })
            except:
                continue
        
        if comparison_data:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Crypto", style="cyan")
            table.add_column("Price", justify="right")
            table.add_column("1Y Return", justify="right")
            table.add_column("Volatility", justify="right")
            table.add_column("RSI", justify="right")
            
            for data in comparison_data:
                ret_color = "green" if data['YTD Return'] >= 0 else "red"
                table.add_row(
                    data['Symbol'],
                    f"${data['Price']:,.2f}",
                    f"[{ret_color}]{data['YTD Return']:+.2f}%[/{ret_color}]",
                    f"{data['Volatility']:.1f}%",
                    f"{data['RSI']:.1f}"
                )
            
            self.console.print(table)
    
    def screen_stocks(self, screen_type: str):
        """Screen stocks based on criteria."""
        self.console.print(Panel(f"[bold cyan]🔍 Stock Screener: {screen_type.title()}[/bold cyan]", expand=False))
        
        # Sample stocks to screen (in production, this would query a larger universe)
        popular_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT']
        
        results = []
        
        self.console.print("[dim]Screening stocks... This may take a moment.[/dim]\n")
        
        for symbol in popular_stocks:
            try:
                df = self._fetch_stock_data(symbol, days=30)
                if df is not None and not df.empty:
                    df = self._calculate_indicators(df)
                    
                    current_price = df['close'].iloc[-1]
                    prev_close = df['close'].iloc[-2]
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    volume = df['volume'].iloc[-1]
                    avg_volume = df['volume'].mean()
                    
                    results.append({
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': change_pct,
                        'volume': volume,
                        'avg_volume': avg_volume,
                        'rsi': df['RSI'].iloc[-1] if 'RSI' in df.columns else 50
                    })
            except:
                continue
        
        if not results:
            self.console.print("[yellow]Could not fetch stock data.[/yellow]")
            return
        
        # Sort based on screen type
        if screen_type == 'gainers':
            results = sorted(results, key=lambda x: x['change_pct'], reverse=True)[:5]
            title = "Top Gainers"
        elif screen_type == 'losers':
            results = sorted(results, key=lambda x: x['change_pct'])[:5]
            title = "Top Losers"
        elif screen_type == 'active':
            results = sorted(results, key=lambda x: x['volume'], reverse=True)[:5]
            title = "Most Active"
        elif screen_type == 'dividend':
            # Filter for typically dividend-paying stocks
            results = [r for r in results if r['symbol'] in ['WMT', 'JPM', 'V']]
            title = "Dividend Stocks"
        else:  # growth
            results = sorted(results, key=lambda x: x['change_pct'], reverse=True)[:5]
            title = "Growth Stocks"
        
        table = Table(show_header=True, header_style="bold magenta", title=title)
        table.add_column("Symbol", style="cyan")
        table.add_column("Price", justify="right")
        table.add_column("Change %", justify="right")
        table.add_column("Volume", justify="right")
        table.add_column("RSI", justify="right")
        
        for r in results:
            color = "green" if r['change_pct'] >= 0 else "red"
            table.add_row(
                r['symbol'],
                f"${r['price']:,.2f}",
                f"[{color}]{r['change_pct']:+.2f}%[/{color}]",
                f"{r['volume']:,.0f}",
                f"{r['rsi']:.1f}"
            )
        
        self.console.print(table)
    
    def get_market_news(self):
        """Get market news."""
        self.console.print(Panel("[bold cyan]📰 Market News[/bold cyan]", expand=False))
        self.console.print("\n[dim]Note: For real-time news, visit financial news websites or")
        self.console.print("set up API keys for news providers in OpenBB.[/dim]\n")
        
        # Educational content about where to find news
        sources = """
## Recommended Financial News Sources

| Source | URL | Focus |
|--------|-----|-------|
| **Bloomberg** | bloomberg.com | Global markets |
| **CNBC** | cnbc.com | US markets |
| **Reuters** | reuters.com | World news |
| **Yahoo Finance** | finance.yahoo.com | General investing |
| **Seeking Alpha** | seekingalpha.com | Stock analysis |
| **MarketWatch** | marketwatch.com | Market data |

## For Real-Time Data
Set up API keys in OpenBB for providers like:
- Alpha Vantage (free tier available)
- FMP (Financial Modeling Prep)
- Polygon.io
        """
        self.console.print(Markdown(sources))


# For testing
if __name__ == "__main__":
    analyzer = StockAnalyzer()
    analyzer.analyze_stock("AAPL")
