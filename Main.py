import json
import yfinance as yf
from datetime import datetime
import pandas as pd
import requests

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
        print("Fetching most recent quarterly balance sheet...")
        quarterly_bs = self.stock.quarterly_balance_sheet
        
        if quarterly_bs is None or quarterly_bs.empty:
            return []
        
        # Get only the most recent quarter (first column)
        most_recent = quarterly_bs.iloc[:, [0]]
        return self.convert_dataframe_to_dict(most_recent)
    
    def get_income_statement(self):
        """Fetch income statement data"""
        print("Fetching income statement...")
        return self.convert_dataframe_to_dict(self.stock.financials)
    
    def get_cash_flow(self):
        """Fetch cash flow statement data"""
        print("Fetching cash flow statement...")
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
            
            print(f"\n✓ Financial data saved to {filename}")
            print(f"✓ Company: {financials['companyName']}")
            print(f"✓ Currency: {financials['currency']}")
            
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


def get_risk_free_rate():
    # Fetch current U.S. 10-year Treasury yield from an external API or web scrape
    # Here we use a public API for demonstration (FRED, requires API key; for demo, we use a placeholder)
    # Replace 'YOUR_API_KEY' with your FRED API key
    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': 'DGS10',
        'api_key': 'YOUR_API_KEY',
        'file_type': 'json',
        'sort_order': 'desc',
        'limit': 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'observations' in data and len(data['observations']) > 0:
        return float(data['observations'][0]['value']) / 100
    else:
        # Fallback, use a static value
        return 0.045  # 4.5%

def get_market_return():
    # For demo, use a static value (e.g., 10% for S&P 500)
    return 0.10

def get_tax_rate(ticker):
    # Use Financial Modeling Prep API for tax rate (requires API key, use placeholder)
    url = f'https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=1&apikey=YOUR_API_KEY'
    response = requests.get(url)
    data = response.json()
    if data and len(data) > 0:
        income_before_tax = data[0]['incomeBeforeTax']
        income_tax_expense = data[0]['incomeTaxExpense']
        if income_before_tax > 0:
            return income_tax_expense / income_before_tax
    return 0.21  # fallback to US corporate tax rate

def get_cost_of_debt(ticker):
    # Use Financial Modeling Prep API for interest expense and total debt (requires API key)
    url_is = f'https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=1&apikey=YOUR_API_KEY'
    url_bs = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?limit=1&apikey=YOUR_API_KEY'
    resp_is = requests.get(url_is).json()
    resp_bs = requests.get(url_bs).json()
    if resp_is and resp_bs:
        interest_expense = abs(resp_is[0]["interestExpense"])
        total_debt = resp_bs[0]["shortTermDebt"] + resp_bs[0]["longTermDebt"]
        if total_debt > 0:
            return interest_expense / total_debt
    return 0.03  # fallback estimate

def calculate_wacc(ticker):
    # Fetch from yfinance
    stock = yf.Ticker(ticker)
    info = stock.info

    # Market Value of Equity
    market_cap = info['marketCap']

    # Market Value of Debt
    total_debt = info.get('totalDebt', 0)
    if total_debt is None:
        total_debt = 0

    # Beta
    beta = info.get('beta', 1)

    # Cost of Equity
    rf = get_risk_free_rate()
    rm = get_market_return()
    cost_of_equity = rf + beta * (rm - rf)

    # Cost of Debt
    cost_of_debt = get_cost_of_debt(ticker)

    # Tax Rate
    tax_rate = get_tax_rate(ticker)

    # WACC calculation
    E = market_cap
    D = total_debt
    V = E + D
    if V == 0:
        raise ValueError("Zero enterprise value.")

    wacc = (E / V) * cost_of_equity + (D / V) * cost_of_debt * (1 - tax_rate)
    return {
        "cost_of_equity": cost_of_equity,
        "cost_of_debt": cost_of_debt,
        "tax_rate": tax_rate,
        "market_cap": E,
        "total_debt": D,
        "wacc": wacc
    }


def main():
    """Main function to run the financial data fetcher"""
    print("=" * 60)
    print("Yahoo Finance Financial Data Fetcher")
    print("=" * 60)
    
    ticker = input("\nEnter stock ticker (e.g., AAPL, MSFT, GOOGL): ").strip()
    
    if not ticker:
        ticker = "AAPL"  # Default to Apple
        print(f"No ticker provided, using default: {ticker}")
    
    fetcher = FinancialDataFetcher(ticker)
    success = fetcher.save_to_json()
    
    if success:
        print("\n✓ Done! Check the generated JSON file for the financial data.")
    else:
        print("\n✗ Failed to fetch and save financial data.")
        print("Please check that the ticker symbol is valid and try again.")
    
    # Calculate WACC for the same ticker
    try:
        print("\n" + "=" * 60)
        print("Calculating WACC...")
        print("=" * 60)
        result = calculate_wacc(ticker)
        print(f"\nWACC for {ticker}: {result['wacc']:.4f} ({result['wacc']*100:.2f}%)")
        print("\nDetails:")
        print(f"  Cost of Equity: {result['cost_of_equity']:.4f} ({result['cost_of_equity']*100:.2f}%)")
        print(f"  Cost of Debt: {result['cost_of_debt']:.4f} ({result['cost_of_debt']*100:.2f}%)")
        print(f"  Tax Rate: {result['tax_rate']:.4f} ({result['tax_rate']*100:.2f}%)")
        print(f"  Market Cap: ${result['market_cap']:,.0f}")
        print(f"  Total Debt: ${result['total_debt']:,.0f}")
    except Exception as e:
        print(f"\n✗ Error calculating WACC: {e}")


if __name__ == "__main__":
    main()
