import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import gradio as gr

# Test downloading stock data

ticker = "AAPL"
period = "1mo"

stock_data = yf.Ticker(ticker).history(period=period)

print(stock_data.head())

# Get Apple's closing prices
stock_close = stock_data["Close"]

# Calculate daily percentage changes
stock_returns = stock_close.pct_change() * 100

# Display the first few results
print(stock_returns.head())

# Download historical gold prices
gold_data = yf.Ticker("GC=F").history(period=period)

# Select gold's closing prices
gold_close = gold_data["Close"]

# Calculate gold's daily percentage changes
gold_returns = gold_close.pct_change() * 100

# Display the first five results
print("\nGold daily percentage changes:")
print(gold_returns.head())




# Match Apple and gold returns by date

# Remove timezone information so dates can be compared
stock_returns.index = stock_returns.index.tz_localize(None)
gold_returns.index = gold_returns.index.tz_localize(None)

# Keep only the calendar date
stock_returns.index = stock_returns.index.normalize()
gold_returns.index = gold_returns.index.normalize()

# Combine both sets of returns into one table
combined_returns = pd.concat(
    [
        stock_returns.rename("Apple"),
        gold_returns.rename("Gold")
    ],
    axis=1
).dropna()

# Display the first five matching dates
print("\nCombined Apple and Gold returns:")
print(combined_returns.head())