

import gradio as gr
import plotly.graph_objects as go
import pandas as pd

# Func python recieves zoom event and dates(print dates in terminakl)

def receive_zoom_dates(selected_dates):
    start_text, end_text = selected_dates.split(" to ")

    start_date = pd.to_datetime(start_text)
    end_date = pd.to_datetime(end_text)

    if end_date <= start_date + pd.DateOffset(months=6):
        frequency = "DAILY"
    else:
        frequency = "WEEKLY"

    print("FREQUENCY SELECTED:", frequency)

    # Create test data for the selected date range
    selected_data = pd.DataFrame(
    {"value": values},
    index=dates
    )

    if frequency == "WEEKLY":
        selected_data = selected_data.resample("W-FRI").last().dropna()

    # Build a new graph
    new_fig = go.Figure()

    new_fig.add_trace(go.Scatter(
        x=selected_data.index,
        y=selected_data["value"],
        mode="markers",
        name=frequency
    ))

    new_fig.update_layout(
        title=f"Zoom Test — {frequency} Data",
        xaxis_title="Date",
        yaxis_title="Test Value",
        xaxis_range=[start_date, end_date]
    )

    return new_fig


dates = pd.date_range("2023-01-01", periods=365, freq="D")
values = list(range(365))

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates,
    y=values,
    mode="markers",
    name="Test Data"
))

fig.update_layout(
    title="Zoom into any date range",
    xaxis_title="Date",
    yaxis_title="Test Value"
)

with gr.Blocks() as demo:
    gr.Markdown("## Detecting Plotly Zoom Events")

    plot = gr.Plot(value=fig, elem_id="zoom_chart")

    zoom_info = gr.Textbox(
        label="Selected date range",
        value="Waiting for zoom...",
        elem_id="zoom_dates"
    )
    zoom_info.change(
        fn=receive_zoom_dates,
        inputs=zoom_info,
        outputs=plot
    )

    
        

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

                // No chart available yet
                if (!chart || typeof chart.on !== "function") {
                    return;
                }

                // Avoid attaching multiple listeners to the same chart
                if (chart.dataset.zoomListenerAttached === "true") {
                    return;
                }

                chart.dataset.zoomListenerAttached = "true";

                chart.on("plotly_relayout", (eventData) => {

                    console.log("ZOOM DETECTED:", eventData);

                    let start = eventData["xaxis.range[0]"];
                    let end = eventData["xaxis.range[1]"];

                    // Handle Autoscale or Reset Axes
                 
                    if (eventData["xaxis.autorange"] === true) {
                        start = "2023-01-01";
                        end = "2023-12-31";

                        console.log("AUTOSCALE DETECTED!");
                    }


                    if (start && end) {

                        const textbox = document.querySelector(
                            "#zoom_dates textarea, #zoom_dates input"
                        );

                        if (textbox) {

                            const setter =
                                Object.getOwnPropertyDescriptor(
                                    Object.getPrototypeOf(textbox),
                                    "value"
                                )?.set;

                            if (setter) {

                                setter.call(
                                    textbox,
                                    `${start} to ${end}`
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

                console.log("Zoom listener attached to current graph!");
            }

            // Attach when the page first loads
            setTimeout(attachZoomListener, 2000);

            // Watch for Gradio replacing the Plotly graph
            const observer = new MutationObserver(() => {
                attachZoomListener();
            });

            observer.observe(
                document.querySelector("#zoom_chart"),
                {
                    childList: true,
                    subtree: true
                }
            );
        }
        """
    )





demo.launch()
