# ====================================================================================================
# IMPORTS
# ====================================================================================================

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import gradio as gr
import matplotlib.dates as mdates
import plotly.graph_objects as go 


metals = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F"
}


metal_colours = {
    "Gold": "#D4A017",
    "Silver": "#8A96A3",
    "Platinum": "#0D9488"
}


# ====================================================================================================
# FIRST TESTING
# ====================================================================================================

# selected_metal = "Platinum"

# # Test downloading stock data

# ticker = "AAPL"
# period = "1mo"

# stock_data = yf.Ticker(ticker).history(period=period)

# print(stock_data.head())

# stock_close = stock_data["Close"]

# stock_returns = stock_close.pct_change() * 100

# print(stock_returns.head())

# gold_data = yf.Ticker(metals[selected_metal]).history(period=period)


# gold_close = gold_data["Close"]


# gold_returns = gold_close.pct_change() * 100

# print(f"\n{selected_metal} daily percentage changes:")
# print(gold_returns.head())

# stock_returns.index = stock_returns.index.tz_localize(None)
# gold_returns.index = gold_returns.index.tz_localize(None)

# stock_returns.index = stock_returns.index.normalize()
# gold_returns.index = gold_returns.index.normalize()

# combined_returns = pd.concat(
#     [
#         stock_returns.rename("Apple"),
#         gold_returns.rename(selected_metal)
#     ],
#     axis=1
# ).dropna()

# print("\nCombined Apple and {selected_metal} returns:")
# print(combined_returns.head())


# # Create the graph
# fig, ax = plt.subplots(figsize=(7, 4))

# ax.scatter(
#     combined_returns.index,
#     combined_returns["Apple"],
#     color="blue",
#     label="Apple",
#     s=25
# )

# ax.scatter(
#     combined_returns.index,
#     combined_returns[selected_metal],
#     color=metal_colours[selected_metal],
#     label=selected_metal,
#     s=25
# )

# 
# ax.axhline(0, color="gray", linestyle="--")

# ax.set_xlabel("Date")
# ax.set_ylabel("Daily Return (%)")
# ax.set_title(f"Apple vs {selected_metal}: Daily Percentage Returns")

# 
# ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))

# ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))

# plt.xticks(rotation=30)

# ax.legend()

# plt.tight_layout()

# plt.savefig("metals_graph.png")

# plt.close()











# ====================================================================================================
# STOCK AND METAL COMPARISON
# ====================================================================================================

def choose_metal(metal, selected_period, selected_dates=None, stock_ticker="AAPL"):

    stock_ticker = stock_ticker.strip().upper()
   
   
    # Error message
    if not stock_ticker:
        raise gr.Error("Please enter a valid stock ticker, such as AAPL or TSLA.")

    stock_data = yf.Ticker(stock_ticker).history(period=selected_period)

    if stock_data.empty or "Close" not in stock_data.columns:
        raise gr.Error(
            f"No data found for '{stock_ticker}'. "
            "Please check the ticker symbol and try again."
        )

    metal_data = yf.Ticker(metals[metal]).history(period=selected_period)

  
    if metal_data.empty or "Close" not in metal_data.columns:
        raise gr.Error(
            f"Unable to retrieve {metal} prices. Please try again later."
        )

    stock_daily_close = stock_data["Close"].copy()
    metal_daily_close = metal_data["Close"].copy()
        
    # Remove timezone info / standardise
    stock_daily_close.index = stock_daily_close.index.tz_localize(None)
    stock_daily_close.index = stock_daily_close.index.normalize()

    metal_daily_close.index = metal_daily_close.index.tz_localize(None)
    metal_daily_close.index = metal_daily_close.index.normalize()


    # Use daily returns for shorter periods and weekly for longer ones
    if selected_period in ["1mo", "3mo", "6mo"]:
        frequency = "Daily"
    else:
        frequency = "Weekly"

    # Adjust the frequency if the user zooms into the graph
    if selected_dates and " to " in selected_dates:
        start_text, end_text = selected_dates.split(" to ")

        start_date = pd.to_datetime(start_text)
        end_date = pd.to_datetime(end_text)

        if end_date <= start_date + pd.DateOffset(months=6):
            frequency = "Daily"
        else:
            frequency = "Weekly"

   
    # Daily / Weekly returns
    stock_daily_returns = stock_daily_close.pct_change() * 100
    metal_daily_returns = metal_daily_close.pct_change() * 100

    # Calculate correlation using aligned daily percentage returns
    daily_comparison = pd.concat(
        [
            stock_daily_returns.rename("Stock"),
            metal_daily_returns.rename("Metal")
        ],
        axis=1
    ).dropna()

    correlation = daily_comparison["Stock"].corr(
        daily_comparison["Metal"]
    )

    if pd.isna(correlation):
        correlation_text = "Correlation unavailable"
    else:
        strength = abs(correlation)

        if strength >= 0.7:
            description = "Strong"
        elif strength >= 0.3:
            description = "Moderate"
        else:
            description = "Weak"

        direction = "positive" if correlation >= 0 else "negative"

        correlation_text = (
            f"Correlation: {correlation:+.2f} "
            f"({description} {direction})"
        )


    stock_weekly_close = stock_daily_close.resample("W-FRI").last()
    metal_weekly_close = metal_daily_close.resample("W-FRI").last()

    stock_weekly_returns = stock_weekly_close.pct_change() * 100
    metal_weekly_returns = metal_weekly_close.pct_change() * 100

    # Select returns to display
    if frequency == "Daily":
        stock_returns = stock_daily_returns
        metal_returns = metal_daily_returns
    else:
        stock_returns = stock_weekly_returns
        metal_returns = metal_weekly_returns


    comparison = pd.concat(
        [
            stock_returns.rename("Stock"),
            metal_returns.rename(metal)
        ],
        axis=1
    ).dropna()

    # Plotly Graph
    fig = go.Figure()

    # Stock returns
    fig.add_trace(go.Scatter(
        x=comparison.index,
        y=comparison["Stock"],
        mode="markers",
        name=stock_ticker,
        marker=dict(color="blue", size=6)
    ))

    # Metal returns
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

    # Labels / layout
    fig.update_layout(
title=dict(
    text=(
        f"{stock_ticker} vs {metal}: {frequency} Percentage Returns"
        f"<br><sup>{correlation_text}</sup>"
    )
),
        xaxis_title="Date",
        yaxis_title=f"{frequency} Return (%)",
        template="plotly_white",
        hovermode="x unified",
        height=450
    )
        # Keep the selected data range after zooming
    if selected_dates and " to " in selected_dates:
        fig.update_xaxes(range=[start_date, end_date])

        
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    return fig














