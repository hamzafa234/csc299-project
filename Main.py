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
  api_key="xxxxxxxxx"
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

def get_10y_treasury_yield_90_days_ago():
    """
    Fetches the 10-Year US Treasury yield (^TNX) from 90 days ago.
    Returns the yield as a float (in percent).
    """
    ticker = yf.Ticker("^TNX")
    data = ticker.history(period="6mo")
    
    if data.empty:
        raise ValueError("No data returned for ^TNX.")
    
    if len(data) < 90:
        raise ValueError("Not enough historical data available.")
    
    # Get the yield from approximately 90 trading days ago
    # (90 calendar days ≈ 60-65 trading days)
    yield_90_days_ago = data["Close"].iloc[-65]  # Adjust index as needed
    
    return yield_90_days_ago

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

def Statements(ticker):
        with open(f'{ticker}_financials.json', 'r') as file:
            data = json.load(file)

        income = data['incomeStatement'][0]
        cash = data['cashFlowStatement'][0]
        income2 = data['incomeStatement'][1]
        cash2 = data['cashFlowStatement'][1]
        income3 = data['incomeStatement'][2]
        cash3 = data['cashFlowStatement'][2]
        income4 = data['incomeStatement'][3]
        cash4 = data['cashFlowStatement'][3]

        print("=" * 60)
        print(" ")
        print("Income Statement Summary")
        print(" ")
        print(f"Fiscal Year:         {income['date']:>10} | {income2['date']:>10} | {income3['date']:>10} | {income4['date']:>10}")
        print(" ")
        print("Income Statement as a Percentage of Revenue:")
        print(" ")
        print(f"Total Revenue:       {'100%':>10} | {'100%':>10} | {'100%':>10} | {'100%':>10}")
        print(f"Cost of Revenue:     {income['Cost Of Revenue'] / income['Total Revenue'] * 100:>9.2f}% | {income2['Cost Of Revenue'] / income2['Total Revenue'] * 100:>9.2f}% | {income3['Cost Of Revenue'] / income3['Total Revenue'] * 100:>9.2f}% | {income4['Cost Of Revenue'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Gross Profit:        {income['Gross Profit'] / income['Total Revenue'] * 100:>9.2f}% | {income2['Gross Profit'] / income2['Total Revenue'] * 100:>9.2f}% | {income3['Gross Profit'] / income3['Total Revenue'] * 100:>9.2f}% | {income4['Gross Profit'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Operating Expenses:  {income['Operating Expense'] / income['Total Revenue'] * 100:>9.2f}% | {income2['Operating Expense'] / income2['Total Revenue'] * 100:>9.2f}% | {income3['Operating Expense'] / income3['Total Revenue'] * 100:>9.2f}% | {income4['Operating Expense'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Operating Income:    {income['Operating Income'] / income['Total Revenue'] * 100:>9.2f}% | {income2['Operating Income'] / income2['Total Revenue'] * 100:>9.2f}% | {income3['Operating Income'] / income3['Total Revenue'] * 100:>9.2f}% | {income4['Operating Income'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Tax Expense:         {income['Tax Provision'] / income['Total Revenue'] * 100:>9.2f}% | {income2['Tax Provision'] / income2['Total Revenue'] * 100:>9.2f}% | {income3['Tax Provision'] / income3['Total Revenue'] * 100:>9.2f}% | {income4['Tax Provision'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Net Income:          {income['Net Income'] / income['Total Revenue'] * 100:>9.2f}% | {income2['Net Income'] / income2['Total Revenue'] * 100:>9.2f}% | {income3['Net Income'] / income3['Total Revenue'] * 100:>9.2f}% | {income4['Net Income'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(" ")
        print("YOY changes:")
        print(" ")
        print(f"Revenue Growth:      {(income['Total Revenue'] - income2['Total Revenue']) / income2['Total Revenue'] * 100:>9.2f}% | {(income2['Total Revenue'] - income3['Total Revenue']) / income3['Total Revenue'] * 100:>9.2f}% | {(income3['Total Revenue'] - income4['Total Revenue']) / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Cost of Revenue:     {(income['Cost Of Revenue'] - income2['Cost Of Revenue']) / income2['Cost Of Revenue'] * 100:>9.2f}% | {(income2['Cost Of Revenue'] - income3['Cost Of Revenue']) / income3['Cost Of Revenue'] * 100:>9.2f}% | {(income3['Cost Of Revenue'] - income4['Cost Of Revenue']) / income4['Cost Of Revenue'] * 100:>9.2f}%")
        print(f"Gross Profit:        {(income['Gross Profit'] - income2['Gross Profit']) / income2['Gross Profit'] * 100:>9.2f}% | {(income2['Gross Profit'] - income3['Gross Profit']) / income3['Gross Profit'] * 100:>9.2f}% | {(income3['Gross Profit'] - income4['Gross Profit']) / income4['Gross Profit'] * 100:>9.2f}%")
        print(f"Operating Expense:   {(income['Operating Expense'] - income2['Operating Expense']) / income2['Operating Expense'] * 100:>9.2f}% | {(income2['Operating Expense'] - income3['Operating Expense']) / income3['Operating Expense'] * 100:>9.2f}% | {(income3['Operating Expense'] - income4['Operating Expense']) / income4['Operating Expense'] * 100:>9.2f}%")
        print(f"Operating Income:    {(income['Operating Income'] - income2['Operating Income']) / income2['Operating Income'] * 100:>9.2f}% | {(income2['Operating Income'] - income3['Operating Income']) / income3['Operating Income'] * 100:>9.2f}% | {(income3['Operating Income'] - income4['Operating Income']) / income4['Operating Income'] * 100:>9.2f}%")
        print(f"Tax Expense:         {(income['Tax Provision'] - income2['Tax Provision']) / income2['Tax Provision'] * 100:>9.2f}% | {(income2['Tax Provision'] - income3['Tax Provision']) / income3['Tax Provision'] * 100:>9.2f}% | {(income3['Tax Provision'] - income4['Tax Provision']) / income4['Tax Provision'] * 100:>9.2f}%")
        print(f"Net Income Growth:   {(income['Net Income'] - income2['Net Income']) / income2['Net Income'] * 100:>9.2f}% | {(income2['Net Income'] - income3['Net Income']) / income3['Net Income'] * 100:>9.2f}% | {(income3['Net Income'] - income4['Net Income']) / income4['Net Income'] * 100:>9.2f}%")
        print(" ")
        print(f"Fiscal Year:             {cash['date']:>10} | {cash2['date']:>10} | {cash3['date']:>10} | {cash4['date']:>10}")
        print(" ")
        print("Cash Flow as a Percentage of Revenue:")
        print(" ")
        print(f"Operating Cash Flow:     {cash['Operating Cash Flow'] / income['Total Revenue'] * 100:>9.2f}% | {cash2['Operating Cash Flow'] / income2['Total Revenue'] * 100:>9.2f}% | {cash3['Operating Cash Flow'] / income3['Total Revenue'] * 100:>9.2f}% | {cash4['Operating Cash Flow'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Investing Cash Flow:     {cash['Investing Cash Flow'] / income['Total Revenue'] * 100:>9.2f}% | {cash2['Investing Cash Flow'] / income2['Total Revenue'] * 100:>9.2f}% | {cash3['Investing Cash Flow'] / income3['Total Revenue'] * 100:>9.2f}% | {cash4['Investing Cash Flow'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Financing Cash Flow:     {cash['Financing Cash Flow'] / income['Total Revenue'] * 100:>9.2f}% | {cash2['Financing Cash Flow'] / income2['Total Revenue'] * 100:>9.2f}% | {cash3['Financing Cash Flow'] / income3['Total Revenue'] * 100:>9.2f}% | {cash4['Financing Cash Flow'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(f"Free Cash Flow:          {cash['Free Cash Flow'] / income['Total Revenue'] * 100:>9.2f}% | {cash2['Free Cash Flow'] / income2['Total Revenue'] * 100:>9.2f}% | {cash3['Free Cash Flow'] / income3['Total Revenue'] * 100:>9.2f}% | {cash4['Free Cash Flow'] / income4['Total Revenue'] * 100:>9.2f}%")
        print(" ")
        print("YOY changes:")
        print(" ")
        print(f"Operating Cash Flow:     {(cash['Operating Cash Flow'] - cash2['Operating Cash Flow']) / abs(cash2['Operating Cash Flow']) * 100:>9.2f}% | {(cash2['Operating Cash Flow'] - cash3['Operating Cash Flow']) / abs(cash3['Operating Cash Flow']) * 100:>9.2f}% | {(cash3['Operating Cash Flow'] - cash4['Operating Cash Flow']) / abs(cash4['Operating Cash Flow']) * 100:>9.2f}%")
        print(f"Investing Cash Flow:     {(cash['Investing Cash Flow'] - cash2['Investing Cash Flow']) / abs(cash2['Investing Cash Flow']) * 100:>9.2f}% | {(cash2['Investing Cash Flow'] - cash3['Investing Cash Flow']) / abs(cash3['Investing Cash Flow']) * 100:>9.2f}% | {(cash3['Investing Cash Flow'] - cash4['Investing Cash Flow']) / abs(cash4['Investing Cash Flow']) * 100:>9.2f}%")
        print(f"Financing Cash Flow:     {(cash['Financing Cash Flow'] - cash2['Financing Cash Flow']) / abs(cash2['Financing Cash Flow']) * 100:>9.2f}% | {(cash2['Financing Cash Flow'] - cash3['Financing Cash Flow']) / abs(cash3['Financing Cash Flow']) * 100:>9.2f}% | {(cash3['Financing Cash Flow'] - cash4['Financing Cash Flow']) / abs(cash4['Financing Cash Flow']) * 100:>9.2f}%")
        print(f"Free Cash Flow:          {(cash['Free Cash Flow'] - cash2['Free Cash Flow']) / abs(cash2['Free Cash Flow']) * 100:>9.2f}% | {(cash2['Free Cash Flow'] - cash3['Free Cash Flow']) / abs(cash3['Free Cash Flow']) * 100:>9.2f}% | {(cash3['Free Cash Flow'] - cash4['Free Cash Flow']) / abs(cash4['Free Cash Flow']) * 100:>9.2f}%")
        print(" ")
        print("=" * 60)

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

    print("=" * 60)
    print(" ")
    print("Credit Spread Analysis")
    print(" ")
    print(f"Bond Maturity Year: {bond_maturity:.0f}")
    print(" ")
    print(f"Market yield of debt: {yeild:.2f}%")
    print(" ")
    print(f"{tbill}y Treasury Yield: {treasury_yield:.2f}%")
    print(" ")
    print(f"\033[31mSpread to {tbill}y treasury: {yeild - treasury_yield:.2f}%\033[0m")
    print(" ")
    print("Negative spread indicates debt market has low liquidity for this companies bonds.")
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
    
    print("="*60)
    print(" ")
    print("Competitor Analysis")
    print(" ")
    print(f"{'Ticker':<10} {'Market Cap':>15} {'Enterprise Value':>15} {'Trailing P/E':>15} {'Forward P/E':>15} {'Yield':>15} {'Price to FCF':>15}")
    print(" ")
    
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
        
        print(f"{symbol:<10} {formatted_values[0]:>15} {formatted_values[1]:>15} {formatted_values[2]:>15} {formatted_values[3]:>15} {formatted_values[4]:>15} {formatted_values[5]:>15}")

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

    print("=" * 60)
    print(" ")
    print("Capital Structure Summary")
    print(" ")
    print(f"Market Capitalization: {format_large_number(cap)}")

    # Use .get() method to safely retrieve preferred stock value
    pre = data['balanceSheet'][0].get('Preferred Stock Equity', 0) or 0
    
    if pre != 0:
        preferred_formatted = format_large_number(pre)
        print(f"Preferred Stock Equity: {preferred_formatted}")
    
    print(f"\033[31mTotal Debt: {total_debt_formatted}\033[0m")

    cash = latest_balance_sheet['Cash And Cash Equivalents']
    cash_formatted = format_large_number(cash)

    print(f"Cash And Cash Equivalents: {cash_formatted}")
    print(" ")
     
    EV = stock.info.get('marketCap', None) + total_debt - latest_balance_sheet['Cash And Cash Equivalents'] + pre
    print(f"Enterprise Value: {format_large_number(EV)}")

    shares_outstanding = income['Basic Average Shares']
    shares_outstanding_formatted = format_large_number(shares_outstanding)
    print(" " )
    print(f"shares outstanding: {shares_outstanding_formatted}") 
    print(" " )
    netdebtpershare = (total_debt - latest_balance_sheet['Cash And Cash Equivalents']) / income['Basic Average Shares']
    print(f"Net Debt per Share: {netdebtpershare:.2f}")
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

    weight_of_debt = f"{weight_of_debt:.4f}"
    weight_of_equity = f"{weight_of_equity:.4f}"

    if 'Interest Expense' in income:
        interest_expense = income['Interest Expense']
    else:
        interest_expense = cash['Interest Paid Supplemental Data']
    
    if(interest_expense == None):
        cost_of_debt = 0
    else:
        cost_of_debt = abs(interest_expense / total_debt) * 100

    cost_of_equity = yield_10y + beta * ERP
    print("=" * 60)
    print(" ")
    print("WACC Calculation")
    print(" ")
    print(f"Cost of Equity: {cost_of_equity:.2f}%")
    print(" ")
    print(f"Cost of Debt: {cost_of_debt:.2f}%")
    print(" ")
    WACC = (float(weight_of_equity) * cost_of_equity) + (float(weight_of_debt) * cost_of_debt * (1 - tax_rate))
    print(f"\033[36mWACC: {WACC:.2f}%\033[0m")
    print(" ")
    print("=" * 60)

def calculate_growth_rate(terminal_value, last_fcf, wacc):
    """
    Calculate the implied perpetual growth rate from terminal value.
    
    Formula: Terminal Value = FCF × (1 + g) / (WACC - g)
    Solving for g: g = (TV × WACC - FCF) / (TV + FCF)
    
    Args:
        terminal_value: Terminal value
        last_fcf: Free cash flow in the last projection year
        wacc: Weighted average cost of capital (as decimal, e.g., 0.1177 for 11.77%)
    
    Returns:
        Growth rate as a decimal
    """
    # Rearranged formula: g = (TV × WACC - FCF) / (TV + FCF)
    numerator = (terminal_value * wacc) - last_fcf
    denominator = terminal_value + last_fcf
    growth_rate = numerator / denominator
    
    return growth_rate

def generate_excel(ticker, type):
    with open(f'{ticker}_financials.json', 'r') as file:
            data = json.load(file)

    income_statement = data['incomeStatement'][0]
    cash_flow_statement = data['cashFlowStatement'][0]
    balance_sheet = data['balanceSheet'][0]

    wb = openpyxl.load_workbook('template.xlsx')
    ws = wb.active
        
    debt = balance_sheet['Total Debt']
    cash = balance_sheet['Cash And Cash Equivalents']
    shares = income_statement['Basic Average Shares']

    ws["U17"] = debt/1000000
    ws["U15"] = cash/1000000
    ws["U21"] = shares/1000000

    rev = income_statement['Total Revenue']
    cogs = income_statement['Cost Of Revenue']
    operating_expense = income_statement['Operating Expense']
    other_expense = income_statement['Net Interest Income']
    tax = income_statement['Tax Provision']

    # Use .get() method with default value of 0 to handle None or missing keys
    div = income_statement.get("Preferred Stock Dividends", 0) or 0
    div += income_statement.get('Otherunder Preferred Stock Dividend', 0) or 0

    ws["C2"] = rev/1000000
    ws["C4"] = cogs/1000000
    ws["C10"] = operating_expense/1000000
    ws["C16"] = other_expense/1000000
    ws["C21"] = tax/1000000
    ws["C25"] = div/1000000

    lis = wacc_no_print(ticker)    
    wacc = lis[0]
    cost_of_equity = lis[1]
    cost_of_debt = lis[2]
    weight_of_equity = lis[3]
    weight_of_debt = lis[4]

    ws["U10"] = wacc/100
    ws["U8"] = weight_of_equity
    ws["U6"] = weight_of_debt
    ws["U2"] = cost_of_equity/100
    ws["U4"] = cost_of_debt/100

    ws["L6"] = cash_flow_statement['Change In Working Capital']/1000000
    ws["L10"] = cash_flow_statement['Capital Expenditure']/1000000

    ws["L12"] = cash_flow_statement['Free Cash Flow']/1000000 - div/1000000

    ws["L4"] = cash_flow_statement['Operating Cash Flow']/1000000 - cash_flow_statement['Change In Working Capital']/1000000 - income_statement['Net Income']/1000000

    ws["Q16"] = discount_factor(wacc/100, 5)
    ws["P16"] = discount_factor(wacc/100, 4)
    ws["O16"] = discount_factor(wacc/100, 3)
    ws["N16"] = discount_factor(wacc/100, 2)
    ws["M16"] = discount_factor(wacc/100, 1)

    # Save the workbook    
    if (type == "default"):
        wb.save(f'{ticker}_financial_model.xlsx')
        return
    elif(type == "expectation"):
        stock = yf.Ticker(ticker)
        price_to_fcf = None
        cap = stock.info.get('marketCap', None)
        marketcap = cap
    
        # Get free cash flow from cash flow statement
        cash_flow = stock.cashflow
        if not cash_flow.empty and 'Free Cash Flow' in cash_flow.index:
            # Get the most recent free cash flow (first column)
            fcf = cash_flow.loc['Free Cash Flow'].iloc[0]
            
            # If FCF is positive and we have market cap, calculate ratio
            if fcf and fcf > 0 and cap:
                price_to_fcf = cap / fcf

        ws["M18"] = (fcf * ws["M16"].value)/1000000

        yearone = (price_to_fcf/200) + 1
        ws["D3"] = yearone
        ws["D5"] = yearone
        ws["D11"] = yearone
        ws["C22"] = tax/income_statement['Pretax Income']
        tax_rate = tax/income_statement['Pretax Income']
        ws["D22"] = tax_rate
        ws["E22"] = tax_rate
        ws["F22"] = tax_rate
        ws["G22"] = tax_rate
        ws["H22"] = tax_rate
        ws["M5"] = yearone
        ws["M7"] = yearone
        ws["M11"] = yearone

        ws["D3"].number_format = '0.00'
        ws["D5"].number_format = '0.00'
        ws["D11"].number_format = '0.00'
        ws["M5"].number_format = '0.00'
        ws["M7"].number_format = '0.00'
        ws["M11"].number_format = '0.00'

        fcf = fcf * yearone 

        ws["N18"] = (fcf * ws["N16"].value)/1000000

        cap = cap * (1 + wacc/100)
        pfcftwo = cap / fcf
        yeartwo = (pfcftwo/200) + 1
        ws["E3"] = yeartwo
        ws["E5"] = yeartwo
        ws["E11"] = yeartwo
        ws["N5"] = yeartwo
        ws["N7"] = yeartwo
        ws["N11"] = yeartwo

        ws["E3"].number_format = '0.00'
        ws["E5"].number_format = '0.00'
        ws["E11"].number_format = '0.00'
        ws["N5"].number_format = '0.00'
        ws["N7"].number_format = '0.00'
        ws["N11"].number_format = '0.00'

        fcf = fcf * yeartwo

        ws["O18"] = (fcf * ws["O16"].value)/1000000

        cap = cap * (1 + wacc/100)
        pfcfthree = cap / fcf
        yearthree = (pfcfthree/200) + 1
        ws["F3"] = yearthree
        ws["F5"] = yearthree
        ws["F11"] = yearthree
        ws["O5"] = yearthree
        ws["O7"] = yearthree
        ws["O11"] = yearthree

        ws["F3"].number_format = '0.00'
        ws["F5"].number_format = '0.00'
        ws["F11"].number_format = '0.00'
        ws["O5"].number_format = '0.00'
        ws["O7"].number_format = '0.00'
        ws["O11"].number_format = '0.00'

        fcf = fcf * yearthree
        ws["P18"] = (fcf * ws["P16"].value)/1000000
        cap = cap * (1 + wacc/100)
        pfcffour = cap / fcf
        yearfour = (pfcffour/200) + 1
        ws["G3"] = yearfour
        ws["G5"] = yearfour
        ws["G11"] = yearfour
        ws["P5"] = yearfour
        ws["P7"] = yearfour
        ws["P11"] = yearfour

        ws["P11"].number_format = '0.00'
        ws["G3"].number_format = '0.00'
        ws["G5"].number_format = '0.00'
        ws["G11"].number_format = '0.00'
        ws["P5"].number_format = '0.00'
        ws["P7"].number_format = '0.00'

        fcf = fcf * yearfour
        ws["Q18"] = (fcf * ws["Q16"].value)/1000000
        cap = cap * (1 + wacc/100)
        pfcffive = cap / fcf
        yearfive = (pfcffive/200) + 1
        ws["H3"] = yearfive
        ws["H5"] = yearfive
        ws["H11"] = yearfive
        ws["Q5"] = yearfive
        ws["Q7"] = yearfive
        ws["Q11"] = yearfive

        ws["H3"].number_format = '0.00'
        ws["H5"].number_format = '0.00'
        ws["H11"].number_format = '0.00'
        ws["Q5"].number_format = '0.00'
        ws["Q7"].number_format = '0.00'
        ws["Q11"].number_format = '0.00'

        # subtracting too much need to account for quaters that have already happened
        TV = (marketcap/1000000) - (ws["M18"].value + ws["N18"].value + ws["O18"].value + ws["P18"].value + ws["Q18"].value) - balance_sheet['Cash And Cash Equivalents']/1000000 + balance_sheet['Total Debt']/1000000
        ws["Q20"] = TV

        TTV = TV 

        TV = TV*(1 + wacc/100)**5

        ws["K24"] = TV
        
        g = calculate_growth_rate(TV*1000000, fcf, wacc/100)

        ws["J25"] = g

        wb.save(f'{ticker}_financial_model.xlsx')
        return

def discount_factor(rate, period):
    return 1 / ((1 + rate) ** period)

def wacc_no_print(ticker):
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

    weight_of_debt = f"{weight_of_debt:.4f}"
    weight_of_equity = f"{weight_of_equity:.4f}"

    if 'Interest Expense' in income:
        interest_expense = income['Interest Expense']
    else:
        interest_expense = cash['Interest Paid Supplemental Data']
    
    if(interest_expense == None):
        cost_of_debt = 0
    else:
        cost_of_debt = abs(interest_expense / total_debt) * 100

    cost_of_equity = yield_10y + beta * ERP
    
    WACC = (float(weight_of_equity) * cost_of_equity) + (float(weight_of_debt) * cost_of_debt * (1 - tax_rate))

    lis = [WACC, cost_of_equity, cost_of_debt, weight_of_equity, weight_of_debt]

    return lis


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

@app.command()
def load(
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
def st(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company")
):
    '''Display financial statements summary for the given ticker'''
    Statements(ticker)

@app.command()
def ce(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company")
):
    '''Display competitor analysis for the given ticker'''
    compare(ticker)

@app.command()
def excel(
    ticker: str = typer.Argument(..., help="Ticker symbol of the company"),
    type: str = typer.Option(..., "--type", "-t", help="Type of Excel to generate")
):
    """
    Generate an Excel file with financial data for the given ticker.
    """
    typer.echo(f"Generating {type} Excel file for ticker: {ticker}")
    if(type == "default"):
        generate_excel(ticker, "default")
    
    elif(type == "expectation"):
        generate_excel(ticker, "expectation")
    else:
        typer.echo("Invalid type specified. Use 'default' or 'expectation'.")

filename = 'tasks.json'

def load_tasks():
    """Load tasks from JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open(filename, 'w') as f:
        json.dump(tasks, f, indent=2)

@app.command()
def add(description: str = typer.Argument(..., help="Task description")):
    """Add a new task"""
    tasks = load_tasks()
    task = {
        'id': max([t['id'] for t in tasks], default=0) + 1,
        'description': description,
        'completed': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    tasks.append(task)
    save_tasks(tasks)
    typer.secho(f"✓ Task added successfully (ID: {task['id']})", fg=typer.colors.GREEN)

@app.command()
def remove(task_id: int = typer.Argument(..., help="ID of task to remove")):
    """Remove a task by ID"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if task:
        tasks.remove(task)
        save_tasks(tasks)
        typer.secho(f"✓ Task {task_id} removed successfully", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Task with ID {task_id} not found", fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command()
def complete(task_id: int = typer.Argument(..., help="ID of task to mark as completed")):
    """Mark a task as completed"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if task:
        if task['completed']:
            typer.secho(f"Task {task_id} is already completed", fg=typer.colors.YELLOW)
        else:
            task['completed'] = True
            task['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_tasks(tasks)
            typer.secho(f"✓ Task {task_id} marked as completed", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Task with ID {task_id} not found", fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command()
def list(
    all: bool = typer.Option(False, "--all", "-a", help="Show all tasks including completed"),
    completed_only: bool = typer.Option(False, "--completed", "-c", help="Show only completed tasks")
):
    """List all tasks"""
    tasks = load_tasks()
    
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
    
    typer.echo("\n" + "="*60)
    typer.secho(header, fg=typer.colors.CYAN, bold=True)
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
def search(keyword: str = typer.Argument(..., help="Keyword to search for in task descriptions")):
    """Search tasks by keyword"""
    tasks = load_tasks()
    
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
def clear(
    completed: bool = typer.Option(False, "--completed", "-c", help="Clear only completed tasks"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt")
):
    """Clear all tasks or only completed tasks"""
    tasks = load_tasks()
    
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
        save_tasks(remaining_tasks)
        typer.secho(f"✓ Cleared {len(tasks_to_clear)} completed task(s)", fg=typer.colors.GREEN)
    else:
        save_tasks([])
        typer.secho("✓ All tasks cleared", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
