import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("HydrogelDataCol/Actual Data/Nonflow Data/nonflow_run_2.csv")


plt.figure(figsize=(8, 6))
plt.plot(df["Timestamp"], df["RH"])
plt.xlabel("Timestamp (seconds)")
plt.ylabel("Relative Humidity (%)")
plt.title(f'Timestamp vs RH')
plt.grid(True)
plt.show()
