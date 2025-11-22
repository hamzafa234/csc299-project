import json
import os
import sys
import yfinance as yf
from datetime import datetime
import pandas as pd
import requests
from openai import OpenAI
import typer 
from typing import Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

app = typer.Typer()

client = OpenAI(
  api_key="xxxxxxxx"
)

class FinancialDataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        
    def convert_dataframe_to_dict(self, df):
        """Convert pandas DataFrame to dictionary with proper formatting"""
        if df is None or df.empty:
            return []
        
        # Convert to dictionary with dates as strings
        result = []
        for col in df.columns:
            period_data = {'date': str(col.date())}
            for idx in df.index:
                value = df.loc[idx, col]
                # Convert numpy/pandas types to Python native types
                if pd.isna(value):
                    period_data[idx] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    period_data[idx] = str(value)
                else:
                    try:
                        period_data[idx] = float(value)
                    except (ValueError, TypeError):
                        period_data[idx] = str(value)
            result.append(period_data)
        
        return result
    
    def get_balance_sheet(self):
        """Fetch most recent quarterly balance sheet data"""
        quarterly_bs = self.stock.quarterly_balance_sheet
        
        if quarterly_bs is None or quarterly_bs.empty:
            return []
        
        # Get only the most recent quarter (first column)
        most_recent = quarterly_bs.iloc[:, [0]]
        return self.convert_dataframe_to_dict(most_recent)
    
    def get_income_statement(self):
        """Fetch income statement data"""
        return self.convert_dataframe_to_dict(self.stock.financials)
    
    def get_cash_flow(self):
        """Fetch cash flow statement data"""
        return self.convert_dataframe_to_dict(self.stock.cashflow)
    
    def get_all_financials(self):
        """Fetch all financial statements and return as dictionary"""
        print(f"\nFetching financial data for {self.ticker}...")
        
        try:
            # Get basic info to verify ticker exists
            info = self.stock.info
            company_name = info.get('longName', self.ticker)
            
            financials = {
                'ticker': self.ticker,
                'companyName': company_name,
                'currency': info.get('currency', 'USD'),
                'fetchDate': datetime.now().isoformat(),
                'balanceSheet': self.get_balance_sheet(),
                'incomeStatement': self.get_income_statement(),
                'cashFlowStatement': self.get_cash_flow()
            }
            
            return financials
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def save_to_json(self, filename=None):
        """Fetch financial data and save to JSON file"""
        financials = self.get_all_financials()
        
        if not financials:
            print("Failed to fetch financial data")
            return False
        
        if filename is None:
            filename = f"{self.ticker}_financials.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(financials, f, indent=2)
            
            # Print summary of data retrieved
            bs_periods = len(financials['balanceSheet'])
            is_periods = len(financials['incomeStatement'])
            cf_periods = len(financials['cashFlowStatement'])
            
            print(f"\nData Retrieved:")
            print(f"  Balance Sheet: {bs_periods} quarterly period (most recent)")
            print(f"  Income Statement: {is_periods} annual periods")
            print(f"  Cash Flow: {cf_periods} annual periods")
            
            return True
            
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

def get_10y_treasury_yield():
    """
    Fetches the latest 10-Year US Treasury yield (^TNX) from Yahoo Finance.
    Returns the yield as a float (in percent).
    """
    ticker = yf.Ticker("^TNX")
    data = ticker.history(period="1d")
    
    if data.empty:
        raise ValueError("No data returned for ^TNX.")
    
    latest_yield = data["Close"].iloc[-1]
    return latest_yield

def get_20y_treasury_yield():
    """
    Fetches the latest 20-Year US Treasury yield (^TYX) from Yahoo Finance.
    Returns the yield as a float (in percent).
    """
    ticker = yf.Ticker("^TYX")  # 20-Year Treasury Index
    data = ticker.history(period="1d")
    
    if data.empty:
        raise ValueError("No data returned for ^TYX.")
    
    latest_yield = data["Close"].iloc[-1]
    return latest_yield

