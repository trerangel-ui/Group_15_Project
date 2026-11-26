import io

import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

# Price panel with a macro view: the stock's closing price against a macro indicator

INDICATORS = ["10-year Treasury yield", "Inflation (CPI, year on year)", "Unemployment rate", "Fed funds rate"]

def get_close(symbol, period):
    data = yf.Ticker(symbol).history(period=period, auto_adjust=False)
    if data.empty or data["Close"].dropna().empty:
        raise ValueError(f"No closing-price data was returned for {symbol}.")
    close = data["Close"].dropna()
    close.index = close.index.tz_localize(None)  # remove the timezone so the dates match FRED's
    return close


def get_fred(series_id):
    # FRED lets anyone download a data series as a CSV file from this web address
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    table = pd.read_csv(url, index_col=0, parse_dates=True)  # first column is the date
    values = pd.to_numeric(table.iloc[:, 0], errors="coerce")  # missing values become NaN
    return values.dropna()


def get_macro(indicator, period):
    # Returns the indicator's data and the label for its axis
    if indicator == "10-year Treasury yield":
        return get_close("^TNX", period), "Yield (%)"
    elif indicator == "Inflation (CPI, year on year)":
        prices = get_fred("CPIAUCSL")  # monthly consumer price index
        inflation = prices.pct_change(12) * 100  # change since 12 months ago, in %
        return inflation.dropna(), "Inflation (%)"
    elif indicator == "Unemployment rate":
        return get_fred("UNRATE"), "Unemployment (%)"
    else:
        return get_fred("FEDFUNDS"), "Fed funds rate (%)"


def make_price_chart(ticker, period, indicator):
    close = get_close(ticker, period)
    macro, ylabel = get_macro(indicator, period)

    # Economic data is only published monthly, so line it up with the stock's trading days
    # by carrying the latest published value forward
    macro = macro.reindex(close.index, method="ffill").dropna()
    if macro.empty:
        raise ValueError("No data was published for this indicator in the selected period.")

    corr = close.corr(macro)  # how closely the two lines move together

    price_fig, price_ax = plt.subplots(figsize=(8, 3.2))
    price_ax.plot(close.index, close, label="Close", color="#176B87", linewidth=1.8)
    price_ax.set_ylabel("Price")

    macro_ax = price_ax.twinx()
    macro_ax.plot(macro.index, macro, label=indicator, color="#E07A3F", linewidth=1.3)
    macro_ax.set_ylabel(ylabel)

    price_ax.set_title(f"{ticker} closing price vs {indicator}\n"
                       f"Latest reading: {macro.iloc[-1]:.2f}   |   Correlation: {corr:.2f}",
                       fontsize=10)

    lines = price_ax.get_lines() + macro_ax.get_lines()
    price_ax.legend(lines, [line.get_label() for line in lines], frameon=False, loc="upper left")
    price_ax.grid(axis="y", alpha=0.22)
    price_ax.tick_params(axis="x", labelrotation=25)
    price_fig.tight_layout()

    return price_fig


def placeholder_plot(message):
    figure, axis = plt.subplots(figsize=(8, 3.2))
    axis.text(0.5, 0.5, message, ha="center", va="center", color="#666666")
    axis.set_title("Closing price")
    axis.set_axis_off()
    figure.tight_layout()
    return figure


def update_price_panel(ticker, period, indicator):
    ticker = ticker.strip().upper()
    try:
        if not ticker:
            raise ValueError("Enter a ticker symbol, such as AAPL.")
        return make_price_chart(ticker, period, indicator)
    except Exception as error:
        return placeholder_plot(f"Unable to chart {ticker or 'ticker'} against {indicator}:\n{error}")


def build_price_panel(ticker_input, period_input, load_button):
    # Uses the dashboard's ticker, period and Load button, plus one control of its own
    with gr.Group():
        gr.Markdown("### Price")
        indicator_input = gr.Dropdown(choices=INDICATORS, value="10-year Treasury yield",
                                      label="Macro indicator")
        price_plot = gr.Plot(value=placeholder_plot("Enter a ticker and select Load charts"),
                             label="Closing price")

    inputs = [ticker_input, period_input, indicator_input]
    load_button.click(fn=update_price_panel, inputs=inputs, outputs=[price_plot])
    indicator_input.change(fn=update_price_panel, inputs=inputs, outputs=[price_plot])

    return price_plot
