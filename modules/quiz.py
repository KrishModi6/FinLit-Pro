"""
🎯 Finance Quiz Module
======================
Test your financial literacy knowledge.
"""

import random
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
    ('pointer', 'fg:yellow bold'),
    ('highlighted', 'fg:yellow bold'),
])

class FinanceQuiz:
    """Financial literacy quiz system."""
    
    def __init__(self):
        self.console = Console()
        self.scores = []
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.scores_file = os.path.join(self.data_dir, 'quiz_scores.json')
        
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_scores()
        
        # Question banks by category
        self.questions = {
            'basics': [
                {
                    'question': 'What does a stock represent?',
                    'options': [
                        'A loan to a company',
                        'Ownership in a company',
                        'A government bond',
                        'A savings account'
                    ],
                    'correct': 1,
                    'explanation': 'A stock represents partial ownership (equity) in a company.'
                },
                {
                    'question': 'What is a "bull market"?',
                    'options': [
                        'A market where prices are falling',
                        'A market where prices are rising',
                        'A market with high volatility',
                        'A market with low trading volume'
                    ],
                    'correct': 1,
                    'explanation': 'A bull market is characterized by rising prices and optimism, named after how a bull attacks (thrusting upward).'
                },
                {
                    'question': 'What is a stock ticker symbol?',
                    'options': [
                        'The price of a stock',
                        'A unique abbreviation that identifies a stock',
                        'The number of shares outstanding',
                        'The company\'s market cap'
                    ],
                    'correct': 1,
                    'explanation': 'A ticker symbol is a unique series of letters representing a publicly traded company (e.g., AAPL for Apple).'
                },
                {
                    'question': 'What is a dividend?',
                    'options': [
                        'A fee charged by brokers',
                        'A portion of company profits paid to shareholders',
                        'The price difference between buy and sell orders',
                        'A type of stock split'
                    ],
                    'correct': 1,
                    'explanation': 'A dividend is a payment made by companies to shareholders, typically from profits.'
                },
                {
                    'question': 'What is an IPO?',
                    'options': [
                        'Initial Price Offering',
                        'Internal Profit Organization',
                        'Initial Public Offering',
                        'Investment Portfolio Option'
                    ],
                    'correct': 2,
                    'explanation': 'IPO (Initial Public Offering) is when a private company first sells shares to the public.'
                },
                {
                    'question': 'What is market capitalization?',
                    'options': [
                        'Total trading volume',
                        'Share price times number of outstanding shares',
                        'Company\'s total revenue',
                        'Company\'s profit margin'
                    ],
                    'correct': 1,
                    'explanation': 'Market cap = Share Price × Total Shares Outstanding. It represents the total market value of a company.'
                },
                {
                    'question': 'What does NYSE stand for?',
                    'options': [
                        'New York Stock Exchange',
                        'National Yield Securities Exchange',
                        'North York Securities Exchange',
                        'New Yield Stock Exchange'
                    ],
                    'correct': 0,
                    'explanation': 'NYSE is the New York Stock Exchange, the largest stock exchange in the world by market cap.'
                },
                {
                    'question': 'What is the "bid" price?',
                    'options': [
                        'The highest price a buyer is willing to pay',
                        'The lowest price a seller is willing to accept',
                        'The average trading price',
                        'The opening price of the day'
                    ],
                    'correct': 0,
                    'explanation': 'The bid price is the highest price a buyer is willing to pay for a security.'
                }
            ],
            'fundamentals': [
                {
                    'question': 'What is compound interest?',
                    'options': [
                        'Interest charged on the principal only',
                        'Interest earned on both principal and accumulated interest',
                        'A fixed rate of return',
                        'Interest paid monthly'
                    ],
                    'correct': 1,
                    'explanation': 'Compound interest is interest on interest - your earnings generate more earnings over time.'
                },
                {
                    'question': 'What is diversification?',
                    'options': [
                        'Investing all money in one stock',
                        'Spreading investments across different assets to reduce risk',
                        'Only investing in bonds',
                        'Timing the market'
                    ],
                    'correct': 1,
                    'explanation': 'Diversification means spreading investments across different assets, sectors, and regions to reduce risk.'
                },
                {
                    'question': 'What is the Rule of 72?',
                    'options': [
                        'Never invest more than 72% of your income',
                        'A formula to estimate how long it takes money to double',
                        'The maximum number of stocks to own',
                        'A tax rule for investments'
                    ],
                    'correct': 1,
                    'explanation': 'Rule of 72: Divide 72 by your annual return rate to estimate years to double your money.'
                },
                {
                    'question': 'What is dollar-cost averaging?',
                    'options': [
                        'Buying only when prices are low',
                        'Investing a fixed amount regularly regardless of price',
                        'Averaging your stock prices',
                        'Selling when prices drop'
                    ],
                    'correct': 1,
                    'explanation': 'Dollar-cost averaging involves investing a fixed amount at regular intervals, regardless of market conditions.'
                },
                {
                    'question': 'Which generally has higher risk AND higher potential returns?',
                    'options': [
                        'Government bonds',
                        'Savings accounts',
                        'Stocks',
                        'Certificates of deposit'
                    ],
                    'correct': 2,
                    'explanation': 'Stocks typically have higher risk but also higher potential returns compared to bonds and savings.'
                },
                {
                    'question': 'What is an expense ratio?',
                    'options': [
                        'The ratio of income to expenses',
                        'The annual fee charged by investment funds',
                        'The company\'s operating costs',
                        'A measure of stock volatility'
                    ],
                    'correct': 1,
                    'explanation': 'Expense ratio is the annual fee that funds charge investors, expressed as a percentage of assets.'
                },
                {
                    'question': 'What is a portfolio?',
                    'options': [
                        'A single stock investment',
                        'A collection of investments held by an individual or institution',
                        'A type of bond',
                        'A trading strategy'
                    ],
                    'correct': 1,
                    'explanation': 'A portfolio is the collection of all your investments including stocks, bonds, and other assets.'
                },
                {
                    'question': 'What does "buy and hold" mean?',
                    'options': [
                        'Buying stocks and selling within a day',
                        'Investing for the long term and ignoring short-term fluctuations',
                        'Only buying during market crashes',
                        'Holding cash instead of investing'
                    ],
                    'correct': 1,
                    'explanation': 'Buy and hold is a long-term investment strategy where investors hold securities regardless of short-term volatility.'
                }
            ],
            'technical': [
                {
                    'question': 'What does RSI measure?',
                    'options': [
                        'Stock revenue',
                        'Momentum and overbought/oversold conditions',
                        'Trading volume',
                        'Dividend yield'
                    ],
                    'correct': 1,
                    'explanation': 'RSI (Relative Strength Index) measures momentum on a 0-100 scale. Above 70 = overbought, below 30 = oversold.'
                },
                {
                    'question': 'What is a "Golden Cross"?',
                    'options': [
                        'When RSI hits 50',
                        'When the 50-day MA crosses above the 200-day MA',
                        'A stock reaching all-time high',
                        'When volume doubles'
                    ],
                    'correct': 1,
                    'explanation': 'A Golden Cross occurs when the 50-day moving average crosses above the 200-day MA - a bullish signal.'
                },
                {
                    'question': 'What do Bollinger Bands measure?',
                    'options': [
                        'Trading volume',
                        'Volatility and potential overbought/oversold conditions',
                        'Dividend payments',
                        'Company earnings'
                    ],
                    'correct': 1,
                    'explanation': 'Bollinger Bands use standard deviation to show volatility. Price near upper band may be overbought; near lower may be oversold.'
                },
                {
                    'question': 'What is a support level?',
                    'options': [
                        'A price level where buying pressure prevents further decline',
                        'A price level where selling pressure prevents further rise',
                        'The highest price ever reached',
                        'The average trading price'
                    ],
                    'correct': 0,
                    'explanation': 'Support is a price level where demand (buying) is strong enough to prevent further price decline.'
                },
                {
                    'question': 'What does MACD stand for?',
                    'options': [
                        'Moving Average Convergence Divergence',
                        'Market Analysis and Change Detection',
                        'Monthly Average Cost Difference',
                        'Maximum Allowable Capital Distribution'
                    ],
                    'correct': 0,
                    'explanation': 'MACD (Moving Average Convergence Divergence) is a trend-following momentum indicator.'
                },
                {
                    'question': 'A candlestick with a long lower wick suggests:',
                    'options': [
                        'Strong selling pressure',
                        'Buyers pushed the price back up from a low',
                        'Low trading volume',
                        'The market is closed'
                    ],
                    'correct': 1,
                    'explanation': 'A long lower wick (shadow) indicates that buyers pushed the price back up after sellers drove it down.'
                },
                {
                    'question': 'What does increasing volume with rising price indicate?',
                    'options': [
                        'Weak trend that may reverse',
                        'Strong bullish trend with conviction',
                        'Market manipulation',
                        'Nothing significant'
                    ],
                    'correct': 1,
                    'explanation': 'Rising prices with increasing volume indicates strong buying conviction - a healthy uptrend.'
                },
                {
                    'question': 'What is a "Death Cross"?',
                    'options': [
                        'When a stock loses all value',
                        'When the 50-day MA crosses below the 200-day MA',
                        'When RSI hits zero',
                        'When trading is halted'
                    ],
                    'correct': 1,
                    'explanation': 'A Death Cross is when the 50-day MA crosses below the 200-day MA - a bearish signal.'
                }
            ]
        }
    
    def _load_scores(self):
        """Load previous quiz scores."""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    self.scores = json.load(f)
        except:
            self.scores = []
    
    def _save_scores(self):
        """Save quiz scores."""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except:
            pass
    
    def run_quiz(self, category: str):
        """Run a quiz for the specified category."""
        self.console.clear()
        
        if category == 'complete':
            # Combine all categories
            all_questions = []
            for cat_questions in self.questions.values():
                all_questions.extend(cat_questions)
            questions = random.sample(all_questions, min(15, len(all_questions)))
            title = "Complete Assessment"
        else:
            questions = random.sample(self.questions.get(category, []), 
                                     min(8, len(self.questions.get(category, []))))
            title = f"{category.title()} Quiz"
        
        self.console.print(Panel(f"[bold cyan]🎯 {title}[/bold cyan]", expand=False))
        self.console.print(f"\n[dim]Answer {len(questions)} questions to test your knowledge![/dim]\n")
        
        score = 0
        total = len(questions)
        
        for i, q in enumerate(questions, 1):
            self.console.print(f"\n[bold yellow]Question {i}/{total}[/bold yellow]")
            self.console.print(f"\n{q['question']}\n")
            
            # Create options with letters
            options = [f"{chr(65+j)}. {opt}" for j, opt in enumerate(q['options'])]
            
            answer = questionary.select(
                "Your answer:",
                choices=options,
                style=custom_style
            ).ask()
            
            if answer is None:
                break
            
            # Extract answer index
            answer_idx = ord(answer[0]) - 65
            
            if answer_idx == q['correct']:
                score += 1
                self.console.print("[bold green]✅ Correct![/bold green]")
            else:
                self.console.print(f"[bold red]❌ Incorrect![/bold red]")
                self.console.print(f"[dim]The correct answer was: {q['options'][q['correct']]}[/dim]")
            
            self.console.print(f"[dim]💡 {q['explanation']}[/dim]")
        
        # Show results
        percentage = (score / total) * 100 if total > 0 else 0
        
        self.console.print("\n" + "=" * 50)
        self.console.print(Panel(f"[bold cyan]📊 Quiz Results[/bold cyan]", expand=False))
        
        if percentage >= 80:
            grade = "[bold green]A - Excellent![/bold green] 🌟"
        elif percentage >= 60:
            grade = "[bold yellow]B - Good![/bold yellow] 👍"
        elif percentage >= 40:
            grade = "[bold orange]C - Keep Learning![/bold orange] 📚"
        else:
            grade = "[bold red]D - Review the material![/bold red] 📖"
        
        self.console.print(f"\n   Score: {score}/{total} ({percentage:.0f}%)")
        self.console.print(f"   Grade: {grade}")
        
        # Save score
        self.scores.append({
            'category': category,
            'score': score,
            'total': total,
            'percentage': percentage,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        self._save_scores()
        
        # Feedback
        if percentage < 60:
            self.console.print("\n[dim]💡 Tip: Review the educational modules to improve your score![/dim]")
    
    def view_scores(self):
        """View historical quiz scores."""
        self.console.print(Panel("[bold cyan]📊 Quiz Score History[/bold cyan]", expand=False))
        
        if not self.scores:
            self.console.print("\n[yellow]No quiz scores yet! Take a quiz to get started.[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date", style="cyan")
        table.add_column("Category", style="white")
        table.add_column("Score", justify="right")
        table.add_column("Percentage", justify="right")
        table.add_column("Grade", justify="center")
        
        for s in self.scores[-10:]:  # Show last 10
            pct = s['percentage']
            if pct >= 80:
                grade = "[green]A[/green]"
            elif pct >= 60:
                grade = "[yellow]B[/yellow]"
            elif pct >= 40:
                grade = "[orange]C[/orange]"
            else:
                grade = "[red]D[/red]"
            
            table.add_row(
                s['date'],
                s['category'].title(),
                f"{s['score']}/{s['total']}",
                f"{pct:.0f}%",
                grade
            )
        
        self.console.print(table)
        
        # Statistics
        if len(self.scores) > 1:
            avg_score = sum(s['percentage'] for s in self.scores) / len(self.scores)
            best_score = max(s['percentage'] for s in self.scores)
            
            self.console.print("\n[bold yellow]📈 Statistics[/bold yellow]")
            self.console.print(f"   Total Quizzes: {len(self.scores)}")
            self.console.print(f"   Average Score: {avg_score:.1f}%")
            self.console.print(f"   Best Score: {best_score:.0f}%")


# For testing
if __name__ == "__main__":
    quiz = FinanceQuiz()
    quiz.run_quiz("basics")
