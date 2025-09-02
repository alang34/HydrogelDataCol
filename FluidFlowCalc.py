import matplotlib as plt
import numpy as np
import scipy as sp
import pandas as pd

# System Constants
# in square meters, m/s, and designated
tubeCrossSection = 0.0000712423
snakeCrossSection = 0.00064516
snakeLength = 2.87
snakeHydraulicDiameter = 0.0254 
gasConstant = 287 # J/(kg*K)
airViscosity = 1.846e-5 # Pa*s
gelTemp = 300

#input conditions
#Singular input

inletTemp = 300
inletPressure = 101325 # Pa
inletDensity = inletPressure / (gasConstant * inletTemp) # kg/m^3
volumetricFlowRateSCFH = 180 # scfh

volumetricFlowRate = volumetricFlowRateSCFH * 0.0000078658
snakeVelocity = volumetricFlowRate / snakeCrossSection
snakeReynolds = (inletDensity*snakeVelocity*snakeHydraulicDiameter) / airViscosity
timeInSnake = snakeLength / snakeVelocity

print(snakeVelocity)
print(snakeReynolds)
# df = pd.read_csv('data1.csv')
# a = df.to_numpy()
# timestampl = a[0:, 0]
# inTemp = a[0:, 1]
# inAbsHum = a[0:, 2]
# inRelHum = a[0:, 3]
# outTemp = a[0:, 4]
# outAbsHum = a[0:, 5]
# outRelHum = a[0:, 6]