# ====================================================================================================
# GRADIO 
# ====================================================================================================

def build_metals_panel(demo, ticker_input, period_input, load_button):
    with gr.Column():

        gr.Markdown("## Stock vs Precious Metals Comparison")
    
     
        

        metal_dropdown = gr.Dropdown(
            choices=["Gold", "Silver", "Platinum"],
            value="Gold",
            label="Choose a precious metal"
        )


        metals_plot = gr.Plot(
            label="Metals Comparison",
            elem_id="zoom_chart"
        )

        # Recieve the slected date range from JavaScript
        zoom_info = gr.Textbox(
            label="Selected zoom dates",
            value="Waiting for zoom...",
            elem_id="zoom_dates"
        )


        # Updates when user zooms
        zoom_info.change(
            fn=choose_metal,
            inputs=[metal_dropdown, period_input, zoom_info, ticker_input],
            outputs=metals_plot
        )

        metal_dropdown.change(
            fn=choose_metal,
            inputs=[metal_dropdown, period_input, gr.State(None), ticker_input],
            outputs=metals_plot
        )
        load_button.click(
            fn=choose_metal,
            inputs=[metal_dropdown, period_input, gr.State(None), ticker_input],
            outputs=metals_plot
        )

        period_input.change(
            fn=choose_metal,
            inputs=[metal_dropdown, period_input, gr.State(None), ticker_input],
            outputs=metals_plot
        )

        ticker_input.submit(
            fn=choose_metal,
            inputs=[metal_dropdown, period_input, gr.State(None), ticker_input],
            outputs=metals_plot
        )

        # Show graph when dash opens
        demo.load(
            fn=choose_metal,
            inputs=[metal_dropdown, period_input, gr.State(None), ticker_input],
            outputs=metals_plot
        )
        return metals_plot, metal_dropdown
    
    
    
    
    
    
    
    
    
    
    




    
    
    
    # ====================================================================================================
    # AUTOMATIC ZOOM FUNCTIONALITY (JavaScript)
    # ====================================================================================================
    
    
        # Listen for changes to the graph's date range
        demo.load(
            fn=None,
            inputs=None,
            outputs=None,
            js="""
            async () => {

                function attachZoomListener() {
                    const chart = document.querySelector(
                        "#zoom_chart .js-plotly-plot"
                    );

                    if (!chart || typeof chart.on !== "function") {
                        return;
                    }

                    // Prevent duplicate listeners
                    if (chart.dataset.zoomListenerAttached === "true") {
                        return;
                    }

                    chart.dataset.zoomListenerAttached = "true";

                    chart.on("plotly_relayout", (eventData) => {

                        let start = eventData["xaxis.range[0]"];
                        let end = eventData["xaxis.range[1]"];

                        // Reset to the full date range when zooming out
                        if (eventData["xaxis.autorange"] === true) {
                            const fullRange = chart._fullData
                                .flatMap(trace => trace.x || [])
                                .map(date => new Date(date).getTime())
                                .filter(Number.isFinite);

                            if (fullRange.length > 0) {
                                start = new Date(Math.min(...fullRange))
                                    .toISOString();
                                end = new Date(Math.max(...fullRange))
                                    .toISOString();
                            }
                        }

                        if (start && end) {
                            const textbox = document.querySelector(
                                "#zoom_dates textarea, #zoom_dates input"
                            );

                            if (textbox) {
                                const setter = Object.getOwnPropertyDescriptor(
                                    Object.getPrototypeOf(textbox),
                                    "value"
                                )?.set;

                                if (setter) {
                                    const formatDate = (date) =>
                                        new Date(date).toISOString().slice(0, 10);

                                    setter.call(
                                       textbox,
                                        `${formatDate(start)} to ${formatDate(end)}`
                                    );

                                    textbox.dispatchEvent(
                                        new Event("input", { bubbles: true })
                                    );

                                    textbox.dispatchEvent(
                                        new Event("change", { bubbles: true })
                                    );
                                }
                            }
                        }
                    });

                
                }

                setTimeout(attachZoomListener, 2000);

                // keep unchanged
                const observer = new MutationObserver(() => {
                    attachZoomListener();
                });

                const container = document.querySelector("#zoom_chart");

                if (container) {
                    observer.observe(container, {
                        childList: true,
                        subtree: true
                    });
                }
            }
            """
        )


# The metals panel will be launched through Graph_Launcher.ipynb


