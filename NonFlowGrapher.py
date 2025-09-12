import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("HydrogelDataCol/Actual Data/Nonflow Data/nonflow_run_3.csv")


plt.figure(figsize=(8, 6))
plt.plot(df["RH"], df["Temp"])
plt.xlabel("Timestamp")
plt.ylabel("Relative Humidity (%)")
plt.title(f'RH vs Timestamp - Run 3')
plt.grid(True)
plt.show()