def get_30y_treasury_yield():
    """
    Fetches the latest 30-Year US Treasury yield (^TYX) from Yahoo Finance.
    Returns the yield as a float (in percent).
    """
    ticker = yf.Ticker("^TYX")  # 30-Year Treasury Index
    data = ticker.history(period="1d")
    
    if data.empty:
        raise ValueError("No data returned for ^TYX.")
    
    latest_yield = data["Close"].iloc[-1]
    return latest_yield

def credit_spread_analysis(ticker):
    response = client.responses.create(
        model="gpt-5-nano",
        tools=[{"type": "web_search"}],
        input="get me the yield to maturity for" + ticker + "that is due in more than 5 years. Chose the bond that was traded the most recently. Do not ask any follow up questions. Return a list that has two floats. Do not return any text other than the list. If the yeild is 5.49 percent and has a maturity date of 2065 you will return [0.0549, 2065.0]. Do not return a link ever if the company has no bonds return [0.0, 0.0]",
        store=True,
    )

    bond_data = eval(response.output_text)
    yeild = bond_data[0]
    bond_maturity = bond_data[1]
    yeild = yeild * 100

    delta = bond_maturity - datetime.now().year
    if delta > 25:
        treasury_yield = get_30y_treasury_yield()
        tbill = 30
    elif delta > 15:
        treasury_yield = get_20y_treasury_yield()
        tbill = 20
    else:
        treasury_yield = get_10y_treasury_yield()
        tbill = 10

    spread = yeild - treasury_yield
    
    filename = f"{ticker}_summary.md"
    
    # Check if file exists and read existing content
    existing_content = ""
    try:
        with open(filename, 'r') as f:
            existing_content = f.read()
    except FileNotFoundError:
        pass
    
    # Build the credit spread content
    credit_content = "# Credit Spread Analysis\n\n"
    credit_content += f"**Bond Maturity Year:** {bond_maturity:.0f}\n\n"
    credit_content += f"**Market Yield of Debt:** {yeild:.2f}%\n\n"
    credit_content += f"**{tbill}y Treasury Yield:** {treasury_yield:.2f}%\n\n"
    credit_content += "---\n\n"
    credit_content += f"## **Spread to {tbill}y Treasury: {spread:.2f}%**\n\n"
    
    if spread < 0:
        credit_content += "> **Note:** Negative spread indicates debt market has low liquidity for this company's bonds.\n"
    
    # Write to file
    with open(filename, 'w') as f:
        if existing_content:
            f.write(existing_content)
            f.write("\n\n---\n\n")
            f.write(credit_content)
        else:
            f.write(credit_content)
    
    print("=" * 60)
    print(" ")
    print(f"Credit Spread Analysis saved to {filename}")
    print(" ")
    print("=" * 60)

def compare(ticker):
    response = client.responses.create(
        model="gpt-5-nano",
        tools=[{"type": "web_search"}],
        input="get me the main competitors for " + ticker + " Do not ask any follow up questions. Return a list of ticker symbols only. Do not return any text other than the list. only return up to 5 competitors. for example if the main competeitors are apple, microsoft, and google, you will return ['AAPL', 'MSFT', 'GOOGL']. If there are no competitors return an empty list [] do not return a link ever",
        store=True,
    )
    comp_data = eval(response.output_text)
    comp_data.append(ticker)
    
    filename = f"{ticker}_summary.md"
    
    # Check if file exists and read existing content
    existing_content = ""
    try:
        with open(filename, 'r') as f:
            existing_content = f.read()
    except FileNotFoundError:
        pass
    
    # Build the table content
    table_content = "# Competitor Analysis\n\n"
    table_content += "| Ticker | Market Cap | Enterprise Value | Trailing P/E | Forward P/E | Yield | Price to FCF |\n"
    table_content += "|--------|------------|------------------|--------------|-------------|-------|-------------|\n"
    
    for symbol in comp_data[:6]:
        values = getCompVal(symbol)
        # Format specific columns
        formatted_values = []
        for i, v in enumerate(values):
            if v is None:
                formatted_values.append('N/A')
            elif i in [0, 1]:  # Market Cap, Enterprise Value
                formatted_values.append(format_large_number(v))
            elif i in [2, 3, 5]:  # Trailing P/E, Forward P/E, Price to FCF
                formatted_values.append(f"{v:.3f}")
            else:
                formatted_values.append(str(v))
        
        table_content += f"| {symbol} | {formatted_values[0]} | {formatted_values[1]} | {formatted_values[2]} | {formatted_values[3]} | {formatted_values[4]} | {formatted_values[5]} |\n"
    
    # Write to file
    with open(filename, 'w') as f:
        if existing_content:
            f.write(existing_content)
            f.write("\n\n---\n\n")
            f.write(table_content)
        else:
            f.write(table_content)
    
    print("=" * 60)
    print(" ")
    print(f"Competitor Analysis saved to {filename}")
    print(" ")
    print("=" * 60)

