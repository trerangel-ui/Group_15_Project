"""Stock vs crypto panel (Achille).

Question asked by this panel: is crypto a diversifier for a stock investor,
or does it fall at the same time as the stock?

One chart slot, two views (chosen with the "View" control):
1. Falls from peak: the drawdown (%) of the stock and of the crypto
   (filled area chart), with the stock's worst day annotated.
2. Rolling correlation: the 60-day correlation of their daily returns
   (line chart): above 0 = they move together, below 0 = they move in
   opposite directions (crypto diversifies).

The panel reuses the dashboard's ticker, period and Load button, and adds
two controls of its own: the crypto (Bitcoin / Ethereum) and the view.
"""

import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

# Yahoo Finance tickers for the cryptos
CRYPTOS = {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD"}
CRYPTO_COLORS = {"Bitcoin": "#F2A900", "Ethereum": "#7A6FD0"}
STOCK_COLOR = "#176B87"
VIEWS = ["Falls from peak", "Rolling correlation"]
ROLLING_WINDOW = 60  # trading days, about 3 months


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
    """Short text that tells the story of the chart, in two parts.

    1. Day to day: are the daily returns linked (correlation)?
    2. In a crash: on the stock's worst day, did the crypto hold up better?
    """
    if correlation > 0.3:
        daily = "they tend to move together"
    elif correlation < -0.3:
        daily = "they tend to move in opposite directions"
    else:
        daily = "they are only weakly linked"

    worst_day = dd["Stock"].idxmin()
    stock_fall = dd.loc[worst_day, "Stock"]
    crypto_fall = dd.loc[worst_day, crypto]
    if crypto_fall < stock_fall:
        crash = f"{crypto} did not protect: it was even further below its peak"
    else:
        crash = f"{crypto} held up better than the stock"

    return (
        f"**Day to day:** correlation of daily returns is **{correlation:.2f}**, so {daily}.  \n"
        f"**In the worst fall:** on {worst_day:%d %b %Y}, {ticker} was **{-stock_fall:.1f}%** "
        f"below its peak and {crypto} **{-crypto_fall:.1f}%**, so {crash}. "
        f"{crypto}'s own worst fall over the period: **{dd[crypto].min():.1f}%** from its peak."
    )


def draw_drawdowns(ax, ticker, crypto, dd, correlation):
    """View 1: how far each asset is below its previous peak."""
    # Crypto as a light area, stock as a solid line on top, so they never mix
    ax.fill_between(dd.index, dd[crypto], 0, color=CRYPTO_COLORS[crypto], alpha=0.3, label=crypto)
    ax.plot(dd.index, dd["Stock"], color=STOCK_COLOR, linewidth=1.6, label=ticker)
    ax.set_title(f"{ticker} vs {crypto}: fall from peak")
    ax.set_ylabel("Drawdown from peak (%)")
    ax.legend(frameon=False, loc="lower left")

    # Annotation: the stock's worst moment, and where the crypto stood that day
    worst_day = dd["Stock"].idxmin()
    # Put the label on the left of the arrow when the worst day is near the right edge
    near_right_edge = dd.index.get_loc(worst_day) > len(dd) * 0.7
    ax.annotate(
        f"{ticker} worst: {dd['Stock'].min():.1f}%\n{crypto} that day: {dd.loc[worst_day, crypto]:.1f}%",
        xy=(worst_day, dd["Stock"].min()),
        xytext=(-15 if near_right_edge else 15, -12),
        va="top",
        textcoords="offset points",
        ha="right" if near_right_edge else "left",
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "none", "alpha": 0.85},
        arrowprops={"arrowstyle": "->", "color": "#555555"},
    )


def draw_rolling_correlation(ax, ticker, crypto, rolling_corr):
    """View 2: correlation of daily returns over a moving 60-day window."""
    # Colour-blind friendly: orange above 0 (move together), blue below 0 (opposite moves)
    ax.fill_between(rolling_corr.index, rolling_corr, 0, where=rolling_corr >= 0,
                    color="#E07B39", alpha=0.35, interpolate=True)
    ax.fill_between(rolling_corr.index, rolling_corr, 0, where=rolling_corr < 0,
                    color="#2C7FB8", alpha=0.35, interpolate=True)
    ax.plot(rolling_corr.index, rolling_corr, color="#333333", linewidth=1)
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.set_ylim(-1, 1)
    ax.set_title(f"{ticker} vs {crypto}: {ROLLING_WINDOW}-day rolling correlation")
    ax.set_ylabel("Correlation")
    ax.text(0.01, 0.96, "Above 0: they move together", transform=ax.transAxes,
            ha="left", va="top", fontsize=8, color="#B4591F")
    ax.text(0.01, 0.04, "Below 0: they move in opposite directions", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=8, color="#1F5F8B")


def make_crypto_chart(ticker, crypto, period, view):
    """Build the chart for the chosen view, and its summary."""
    prices = load_comparison(ticker, crypto, period)
    returns = prices.pct_change().dropna()
    correlation = returns["Stock"].corr(returns[crypto])
    dd = drawdown(prices)

    fig, ax = plt.subplots(figsize=(8, 3.2))

    if view == "Rolling correlation":
        rolling_corr = returns["Stock"].rolling(ROLLING_WINDOW).corr(returns[crypto]).dropna()
        if rolling_corr.empty:
            raise ValueError(f"Need more than {ROLLING_WINDOW} trading days. Pick a longer period.")
        draw_rolling_correlation(ax, ticker, crypto, rolling_corr)
    else:
        draw_drawdowns(ax, ticker, crypto, dd, correlation)

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


def update_crypto_panel(ticker, period, crypto, view):
    """Called by Gradio when the dashboard is loaded or a control of this panel changes."""
    ticker = (ticker or "").strip().upper()
    try:
        if not ticker:
            raise ValueError("Enter a ticker symbol, such as AAPL.")
        return make_crypto_chart(ticker, crypto, period, view)
    except Exception as error:
        return placeholder(str(error)), f"Unable to compare {ticker or 'ticker'} with {crypto}: {error}"


def build_crypto_panel(ticker_input, period_input, load_button):
    """Add the panel to the dashboard. Call it inside `with demo:`.

    It reuses the dashboard's ticker, period and Load button, and adds two
    controls of its own: the crypto (Bitcoin / Ethereum) and the view.
    """
    with gr.Group():
        gr.Markdown("### Stock vs Crypto")
        with gr.Row():
            crypto_input = gr.Radio(choices=list(CRYPTOS), value="Bitcoin", label="Crypto")
            view_input = gr.Radio(choices=VIEWS, value=VIEWS[0], label="View")
        crypto_plot = gr.Plot(value=placeholder("Enter a ticker and select Load charts"), label="Stock vs crypto")
        crypto_summary = gr.Markdown("Load a ticker to compare it with Bitcoin or Ethereum.")

    inputs = [ticker_input, period_input, crypto_input, view_input]
    outputs = [crypto_plot, crypto_summary]
    load_button.click(fn=update_crypto_panel, inputs=inputs, outputs=outputs)
    crypto_input.change(fn=update_crypto_panel, inputs=inputs, outputs=outputs)
    view_input.change(fn=update_crypto_panel, inputs=inputs, outputs=outputs)

    return crypto_plot
