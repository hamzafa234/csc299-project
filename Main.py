import yfinance as yf
import requests

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
    # For demo, use a static value (e.g., 8% for S&P 500)
    return 0.08

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

# Example usage:
if __name__ == "__main__":
    ticker = "AAPL"
    result = calculate_wacc(ticker)
    print(f"WACC for {ticker}: {result['wacc']:.4f}")
    print("Details:", result)