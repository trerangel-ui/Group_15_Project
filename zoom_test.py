

import gradio as gr
import plotly.graph_objects as go
import pandas as pd

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
        value="Waiting for zoom..."
    )


    
    demo.load(
        fn=None,
        inputs=None,
        outputs=None,
        js="""
        async () => {
            // Wait for Gradio to finish rendering
            await new Promise(resolve => setTimeout(resolve, 2000));

            const chart = document.querySelector(
                "#zoom_chart .js-plotly-plot"
            );

            if (chart) {
                console.log("SUCCESS: Plotly graph found!");

                // Listen for zoom events
                chart.on("plotly_relayout", (eventData) => {
                    console.log("ZOOM DETECTED:", eventData);
                });

                console.log("Zoom listener attached!");
            } else {
                console.log("ERROR: Plotly graph not found.");
            }
        }
        """
    )


demo.launch()