def format_large_number(num):
    """Format large numbers with B (billions), M (millions), or K (thousands)"""
    if num >= 1_000_000_000_000:  # Trillions
        return f"{num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:  # Billions
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:  # Millions
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:  # Thousands
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.2f}"

def getCompVal(ticker):
    stock = yf.Ticker(ticker)
    cap = stock.info.get('marketCap', None)
    pe = stock.info.get('trailingPE', None)
    fpe = stock.info.get('forwardPE', None)
    y = stock.info.get('dividendYield', None)
    ev = stock.info.get('enterpriseValue', None)
    
    # Calculate Price to FCF manually
    price_to_fcf = None
    try:
        # Get free cash flow from cash flow statement
        cash_flow = stock.cashflow
        if not cash_flow.empty and 'Free Cash Flow' in cash_flow.index:
            # Get the most recent free cash flow (first column)
            fcf = cash_flow.loc['Free Cash Flow'].iloc[0]
            
            # If FCF is positive and we have market cap, calculate ratio
            if fcf and fcf > 0 and cap:
                price_to_fcf = cap / fcf
    except Exception as e:
        # If calculation fails, leave as None
        pass

    list = [cap, ev, pe, fpe, y, price_to_fcf]
    return list
    
def capital_structure_summary(ticker):
    with open(f'{ticker}_financials.json', 'r') as file:
            data = json.load(file)

    stock = yf.Ticker(ticker)
    cap = stock.info.get('marketCap', None)

    total_debt = data['balanceSheet'][0]['Total Debt']
    latest_balance_sheet = data['balanceSheet'][0]
    income = data['incomeStatement'][0]

    total_debt_formatted = format_large_number(total_debt)

    # Use .get() method to safely retrieve preferred stock value
    pre = data['balanceSheet'][0].get('Preferred Stock Equity', 0) or 0

    cash = latest_balance_sheet['Cash And Cash Equivalents']
    cash_formatted = format_large_number(cash)
     
    EV = stock.info.get('marketCap', None) + total_debt - latest_balance_sheet['Cash And Cash Equivalents'] + pre

    shares_outstanding = income['Basic Average Shares']
    shares_outstanding_formatted = format_large_number(shares_outstanding)
    
    netdebtpershare = (total_debt - latest_balance_sheet['Cash And Cash Equivalents']) / income['Basic Average Shares']
    
    filename = f"{ticker}_summary.md"
    
    # Check if file exists and read existing content
    existing_content = ""
    try:
        with open(filename, 'r') as f:
            existing_content = f.read()
    except FileNotFoundError:
        pass
    
    # Build the capital structure content
    capital_content = "# Capital Structure Summary\n\n"
    capital_content += f"**Market Capitalization:** {format_large_number(cap)}\n\n"
    
    if pre != 0:
        preferred_formatted = format_large_number(pre)
        capital_content += f"**Preferred Stock Equity:** {preferred_formatted}\n\n"
    
    capital_content += f"**Total Debt:** {total_debt_formatted}\n\n"
    capital_content += f"**Cash And Cash Equivalents:** {cash_formatted}\n\n"
    capital_content += "---\n\n"
    capital_content += f"**Enterprise Value:** {format_large_number(EV)}\n\n"
    capital_content += f"**Shares Outstanding:** {shares_outstanding_formatted}\n\n"
    capital_content += "---\n\n"
    capital_content += f"## **Net Debt per Share: ${netdebtpershare:.2f}**\n"
    
    # Write to file
    with open(filename, 'w') as f:
        if existing_content:
            f.write(existing_content)
            f.write("\n\n---\n\n")
            f.write(capital_content)
        else:
            f.write(capital_content)
    
    print("=" * 60)
    print(" ")
    print(f"Capital Structure Summary saved to {filename}")
    print(" ")
    print("=" * 60)

