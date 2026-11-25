import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

# Stock vs crypto panel: does crypto protect a stock investor when the stock falls?
# Two views: how far each one falls from its peak, and the correlation of their daily returns.

CRYPTOS = {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD"}


def get_close(symbol, period):
    data = yf.Ticker(symbol).history(period=period, auto_adjust=False)
    if data.empty or data["Close"].dropna().empty:
        raise ValueError(f"No closing-price data was returned for {symbol}.")
    return data["Close"].dropna()


def make_crypto_chart(ticker, crypto, period, view):
    stock_close = get_close(ticker, period)
    crypto_close = get_close(CRYPTOS[crypto], period)

    # Crypto trades every day but stocks don't, so line the crypto up on the stock's trading days
    crypto_close = crypto_close.reindex(stock_close.index, method="ffill")
    df = pd.DataFrame({"Stock": stock_close, crypto: crypto_close}).dropna()
    if len(df) < 15:
        raise ValueError("Not enough trading days to compare. Try a longer period.")

    returns = df.pct_change().dropna()
    drawdown = (df / df.cummax() - 1) * 100  # fall from the highest price so far, in %

    crypto_fig, crypto_ax = plt.subplots(figsize=(8, 3.2))

    if view == "Correlation":
        window = min(60, max(10, len(returns) // 3))  # 60 days, shorter for short periods
        corr = returns["Stock"].rolling(window).corr(returns[crypto]).dropna()
        overall = returns["Stock"].corr(returns[crypto])  # one number for the whole period

        # Orange = they move together, blue = they move in opposite directions
        corr_colors = ["#E07B39" if value >= 0 else "#2C7FB8" for value in corr]
        crypto_ax.bar(corr.index, corr, color=corr_colors, width=1.5)
        crypto_ax.axhline(0, color="#555555", linewidth=0.8)
        crypto_ax.axhline(overall, color="#333333", linestyle="--", linewidth=1,
                          label=f"Whole period: {overall:.2f}")
        crypto_ax.set_title(f"{ticker} vs {crypto}: {window}-day rolling correlation")
        crypto_ax.set_ylabel("Correlation\n(orange = together)")
    else:
        crypto_color = "#F2A900" if crypto == "Bitcoin" else "#7A6FD0"
        crypto_ax.fill_between(drawdown.index, drawdown[crypto], 0, color=crypto_color, alpha=0.3, label=crypto)
        crypto_ax.plot(drawdown.index, drawdown["Stock"], color="#176B87", linewidth=1.6, label=ticker)
        crypto_ax.set_title(f"{ticker} vs {crypto}: fall from peak")
        crypto_ax.set_ylabel("Drawdown from peak (%)")

        # Label the stock's worst day and where the crypto was that day
        worst_day = drawdown["Stock"].idxmin()
        on_right = worst_day > drawdown.index[int(len(drawdown) * 0.7)]
        # Put the label under the point, unless the stock is the lowest line on the chart
        below = drawdown["Stock"].min() > drawdown[crypto].min()
        crypto_ax.annotate(
            f"{ticker} worst: {drawdown['Stock'].min():.1f}%\n"
            f"{crypto} that day: {drawdown.loc[worst_day, crypto]:.1f}%",
            xy=(worst_day, drawdown["Stock"].min()),
            xytext=(-15 if on_right else 15, -12 if below else 12),
            textcoords="offset points",
            ha="right" if on_right else "left",
            va="top" if below else "bottom",
            fontsize=8,
            bbox={"boxstyle": "round", "facecolor": "white", "edgecolor": "none", "alpha": 0.85},
            arrowprops={"arrowstyle": "->", "color": "#555555"},
        )

    crypto_ax.legend(frameon=False, loc="lower left")
    crypto_ax.grid(axis="y", alpha=0.22)
    crypto_ax.tick_params(axis="x", labelrotation=25)
    crypto_fig.tight_layout()

    return crypto_fig


def placeholder_plot(message):
    figure, axis = plt.subplots(figsize=(8, 3.2))
    axis.text(0.5, 0.5, message, ha="center", va="center", color="#666666")
    axis.set_title("Stock vs crypto")
    axis.set_axis_off()
    figure.tight_layout()
    return figure


def update_crypto_panel(ticker, period, crypto, view):
    ticker = ticker.strip().upper()
    try:
        if not ticker:
            raise ValueError("Enter a ticker symbol, such as AAPL.")
        return make_crypto_chart(ticker, crypto, period, view)
    except Exception as error:
        return placeholder_plot(f"Unable to compare {ticker or 'ticker'} with {crypto}:\n{error}")


def build_crypto_panel(ticker_input, period_input, load_button):
    # Uses the dashboard's ticker, period and Load button, plus two controls of its own
    with gr.Group():
        gr.Markdown("### Stock vs crypto")
        with gr.Row():
            crypto_input = gr.Radio(choices=["Bitcoin", "Ethereum"], value="Bitcoin", label="Crypto")
            view_input = gr.Radio(choices=["Falls from peak", "Correlation"],
                                  value="Falls from peak", label="View")
        crypto_plot = gr.Plot(value=placeholder_plot("Enter a ticker and select Load charts"),
                              label="Stock vs crypto")

    inputs = [ticker_input, period_input, crypto_input, view_input]
    load_button.click(fn=update_crypto_panel, inputs=inputs, outputs=[crypto_plot])
    crypto_input.change(fn=update_crypto_panel, inputs=inputs, outputs=[crypto_plot])
    view_input.change(fn=update_crypto_panel, inputs=inputs, outputs=[crypto_plot])

    return crypto_plot, crypto_input
