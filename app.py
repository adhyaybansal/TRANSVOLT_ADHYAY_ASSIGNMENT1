from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os

app = Flask(__name__)


os.makedirs("static", exist_ok=True)

def generate_charts_and_tables():
    df = pd.read_csv("Sample_Data.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    plt.figure(figsize=(12, 6))
    plt.plot(df['Timestamp'], df['Values'], label="Voltage", color='blue')
    plt.xlabel("Timestamp")
    plt.ylabel("Voltage")
    plt.title("Voltage vs Timestamp")
    plt.legend()
    plt.savefig("static/python_chart.png", dpi=300, bbox_inches='tight')
    plt.close()

    df['1000_MA'] = df['Values'].rolling(window=1000).mean()
    df['5000_MA'] = df['Values'].rolling(window=5000).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(df['Timestamp'], df['Values'], label='Original Values', color='blue', linewidth=0.8)
    plt.plot(df['Timestamp'], df['1000_MA'], label='1000 Value MA', color='red', linewidth=1.5)
    plt.plot(df['Timestamp'], df['5000_MA'], label='5000 Value MA', color='green', linewidth=1.5)
    plt.title('Values with 1000 and 5000 Value Moving Averages', fontsize=14)
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Values', fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.savefig("static/moving_average_chart_matplotlib.png", dpi=300, bbox_inches='tight')
    plt.close()

    df['Moving_Avg_5'] = df['Values'].rolling(window=5).mean()
    plt.figure(figsize=(12, 6))
    plt.plot(df['Timestamp'], df['Values'], label="Voltage", alpha=0.7)
    plt.plot(df['Timestamp'], df['Moving_Avg_5'], label="5-Day Moving Avg", color="orange")
    plt.xlabel("Timestamp")
    plt.ylabel("Voltage")
    plt.title("Voltage with 5-Day Moving Average")
    plt.legend()
    plt.savefig("static/moving_avg.png", dpi=300, bbox_inches='tight')
    plt.close()

    peaks, _ = find_peaks(df['Values'])
    lows, _ = find_peaks(-df['Values'])
    peaks_df = df.iloc[peaks]
    lows_df = df.iloc[lows]

    low_voltage_df = df[df['Values'] < 20]

    df['Slope'] = df['Values'].diff()
    downward_accel_df = df[(df['Slope'] < 0) & (df['Slope'].diff() < 0)][['Timestamp', 'Values', 'Slope']]

    return {
        "peaks": peaks_df.to_html(classes="table table-striped", index=False),
        "lows": lows_df.to_html(classes="table table-striped", index=False),
        "low_voltage": low_voltage_df.to_html(classes="table table-striped", index=False),
        "downward_accel": downward_accel_df.to_html(classes="table table-striped", index=False)
    }

tables = generate_charts_and_tables()

@app.route("/")
def index():
    interpretations = [
        "The voltage values fluctuate in a repeating cyclical pattern over the recorded period, with frequent sharp drops followed by quick recoveries.",
        "The linear trendline has a very small positive slope, suggesting almost no overall increase in voltage over time.",
        "The R² value of 0.0009 indicates that the linear trendline does not closely fit the actual data, as the variations are mostly short-term cycles rather than long-term trends.",
        "Voltage levels peak around 100 units and drop to as low as about 25–30 units during each cycle.",
        "This pattern likely reflects a periodic charging and discharging process or a system operating in regular on-off cycles."
    ]
    return render_template("index.html", interpretations=interpretations, tables=tables)

if __name__ == "__main__":
    app.run(debug=True)