def wacc_calculation(ticker):
    global yield_10y
    yield_10y = get_10y_treasury_yield()

    stock = yf.Ticker(ticker)
    cap = stock.info.get('marketCap', None)
    beta = stock.info.get("beta")

    ERP = 10 - yield_10y

    with open(f'{ticker}_financials.json', 'r') as file:
            data = json.load(file)

    # Access the first balance sheet entry
    latest_balance_sheet = data['balanceSheet'][0]

    income = data['incomeStatement'][0]

    cash = data['cashFlowStatement'][0]

    # Get Total Debt
    total_debt = latest_balance_sheet['Total Debt']

    tax_rate = income["Tax Rate For Calcs"]

    weight_of_debt = total_debt / (total_debt + cap)
    weight_of_equity = cap / (total_debt + cap)

    weight_of_debt_formatted = f"{weight_of_debt:.4f}"
    weight_of_equity_formatted = f"{weight_of_equity:.4f}"

    if 'Interest Expense' in income:
        interest_expense = income['Interest Expense']
    else:
        interest_expense = cash['Interest Paid Supplemental Data']
    
    if(interest_expense == None):
        cost_of_debt = 0
    else:
        cost_of_debt = abs(interest_expense / total_debt) * 100

    cost_of_equity = yield_10y + beta * ERP
    
    WACC = (weight_of_equity * cost_of_equity) + (weight_of_debt * cost_of_debt * (1 - tax_rate))
    
    filename = f"{ticker}_summary.md"
    
    # Check if file exists and read existing content
    existing_content = ""
    try:
        with open(filename, 'r') as f:
            existing_content = f.read()
    except FileNotFoundError:
        pass
    
    # Build the WACC content
    wacc_content = "# WACC Calculation\n\n"
    wacc_content += f"**10-Year Treasury Yield:** {yield_10y:.2f}%\n\n"
    wacc_content += f"**Market Cap:** ${cap:,.0f}\n\n"
    wacc_content += f"**Beta:** {beta:.2f}\n\n"
    wacc_content += f"**Equity Risk Premium:** {ERP:.2f}%\n\n"
    wacc_content += f"**Total Debt:** ${total_debt:,.0f}\n\n"
    wacc_content += f"**Tax Rate:** {tax_rate:.2%}\n\n"
    wacc_content += "---\n\n"
    wacc_content += f"**Weight of Debt:** {weight_of_debt_formatted}\n\n"
    wacc_content += f"**Weight of Equity:** {weight_of_equity_formatted}\n\n"
    wacc_content += f"**Cost of Equity:** {cost_of_equity:.2f}%\n\n"
    wacc_content += f"**Cost of Debt:** {cost_of_debt:.2f}%\n\n"
    wacc_content += "---\n\n"
    wacc_content += f"## **WACC: {WACC:.2f}%**\n"
    
    # Write to file
    with open(filename, 'w') as f:
        if existing_content:
            f.write(existing_content)
            f.write("\n\n---\n\n")
            f.write(wacc_content)
        else:
            f.write(wacc_content)
    
    print("=" * 60)
    print(" ")
    print(f"WACC Calculation saved to {filename}")
    print(" ")
    print("=" * 60)

