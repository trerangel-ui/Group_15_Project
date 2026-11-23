import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import gradio as gr
import matplotlib.dates as mdates
import plotly.graph_objects as go 

# Precious metals and their Yahoo Finance ticker symbols
metals = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F"
}

# Colours for each precious metal
metal_colours = {
    "Gold": "#D4A017",
    "Silver": "#8A96A3",
    "Platinum": "#0D9488"
}

# Choose which metal to compare for test!!!!!
selected_metal = "Platinum"

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

gold_data = yf.Ticker(metals[selected_metal]).history(period=period)

# Select gold's closing prices
gold_close = gold_data["Close"]

# Calculate gold's daily percentage changes
gold_returns = gold_close.pct_change() * 100

# Display the first five results
print(f"\n{selected_metal} daily percentage changes:")
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
        gold_returns.rename(selected_metal)
    ],
    axis=1
).dropna()

# Display the first five matching dates
print("\nCombined Apple and {selected_metal} returns:")
print(combined_returns.head())





# Create the graph
fig, ax = plt.subplots(figsize=(7, 4))

# Plot Apple's daily returns as blue dots
ax.scatter(
    combined_returns.index,
    combined_returns["Apple"],
    color="blue",
    label="Apple",
    s=25
)

# Plot gold's daily returns as gold dots
ax.scatter(
    combined_returns.index,
    combined_returns[selected_metal],
    color=metal_colours[selected_metal],
    label=selected_metal,
    s=25
)

# Add a horizontal line at 0%
ax.axhline(0, color="gray", linestyle="--")

# Add labels and title
ax.set_xlabel("Date")
ax.set_ylabel("Daily Return (%)")
ax.set_title(f"Apple vs {selected_metal}: Daily Percentage Returns")

# Show fewer dates on the X-axis
ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))

# Display dates in a shorter format
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))

# Rotate date labels slightly
plt.xticks(rotation=30)

# Show which dots belong to which investment
ax.legend()

# Improve spacing
plt.tight_layout()

# Save the graph as an image
plt.savefig("metals_graph.png")

# Close the figure
plt.close()







# GRADIO DROP DOWN ----

# Create a graph using the metal selected in Gradio
def choose_metal(metal, selected_period):

    # Download Apple's prices
    stock_data = yf.Ticker("AAPL").history(period=selected_period)

    # Download the selected precious metal's prices
    metal_data = yf.Ticker(metals[metal]).history(period=selected_period)

    # Keep daily closing prices for both investments
    stock_daily_close = stock_data["Close"].copy()
    metal_daily_close = metal_data["Close"].copy()



    # Choose the return frequency based on the selected period
    if selected_period in ["1mo", "3mo", "6mo"]:
        frequency = "Daily"
    else:
        frequency = "Weekly"

   
    # Calculate daily percentage returns
    stock_daily_returns = stock_daily_close.pct_change() * 100
    metal_daily_returns = metal_daily_close.pct_change() * 100

    # Calculate weekly closing prices
    stock_weekly_close = stock_daily_close.resample("W-FRI").last()
    metal_weekly_close = metal_daily_close.resample("W-FRI").last()

    # Calculate weekly percentage returns
    stock_weekly_returns = stock_weekly_close.pct_change() * 100
    metal_weekly_returns = metal_weekly_close.pct_change() * 100

    # Choose which returns to display initially
    if frequency == "Daily":
        stock_returns = stock_daily_returns
        metal_returns = metal_daily_returns
    else:
        stock_returns = stock_weekly_returns
        metal_returns = metal_weekly_returns

        # Standardise Apple's dates
    stock_returns.index = stock_returns.index.tz_localize(None)
    stock_returns.index = stock_returns.index.normalize()

    # Standardise the metal's dates
    metal_returns.index = metal_returns.index.tz_localize(None)
    metal_returns.index = metal_returns.index.normalize()       

    # Match the date format used for Apple
    metal_returns.index = metal_returns.index.tz_localize(None)
    metal_returns.index = metal_returns.index.normalize()

    # Combine Apple and the selected metal
    comparison = pd.concat(
        [
            stock_returns.rename("Apple"),
            metal_returns.rename(metal)
        ],
        axis=1
    ).dropna()

    # Create an interactive Plotly graph
    fig = go.Figure()

    # Add Apple's percentage returns
    fig.add_trace(go.Scatter(
        x=comparison.index,
        y=comparison["Apple"],
        mode="markers",
        name="Apple",
        marker=dict(color="blue", size=6)
    ))

    # Add the selected metal's percentage returns
    fig.add_trace(go.Scatter(
        x=comparison.index,
        y=comparison[metal],
        mode="markers",
        name=metal,
        marker=dict(
            color=metal_colours[metal],
            size=6
        )
    ))

    # Add graph labels and formatting
    fig.update_layout(
        title=f"Apple vs {metal}: {frequency} Percentage Returns",
        xaxis_title="Date",
        yaxis_title=f"{frequency} Return (%)",
        template="plotly_white",
        hovermode="x unified",
        height=450
    )

    # Add a horizontal reference line at 0%
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    return fig



demo = gr.Interface(
    fn=choose_metal,

    inputs=[
        gr.Dropdown(
            choices=["Gold", "Silver", "Platinum"],
            value="Gold",
            label="Choose a precious metal"
        ),

        gr.Dropdown(
            choices=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            value="1mo",
            label="Choose a time period"
        )
    ],

    outputs=gr.Plot(label="Metals Comparison")
)

demo.launch()

