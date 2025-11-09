import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

csv_files = ["Actual Data/Nonflow Data/nonflow_run_2.csv",
             "Actual Data/Nonflow Data/nonflow_run_3.csv",
             "Actual Data/Nonflow Data/nonflow_run_4.csv",
             "Actual Data/Nonflow Data/nonflow_run_5.csv"]

def plot(csv, x, y, log):
    df = pd.read_csv(csv)
    plt.figure(figsize=(8,6), label = f'Run {csv[-5]}')
    plt.plot(df[x], df[y])
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f'{x} vs {y} for Run 3')
    plt.grid(True)
    plt.legend()
    if log:
        plt.xscale('log')
    plt.show()

def plot_all(csv_files, x, y, log):
    plt.figure(figsize=(8,6))
    for csv in csv_files:
        df = pd.read_csv(csv)
        plt.plot(df[x], df[y], label = f'Run {csv[-5]}')
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f'{x} vs {y} For all runs')
    plt.grid(True)
    plt.legend()
    if log:
        plt.xscale('log')
    plt.show()
plot(csv_files[1], "Timestamp", "RH", False)
# plot_all(csv_files, "Timestamp", "Temp", True)