def notes(ticker):
    response = client.responses.create(
        model="gpt-5-nano",
        tools=[{"type": "web_search"}],
        input="Give a summary of what" + ticker + "does. Do not ask any follow up questions. Return a concise summary in 225 words or less. Do not return any text other than the summary. do not return a link ever. Make sure to return bullet points",
        store=True,
    )

    filename = f"{ticker}_summary.md"
    
    # Check if file exists and read existing content
    existing_content = ""
    try:
        with open(filename, 'r') as f:
            existing_content = f.read()
    except FileNotFoundError:
        pass  # File doesn't exist yet, which is fine
    
    # Write content to markdown file
    with open(filename, 'w') as f:
        if existing_content:
            # If there's existing content, preserve it and add new summary
            f.write(existing_content)
            f.write("\n\n---\n\n")
            f.write(f"# {ticker} Summary (Updated)\n\n")
            f.write(response.output_text)
        else:
            # If it's a new file, write normally
            f.write(f"# {ticker} Summary\n\n")
            f.write(response.output_text)
    
    print("=" * 60)
    print(" ")
    print(f"Company Summary saved to {filename}")
    print(" ")
    print("=" * 60)

def main(command):
    
    #command = sys.argv[1].lower() 

    global ticker
    ticker = command if command != "" else None

    if not ticker:
        ticker = "AAPL"  # Default to Apple
        print(f"No ticker provided, using default: {ticker}")
    
    fetcher = FinancialDataFetcher(ticker)
    success = fetcher.save_to_json()

    stock = yf.Ticker(ticker)
    global beta 
    global cap 
    global current_price
    info = stock.info
    beta = info.get("beta")
    cap = info.get('marketCap', None)
    global current_price
    current_price = stock.info.get("currentPrice")
    

    if success:
        print("\n✓ Done! Check the generated JSON file for the financial data.")

    else:
        print("\n✗ Failed to fetch and save financial data.")
        print("Please check that the ticker symbol is valid and try again.")

app = typer.Typer()

# Global state file to track current ticker
STATE_FILE = ".current_ticker.json"

@app.command()
def lad(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company")
):
    '''Fetch and save financial data for the given ticker (must be run before other commands)'''
    main(ticker)

@app.command()
def wac (
    ticker: str = typer.Argument(..., help="Ticker symbol of the company")
):
    '''Calculate and display the WACC for the given ticker'''
    wacc_calculation(ticker)

@app.command()
def cs(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company")
):
    '''Display the capital structure summary for the given ticker'''
    capital_structure_summary(ticker)

@app.command()
def csp(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company")
):
    '''See credit spread for the given ticker'''
    credit_spread_analysis(ticker)

@app.command()
def ce(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company")
):
    '''Display competitor analysis for the given ticker'''
    compare(ticker)

def get_current_ticker():
    """Get the currently active ticker"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('ticker')
    return None

def set_current_ticker(ticker):
    """Set the currently active ticker"""
    with open(STATE_FILE, 'w') as f:
        json.dump({'ticker': ticker}, f)

def get_filename(ticker=None):
    """Get the filename for a given ticker or current ticker"""
    if ticker is None:
        ticker = get_current_ticker()
        if ticker is None:
            typer.secho("✗ No active ticker. Run 'bg <ticker>' first.", fg=typer.colors.RED)
            raise typer.Exit(1)
    return f"{ticker}_notes.json"

@app.command()
def bg(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company")
):
    '''Start the process for researching a business given its ticker'''
    
    filename = get_filename(ticker)
    
    # Set this as the current ticker
    set_current_ticker(ticker)
    
    tasks = load_tasks(filename)
    
    # Define initial tasks
    initial_tasks = [
        "Examine default risk",
        "Examine big three financial statements",
        "Read form 10-K and 10-Q filings",
        "Perform ratio analysis",
        "Examine expectations",
        "Examine past guidance vs actual performance",
        "Examine competitors"
    ]
    
    # Add all initial tasks
    for description in initial_tasks:
        task = {
            'id': max([t['id'] for t in tasks], default=0) + 1,
            'description': description,
            'completed': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        tasks.append(task)
    
    save_tasks(tasks, filename)
    typer.secho(f"✓ Created research project for {ticker.upper()} with {len(initial_tasks)} tasks", fg=typer.colors.GREEN)
    typer.secho(f"  File: {filename}", fg=typer.colors.CYAN)

def load_tasks(filename):
    """Load tasks from JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks, filename):
    """Save tasks to JSON file"""
    with open(filename, 'w') as f:
        json.dump(tasks, f, indent=2)

