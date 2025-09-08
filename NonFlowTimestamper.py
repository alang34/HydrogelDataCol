import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("HydrogelDataCol/Actual Data/Nonflow Data/nonflow_run_1.csv")

df.insert(0, 'Timestamp', [i * 2 for i in range(len(df))])

df.to_csv("HydrogelDataCol/Actual Data/Nonflow Data/nonflow_run_1.csv", index=False)

plt.figure(figsize=(8, 6))
plt.plot(df["RH"], df["Temp"], marker='o')
plt.xlabel("RH")
plt.ylabel("Temp")
plt.title(f'RH vs Temp')
plt.grid(True)
plt.show()
