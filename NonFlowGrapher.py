import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("HydrogelDataCol/Actual Data/Nonflow Data/nonflow_run_2.csv")


plt.figure(figsize=(8, 6))
plt.plot(df["AH"], df["Temp"])
plt.xlabel("Absolute Humidity")
plt.ylabel("Temperature (°C)")
plt.title(f'AH vs Temp - Run 2')
plt.grid(True)
plt.show()