@app.command()
def add(
    description: str = typer.Argument(..., help="Task description"),
    ticker: str = typer.Option(None, "--ticker", "-t", help="Ticker symbol (uses current if not specified)")
):
    """Add a new task"""
    filename = get_filename(ticker)
    tasks = load_tasks(filename)
    
    task = {
        'id': max([t['id'] for t in tasks], default=0) + 1,
        'description': description,
        'completed': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    tasks.append(task)
    save_tasks(tasks, filename)
    typer.secho(f"✓ Task added successfully (ID: {task['id']})", fg=typer.colors.GREEN)

@app.command()
def rm(
    task_id: int = typer.Argument(..., help="ID of task to remove"),
    ticker: str = typer.Option(None, "--ticker", "-t", help="Ticker symbol (uses current if not specified)")
):
    """Remove a task by ID"""
    filename = get_filename(ticker)
    tasks = load_tasks(filename)
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if task:
        tasks.remove(task)
        save_tasks(tasks, filename)
        typer.secho(f"✓ Task {task_id} removed successfully", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Task with ID {task_id} not found", fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command()
def com(
    task_id: int = typer.Argument(..., help="ID of task to mark as completed"),
    ticker: str = typer.Option(None, "--ticker", "-t", help="Ticker symbol (uses current if not specified)")
):
    """Mark a task as completed"""
    filename = get_filename(ticker)
    tasks = load_tasks(filename)
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if task:
        if task['completed']:
            typer.secho(f"Task {task_id} is already completed", fg=typer.colors.YELLOW)
        else:
            task['completed'] = True
            task['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_tasks(tasks, filename)
            typer.secho(f"✓ Task {task_id} marked as completed", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Task with ID {task_id} not found", fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command()
def lis(
    all: bool = typer.Option(False, "--all", "-a", help="Show all tasks including completed"),
    completed_only: bool = typer.Option(False, "--completed", "-c", help="Show only completed tasks"),
    ticker: str = typer.Option(None, "--ticker", "-t", help="Ticker symbol (uses current if not specified)")
):
    """List all tasks"""
    filename = get_filename(ticker)
    tasks = load_tasks(filename)
    
    if not tasks:
        typer.secho("No tasks found", fg=typer.colors.YELLOW)
        return
    
    # Filter tasks based on options
    if completed_only:
        tasks = [t for t in tasks if t['completed']]
        header = "COMPLETED TASKS"
    elif not all:
        tasks = [t for t in tasks if not t['completed']]
        header = "PENDING TASKS"
    else:
        header = "ALL TASKS"
    
    if not tasks:
        typer.secho(f"No tasks to display", fg=typer.colors.YELLOW)
        return
    
    # Show current ticker
    current = get_current_ticker()
    typer.echo("\n" + "="*60)
    typer.secho(f"{header} - {current.upper()}", fg=typer.colors.CYAN, bold=True)
    typer.echo("="*60)
    
    for task in tasks:
        status = "✓" if task['completed'] else "○"
        color = typer.colors.GREEN if task['completed'] else typer.colors.WHITE
        typer.secho(f"{status} ID: {task['id']} | {task['description']}", fg=color)
        typer.echo(f"  Created: {task['created_at']}")
        if task['completed']:
            typer.echo(f"  Completed: {task.get('completed_at', 'N/A')}")
        typer.echo("-"*60)

@app.command()
def ser(
    keyword: str = typer.Argument(..., help="Keyword to search for in task descriptions"),
    ticker: str = typer.Option(None, "--ticker", "-t", help="Ticker symbol (uses current if not specified)")
):
    """Search tasks by keyword"""
    filename = get_filename(ticker)
    tasks = load_tasks(filename)
    
    if not tasks:
        typer.secho("No tasks to search", fg=typer.colors.YELLOW)
        return
    
    matches = [t for t in tasks if keyword.lower() in t['description'].lower()]
    
    if not matches:
        typer.secho(f"No tasks found matching '{keyword}'", fg=typer.colors.YELLOW)
        return
    
    typer.echo("\n" + "="*60)
    typer.secho(f"SEARCH RESULTS FOR: '{keyword}'", fg=typer.colors.CYAN, bold=True)
    typer.echo("="*60)
    
    for task in matches:
        status = "✓" if task['completed'] else "○"
        color = typer.colors.GREEN if task['completed'] else typer.colors.WHITE
        typer.secho(f"{status} ID: {task['id']} | {task['description']}", fg=color)
        typer.echo(f"  Created: {task['created_at']}")
        if task['completed']:
            typer.echo(f"  Completed: {task.get('completed_at', 'N/A')}")
        typer.echo("-"*60)
    
    typer.secho(f"\nFound {len(matches)} task(s)", fg=typer.colors.CYAN)

@app.command()
def cl(
    completed: bool = typer.Option(False, "--completed", "-c", help="Clear only completed tasks"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    ticker: str = typer.Option(None, "--ticker", "-t", help="Ticker symbol (uses current if not specified)")
):
    """Clear all tasks or only completed tasks"""
    filename = get_filename(ticker)
    tasks = load_tasks(filename)
    
    if not tasks:
        typer.secho("No tasks to clear", fg=typer.colors.YELLOW)
        return
    
    if completed:
        tasks_to_clear = [t for t in tasks if t['completed']]
        message = f"clear {len(tasks_to_clear)} completed task(s)"
    else:
        tasks_to_clear = tasks
        message = f"clear ALL {len(tasks)} task(s)"
    
    if not tasks_to_clear:
        typer.secho("No tasks to clear", fg=typer.colors.YELLOW)
        return
    
    if not force:
        confirm = typer.confirm(f"Are you sure you want to {message}?")
        if not confirm:
            typer.secho("Operation cancelled", fg=typer.colors.YELLOW)
            return
    
    if completed:
        remaining_tasks = [t for t in tasks if not t['completed']]
        save_tasks(remaining_tasks, filename)
        typer.secho(f"✓ Cleared {len(tasks_to_clear)} completed task(s)", fg=typer.colors.GREEN)
    else:
        save_tasks([], filename)
        typer.secho("✓ All tasks cleared", fg=typer.colors.GREEN)

@app.command()
def cur():
    """Show the current active ticker"""
    ticker = get_current_ticker()
    if ticker:
        typer.secho(f"Current ticker: {ticker.upper()}", fg=typer.colors.CYAN)
    else:
        typer.secho("No active ticker set. Run 'bg <ticker>' to start.", fg=typer.colors.YELLOW)

@app.command()
def sw(ticker: str = typer.Argument(..., help="Ticker symbol to switch to")):
    """Switch to a different ticker project"""
    filename = get_filename(ticker)
    
    if not os.path.exists(filename):
        typer.secho(f"✗ No project found for {ticker.upper()}. Run 'bg {ticker}' to create it.", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    set_current_ticker(ticker)
    typer.secho(f"✓ Switched to {ticker.upper()}", fg=typer.colors.GREEN)

@app.command()
def sm(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company"),
):
    '''Give a summary of what the company does'''
    notes(ticker)

if __name__ == "__main__":
    app()
