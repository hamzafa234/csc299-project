import json
import sys
import yfinance as yf
from datetime import datetime
import pandas as pd
import requests
from openai import OpenAI

client = OpenAI(
  api_key="xxxxxx"
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
        
def calculate_expectations(WACC):

    with open(f'{ticker}_financials.json', 'r') as file:
            data = json.load(file)


    stock = yf.Ticker(ticker)
    current_price = stock.info.get("currentPrice")
    
    cash = data['cashFlowStatement'][0]
    fcf = cash['Free Cash Flow']
    income = data['incomeStatement'][0]
    fcf_per_share = fcf / income['Basic Average Shares']
    price_to_fcf = current_price / fcf_per_share

    if price_to_fcf > 0:

        print("=" * 60)
        print(" ")
        print("Growth needed to justify current Price Based on FCF per share")

        yearone = price_to_fcf/2
        yearone = yearone / 100
        Eone = fcf_per_share * (1 + yearone)
        print(f"\033[32mYear 1 Growth needed: {yearone*100:.2f}%\033[0m")
        print(f"Year 1 FCF per share needed: {Eone:.2f}")
        print(" ")
        current_price = current_price * ((WACC / 100) + 1)
        yeartwo_pfcf = current_price/Eone 
        yeartwogrowth = yeartwo_pfcf/200
        print(f"\033[32mYear 2 Growth needed: {yeartwogrowth*100:.2f}%\033[0m")
        Etwo = Eone * (1 + yeartwogrowth)
        print(f"Year 2 FCF per share needed: {Etwo:.2f}")
        print(" ")
        current_price = current_price * ((WACC / 100) + 1) 
        yearthree_pfcf = current_price/Etwo
        yearthreegrowth = yearthree_pfcf/200
        print(f"\033[32mYear 3 Growth needed: {yearthreegrowth*100:.2f}%\033[0m")
        Ethree = Etwo * (1 + yearthreegrowth)
        print(f"Year 3 FCF per share needed: {Ethree:.2f}")
        print(" ")
        current_price = current_price * ((WACC / 100) + 1)
        yearfour_pfcf = current_price/Ethree
        yearfourgrowth = yearfour_pfcf/200
        print(f"\033[32mYear 4 Growth needed: {yearfourgrowth*100:.2f}%\033[0m")
        Efour = Ethree * (1 + yearfourgrowth)
        print(f"Year 4 FCF per share needed: {Efour:.2f}")
        print(" ")
        current_price = current_price * ((WACC / 100) + 1)
        yearfive_pfcf = current_price/Efour
        yearfivegrowth = yearfive_pfcf/200
        print(f"\033[32mYear 5 Growth needed: {yearfivegrowth*100:.2f}%\033[0m")
        Efive = Efour * (1 + yearfivegrowth)
        print(f"Year 5 FCF per share needed: {Efive:.2f}")
        print(" ")
        print("=" * 60) 

    else:
        
        print("Price to Free Cash Flow must be positive to compute growth rates needed.")

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

def Statements():
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

def credit_spread_analysis():
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

def compare():
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
    print(f"{'Ticker':<10} {'Market Cap':>15} {'Trailing P/E':>15} {'Forward P/E':>15}")
    print(" ")
    
    for symbol in comp_data[:6]:
        values = getCompVal(symbol)
        print(f"{symbol:<10} {values[0]:>15} {values[1]:>15} {values[2]:>15}")
    
    print(" ")
    print("=" * 60)

def getCompVal(ticker):
    stock = yf.Ticker(ticker)
    cap = stock.info.get('marketCap', None)
    pe = stock.info.get('trailingPE', None)
    fpe = stock.info.get('forwardPE', None)
    list = [cap, pe, fpe]
    return list
    

def capital_structure_summary():
    with open(f'{ticker}_financials.json', 'r') as file:
            data = json.load(file)

    total_debt = data['balanceSheet'][0]['Total Debt']
    latest_balance_sheet = data['balanceSheet'][0]
    income = data['incomeStatement'][0]

    print("=" * 60)
    print(" ")
    print("Capital Structure Summary")
    print(" ")
    print(f"Market Capitalization: {cap}")
    print(f"\033[31mTotal Debt: {total_debt}\033[0m")
    print(f"\033[32mCash and Cash Equivalents: {latest_balance_sheet['Cash And Cash Equivalents']}\033[0m")
    EV = cap + total_debt - latest_balance_sheet['Cash And Cash Equivalents']
    print(f"Enterprise Value: {EV}")

    print(" " )
    print(f"shares outstanding: {income['Basic Average Shares']}") 
    netdebtpershare = (total_debt - latest_balance_sheet['Cash And Cash Equivalents']) / income['Basic Average Shares'] 
    print(f"Net Debt per Share: {netdebtpershare:.2f}")
    print(" " )
    print("=" * 60)


def wacc_calculation():
    global yield_10y
    yield_10y = get_10y_treasury_yield()

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

    interest_expense = income['Interest Expense']
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
    return WACC

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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("="*60 + "\n")
        print("Equity Research Terminal")
        print("="*60 + "\n")
        print("Usage: python Main.py <TICKER>")
        sys.exit(1)    
    
    command = sys.argv[1].lower()
    main(command)
    WACC = wacc_calculation()
    capital_structure_summary()
    credit_spread_analysis()
    Statements()
    calculate_expectations(WACC)
    compare()
