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
def choose_metal(metal, selected_period, selected_dates=None):

    # Download Apple's prices
    stock_data = yf.Ticker("AAPL").history(period=selected_period)

    # Download the selected precious metal's prices
    metal_data = yf.Ticker(metals[metal]).history(period=selected_period)

    # Keep daily closing prices for both investments
    stock_daily_close = stock_data["Close"].copy()
    metal_daily_close = metal_data["Close"].copy()
        
        # Standardise the dates before calculating returns
    stock_daily_close.index = stock_daily_close.index.tz_localize(None)
    stock_daily_close.index = stock_daily_close.index.normalize()

    metal_daily_close.index = metal_daily_close.index.tz_localize(None)
    metal_daily_close.index = metal_daily_close.index.normalize()



    # Initially choose frequency based on the period dropdown
    if selected_period in ["1mo", "3mo", "6mo"]:
        frequency = "Daily"
    else:
        frequency = "Weekly"

    # Override frequency when the user zooms into a date range
    if selected_dates and " to " in selected_dates:
        start_text, end_text = selected_dates.split(" to ")

        start_date = pd.to_datetime(start_text)
        end_date = pd.to_datetime(end_text)

        if end_date <= start_date + pd.DateOffset(months=6):
            frequency = "Daily"
        else:
            frequency = "Weekly"

    print("METALS FREQUENCY:", frequency)

   
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
        # Preserve the selected historical range after updating
    if selected_dates and " to " in selected_dates:
        fig.update_xaxes(range=[start_date, end_date])

        
    # Add a horizontal reference line at 0%
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    return fig


def receive_zoom_dates(selected_dates):
    print("METALS ZOOM RECEIVED:", selected_dates)

with gr.Blocks() as demo:

    gr.Markdown("## Apple vs Precious Metals Comparison")

    # Dropdown to select a precious metal
    metal_dropdown = gr.Dropdown(
        choices=["Gold", "Silver", "Platinum"],
        value="Gold",
        label="Choose a precious metal"
    )

    # Dropdown to select the time period
    period_dropdown = gr.Dropdown(
        choices=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        value="1mo",
        label="Choose a time period"
    )

    # Interactive Plotly graph
    metals_plot = gr.Plot(
        label="Metals Comparison",
        elem_id="zoom_chart"
    )

    # Textbox to receive zoom dates from JavaScript
    zoom_info = gr.Textbox(
        label="Selected zoom dates",
        value="Waiting for zoom...",
        elem_id="zoom_dates"
    )
    # connection for zooming 
    zoom_info.change(
        fn=choose_metal,
        inputs=[metal_dropdown, period_dropdown, zoom_info],
        outputs=metals_plot
    )
   

    # Update graph when the selected metal changes
    metal_dropdown.change(
        fn=choose_metal,
        inputs=[metal_dropdown, period_dropdown],
        outputs=metals_plot
    )

    # Update graph when the selected period changes
    period_dropdown.change(
        fn=choose_metal,
        inputs=[metal_dropdown, period_dropdown],
        outputs=metals_plot
    )

    # Display the initial graph when the app loads
    demo.load(
        fn=choose_metal,
        inputs=[metal_dropdown, period_dropdown],
        outputs=metals_plot
    )
    
    # Detect Plotly zoom events using JavaScript
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
                    console.log("ZOOM DETECTED:", eventData);

                    let start = eventData["xaxis.range[0]"];
                    let end = eventData["xaxis.range[1]"];

                    // Handle zooming back out
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
                                setter.call(textbox, `${start} to ${end}`);

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

                console.log("Zoom listener attached!");
            }

            // Attach after initial rendering
            setTimeout(attachZoomListener, 2000);

            // Reattach if Gradio replaces the graph
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


demo.launch()


