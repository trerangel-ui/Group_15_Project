"""Stock vs crypto panel (Achille).

Question asked by this panel: is crypto a diversifier for a stock investor,
or does it fall at the same time as the stock?

One chart: the drawdown from peak (%) of the stock and of the crypto
(filled area chart), with the stock's worst day annotated. The correlation
of their daily returns is shown in the title and explained in the summary.

The panel reuses the dashboard's ticker, period and Load button, and adds
a Bitcoin / Ethereum choice.
"""

import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

# Yahoo Finance tickers for the cryptos
CRYPTOS = {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD"}
CRYPTO_COLORS = {"Bitcoin": "#F2A900", "Ethereum": "#7A6FD0"}
STOCK_COLOR = "#176B87"


def get_closing_prices(symbol, period):
    """Download daily closing prices for one symbol, indexed by calendar date."""
    data = yf.Ticker(symbol).history(period=period, auto_adjust=False)
    close = data["Close"].dropna() if not data.empty else pd.Series(dtype=float)
    if close.empty:
        raise ValueError(f"No closing-price data was returned for {symbol}.")
    # Stocks and cryptos carry different time zones, so keep the date only
    close.index = pd.to_datetime(close.index).tz_localize(None).normalize()
    return close


def load_comparison(ticker, crypto, period):
    """Return one DataFrame with the stock and the crypto on the same dates.

    Crypto trades 7 days a week but stocks do not, so only the stock's
    trading days are kept (dropna removes weekends and holidays).
    """
    stock_close = get_closing_prices(ticker, period)
    crypto_close = get_closing_prices(CRYPTOS[crypto], period)

    prices = pd.DataFrame({"Stock": stock_close, crypto: crypto_close}).dropna()
    if len(prices) < 30:
        raise ValueError("Not enough overlapping trading days. Try a longer period.")
    return prices


def drawdown(prices):
    """Fall from the highest price reached so far, in %."""
    return (prices / prices.cummax() - 1) * 100


def summarise(ticker, crypto, dd, correlation):
    """Short text that tells the story of the chart."""
    worst_day = dd["Stock"].idxmin()
    if correlation > 0.3:
        verdict = f"they tend to fall together, so {crypto} does not diversify much"
    elif correlation < -0.3:
        verdict = f"they tend to move in opposite directions, so {crypto} diversifies"
    else:
        verdict = f"they are only weakly linked, so {crypto} offers some diversification"
    return (
        f"Worst {ticker} drawdown: **{dd['Stock'].min():.1f}%** on {worst_day:%d %b %Y}, "
        f"while {crypto} was **{dd.loc[worst_day, crypto]:.1f}%** below its peak. "
        f"Correlation of daily returns: **{correlation:.2f}**, {verdict}."
    )


def make_crypto_chart(ticker, crypto, period):
    """Build the chart and its summary for the chosen inputs."""
    prices = load_comparison(ticker, crypto, period)
    returns = prices.pct_change().dropna()
    correlation = returns["Stock"].corr(returns[crypto])
    dd = drawdown(prices)

    fig, ax = plt.subplots(figsize=(8, 3.2))

    # Drawdowns: how far each asset is below its previous peak
    ax.fill_between(dd.index, dd["Stock"], 0, color=STOCK_COLOR, alpha=0.35, label=ticker)
    ax.fill_between(dd.index, dd[crypto], 0, color=CRYPTO_COLORS[crypto], alpha=0.35, label=crypto)
    ax.set_title(f"{ticker} vs {crypto}: fall from peak")
    ax.set_ylabel("Drawdown from peak (%)")
    ax.legend(frameon=False, loc="lower left")

    # Correlation of daily returns, shown in the top-right corner
    ax.text(
        0.99, 0.04, f"Correlation of daily returns: {correlation:.2f}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color="#333333",
    )

    # Annotation: the stock's worst moment, and where the crypto stood that day
    worst_day = dd["Stock"].idxmin()
    # Put the label on the left of the arrow when the worst day is near the right edge
    near_right_edge = dd.index.get_loc(worst_day) > len(dd) * 0.7
    ax.annotate(
        f"{ticker} worst: {dd['Stock'].min():.1f}%\n{crypto} that day: {dd.loc[worst_day, crypto]:.1f}%",
        xy=(worst_day, dd["Stock"].min()),
        xytext=(-15 if near_right_edge else 15, -5),
        textcoords="offset points",
        ha="right" if near_right_edge else "left",
        fontsize=8,
        arrowprops={"arrowstyle": "->", "color": "#555555"},
    )

    ax.grid(axis="y", alpha=0.22)
    ax.tick_params(axis="x", labelrotation=25)
    fig.tight_layout()

    return fig, summarise(ticker, crypto, dd, correlation)


def placeholder(message):
    """Empty chart with a message, used before loading or when something fails."""
    figure, axis = plt.subplots(figsize=(8, 3.2))
    axis.text(0.5, 0.5, message, ha="center", va="center", color="#666666")
    axis.set_title("Stock vs crypto")
    axis.set_axis_off()
    figure.tight_layout()
    return figure


def update_crypto_panel(ticker, period, crypto):
    """Called by Gradio when the dashboard is loaded or the crypto choice changes."""
    ticker = (ticker or "").strip().upper()
    try:
        if not ticker:
            raise ValueError("Enter a ticker symbol, such as AAPL.")
        return make_crypto_chart(ticker, crypto, period)
    except Exception as error:
        return placeholder(str(error)), f"Unable to compare {ticker or 'ticker'} with {crypto}: {error}"


def build_crypto_panel(ticker_input, period_input, load_button):
    """Add the panel to the dashboard. Call it inside `with demo:`.

    It reuses the dashboard's ticker, period and Load button, and adds one
    small control of its own: the choice between Bitcoin and Ethereum.
    """
    with gr.Group():
        gr.Markdown("### Stock vs Crypto")
        crypto_input = gr.Radio(choices=list(CRYPTOS), value="Bitcoin", label="Crypto")
        crypto_plot = gr.Plot(value=placeholder("Enter a ticker and select Load charts"), label="Stock vs crypto")
        crypto_summary = gr.Markdown("Load a ticker to compare it with Bitcoin or Ethereum.")

    inputs = [ticker_input, period_input, crypto_input]
    outputs = [crypto_plot, crypto_summary]
    load_button.click(fn=update_crypto_panel, inputs=inputs, outputs=outputs)
    crypto_input.change(fn=update_crypto_panel, inputs=inputs, outputs=outputs)

    return crypto_plot
