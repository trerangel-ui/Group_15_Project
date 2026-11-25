import pandas as pd
import yfinance as yf
import plotly.graph_objects as go


def make_investment_comparison(data, ticker, period, metal="Gold", crypto="Bitcoin"):
    # Use adjusted stock prices where available
    if "Adj Close" in data.columns:
        stock_close = data["Adj Close"].dropna()
    else:
        stock_close = data["Close"].dropna()

    crypto_symbols = {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
    }

    metal_symbols = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Platinum": "PL=F",
    }

    assets = {
        crypto: crypto_symbols[crypto],
        "Treasury Bonds (IEF)": "IEF",
        metal: metal_symbols[metal],
        "Real Estate (VNQ)": "VNQ",
    }

    # Start with the selected stock
    comparison = pd.DataFrame({
        ticker: stock_close
    })

    # Download the other four investments
    for name, symbol in assets.items():

        asset_data = yf.Ticker(symbol).history(
            period=period,
            auto_adjust=True
        )

        if asset_data.empty or asset_data["Close"].dropna().empty:
            raise ValueError(f"No price data was returned for {name}.")

        asset_close = asset_data["Close"].dropna()

        # Align all investments to the stock's trading dates
        asset_close = asset_close.reindex(
            comparison.index,
            method="ffill"
        )

        comparison[name] = asset_close

    comparison = comparison.dropna()

    if comparison.empty:
        raise ValueError("No overlapping investment data was found.")

    # Calculate percentage returns from the starting date
    returns = (
        comparison.div(comparison.iloc[0]).sub(1)
    ) * 100

    # Create interactive Plotly chart
    fig = go.Figure()

    line_colors = {
        ticker: "#176B87",       # Donkerblauw
        crypto: "#8E44AD",       # Paars
        "Treasury Bonds (IEF)": "#26966F",  # Groen
        metal: "#F1C40F",        # Goudgeel
        "Real Estate (VNQ)": "#E67E22",     # Oranje
    }

    for column in returns.columns:

        fig.add_trace(go.Scatter(
            x=returns.index,
            y=returns[column],
            mode="lines",
            name=column,
            line=dict(
                width=2,
                color=line_colors.get(column, None)
            ),
            hovertemplate=(
                "%{x|%d %b %Y}<br>"
                "%{y:.2f}% return"
                "<extra>%{fullData.name}</extra>"
            )
        ))

    fig.update_layout(
        title="Investment Performance Comparison",
        xaxis_title="Date",
        yaxis_title="Return (%)",
        hovermode="x unified",
        template="plotly_white",
        legend_title="Investments",
        height=450,
        xaxis=dict(
            rangeslider=dict(visible=True)
        ),
        yaxis=dict(
            ticksuffix="%"
        )
    )

    return fig
