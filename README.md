# Group 15 – Financial Market Dashboard

**Project team:** Tre, Kai, Sem, Achille and Elsbeth

## About the Project

The goal of our project is to create an interactive financial market dashboard that makes financial information easier to understand, explore and compare.

Investing is about more than simply looking at whether a stock price goes up or down. To understand the bigger picture, it is useful to compare different types of investments and explore how financial markets develop over time.

Our dashboard combines stock market data, Treasury bond yields, precious metals, cryptocurrencies and real estate investments in one interactive environment.

Users can select a stock ticker, choose a historical time period and explore four different visualizations. These visualizations help users identify trends, observe market fluctuations and understand relationships between different investment categories.

## Dashboard Features

The dashboard contains four main visualizations, displayed in the following order:

### 1. Price – Stock Price vs Macro Indicators

This graph compares the historical closing price of the selected stock with a selected macroeconomic indicator.

Users can:
- Select a stock ticker.
- Choose a historical period.
- Select one of four macroeconomic indicators:
  - **10-year Treasury yield:** tracks changes in the US 10-year Treasury yield.
  - **Inflation (CPI, year on year):** shows the annual percentage change in the Consumer Price Index.
  - **Unemployment rate:** tracks the US unemployment rate.
  - **Fed funds rate:** shows the Federal Reserve's federal funds rate.
- Compare stock price movements with changes in the selected macroeconomic indicator.

The graph uses two vertical axes: the stock closing price is displayed on the left axis, while the selected macroeconomic indicator is displayed on the right axis.

It also displays the latest available reading of the selected indicator and the correlation between the stock price and the indicator.

This visualization helps users explore how stock prices relate to broader economic conditions and how these relationships may differ depending on the selected indicator.

### 2. Stock vs Precious Metals Comparison

This graph compares the daily percentage returns of the selected stock with a selected precious metal.

Users can:
- Choose between Gold, Silver and Platinum.
- Explore the daily percentage returns of both assets.
- View the correlation between the selected stock and precious metal.
- Zoom in on specific dates to investigate particular periods.

The scatterplot helps users understand whether the stock and precious metal tend to move in similar or different directions.

### 3. Investment Performance Comparison

This graph compares the historical performance of several investment categories over the selected time period.

The comparison includes:
- The selected stock.
- Bitcoin or Ethereum.
- Treasury Bonds (IEF).
- Gold, Silver or Platinum.
- Real Estate through the Vanguard Real Estate ETF (VNQ).

The selected cryptocurrency and precious metal are automatically taken from their respective selections in the dashboard. The comparison graph updates accordingly, without requiring users to make the same selections again.

This visualization makes it easier to compare the performance and development of different investments over time.

### 4. Stock vs Crypto

This graph compares the selected stock with a chosen cryptocurrency.

Users can:
- Switch between Bitcoin and Ethereum.
- Choose between two visualization modes:
  - **Falls from peak:** compares how far the stock and cryptocurrency have fallen from their previous peaks.
  - **Correlation:** explores the relationship between the stock and cryptocurrency.

This allows users to investigate how cryptocurrency movements compare with stock market movements and how their performance differs during periods of market decline.

## Why Is This Dashboard Useful?

The main value of our dashboard is that it brings different types of financial information together in one interactive environment.

Users can explore questions such as:
- How does a selected stock perform compared to different macroeconomic indicators?
- Does a selected stock move in a similar direction to Gold, Silver or Platinum?
- How does a stock compare with Bitcoin or Ethereum?
- How do stocks, bonds, precious metals and real estate perform over the same period?
- How do different investments behave during periods of market decline?

Our dashboard does not provide financial advice or tell users what to invest in. Instead, it provides information and visual insights that can support a better understanding of financial markets.

## Data Sources and Technologies

The project uses financial market data retrieved through Yahoo Finance and macroeconomic data retrieved from the Federal Reserve Economic Data (FRED) database.

The main technologies used in this project include:

- **Python** – Main programming language.
- **Pandas** – Data handling and analysis.
- **yfinance** – Retrieving financial market data.
- **FRED** – Retrieving macroeconomic data, including inflation, unemployment and the federal funds rate.
- **Matplotlib** – Data visualization.
- **Plotly** – Interactive visualizations.
- **Gradio** – Building the interactive dashboard.
- **Jupyter Notebook** – Running and testing the project.

## How to Run the Project

1. Install Python.
2. Install Visual Studio Code and the Jupyter Notebook extension.
3. Clone or download the project repository.
4. Open the project folder in Visual Studio Code.
5. Install the required Python packages if they are not already installed.
6. Select the correct Python environment or kernel.
7. Open `Graph_Launcher_Integrated.ipynb`.
8. Run the notebook cells in order to launch the interactive Gradio dashboard.
