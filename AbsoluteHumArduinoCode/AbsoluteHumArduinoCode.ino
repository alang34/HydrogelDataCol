#include <Wire.h>
#include "Adafruit_SHT31.h"

Adafruit_SHT31 sht31 = Adafruit_SHT31();

void setup() {
  Serial.begin(9600);
  
  if (!sht31.begin(0x44)) { //I2C address for SHT30
    Serial.println("Couldnt find SHT30 Sensor!");
    while (1) delay(1);
  }
}

void loop() {
  delay(2000); //unsure about a good delay, maybe a much longer delay since it shouldnt fluxuate much

  float temp = sht31.readTemperature(); // Get Temp (degC)
  float hum = sht31.readHumidity(); //rel humidity (%)

  if (isnan(hum) || isnan(temp)) { 
    Serial.println ("Failed to read sensor!");
    return; 
  }

  //compute SVP 
  float SVP = 6.112 * exp((17.67 * temp) / (temp + 243.5));

  //Compute vapor pressure (VP)
  float VP = (hum / 100.0) * SVP;

  //absolute humidity
  float AH = (VP * 100 * 18.016) / (8.314 * (temp + 273.15));

  // //Data to check if monitor works correctly
  // Serial.print("Temperature: "); Serial.print(temp); Serial.println(" °C");
  // Serial.print("Humidity: "); Serial.print(hum); Serial.println(" %");
  // Serial.print("SVP: "); Serial.print(SVP); Serial.println(" hPa");
  // Serial.print("VP: "); Serial.print(VP); Serial.println(" hPa");



  //prints absolute humidity & temp that will be going into csv
  Serial.print(temp);
}
