/*
 * Integrated Environmental Data Logger - VERIFIED VERSION
 * - 5x K-type Thermocouples (MAX6675)
 * - 8x SHT31 Temperature/Humidity Sensors
 * - TCA9548A I2C Multiplexer
 * - SD Card Data Logging
 * 
 * HARDWARE CONNECTIONS:
 * MAX6675 (all 5 modules):
 *   - CLK (SCK) -> Arduino Pin 13
 *   - DO (SO)   -> Arduino Pin 12
 *   - CS pins   -> Arduino Pins 2, 3, 4, 5, 6
 * 
 * TCA9548A Multiplexer:
 *   - SDA -> Arduino A4
 *   - SCL -> Arduino A5
 *   - VCC -> 5V
 *   - GND -> GND
 * 
 * SHT31 Sensors (8 total):
 *   - Each connected to one TCA9548A channel (SC0-SC7, SD0-SD7)
 * 
 * SD Card Module:
 *   - CS   -> Arduino Pin 10
 *   - MOSI -> Arduino Pin 11
 *   - MISO -> Arduino Pin 12 (shared with MAX6675)
 *   - SCK  -> Arduino Pin 13 (shared with MAX6675)
 */

#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include "max6675.h"
#include "Adafruit_SHT31.h"

// ==================== PIN DEFINITIONS ====================
const int SD_CS_PIN = 10;        // SD card chip select
const int THERMO_CLK = 13;       // Shared clock (SCK)
const int THERMO_DO = 12;        // Shared data out (MISO/SO)

// Chip select pins for each MAX6675 thermocouple
const int TC_CS_PINS[5] = {2, 3, 4, 5, 6};

// ==================== I2C ADDRESSES ====================
const uint8_t MUX_ADDRESS = 0x70;      // TCA9548A default address
const uint8_t SHT31_ADDRESS = 0x44;    // SHT31 default address

// ==================== SETTINGS ====================
const unsigned long SAMPLE_INTERVAL = 2000;  // Milliseconds between readings
const char* DATA_FILE = "envdata.csv";       // Data file name (8.3 format)

// ==================== SENSOR OBJECTS ====================
// Create 5 MAX6675 objects (one per thermocouple)
// Constructor: MAX6675(sck_pin, cs_pin, so_pin)
MAX6675 thermocouples[5] = {
  MAX6675(THERMO_CLK, TC_CS_PINS[0], THERMO_DO),
  MAX6675(THERMO_CLK, TC_CS_PINS[1], THERMO_DO),
  MAX6675(THERMO_CLK, TC_CS_PINS[2], THERMO_DO),
  MAX6675(THERMO_CLK, TC_CS_PINS[3], THERMO_DO),
  MAX6675(THERMO_CLK, TC_CS_PINS[4], THERMO_DO)
};

// Create single SHT31 object (reused via multiplexer)
Adafruit_SHT31 sht31 = Adafruit_SHT31();

// ==================== GLOBAL VARIABLES ====================
unsigned long lastSampleTime = 0;
unsigned long sampleCount = 0;

// ==================== MULTIPLEXER FUNCTIONS ====================

// Select a specific channel (0-7) on the TCA9548A multiplexer
void selectMuxChannel(uint8_t channel) {
  if (channel > 7) return;  // Invalid channel
  
  Wire.beginTransmission(MUX_ADDRESS);
  Wire.write(1 << channel);  // Activate the selected channel
  Wire.endTransmission();
}

// Disable all multiplexer channels
void disableMuxChannels() {
  Wire.beginTransmission(MUX_ADDRESS);
  Wire.write(0);  // No channels active
  Wire.endTransmission();
}

// ==================== SETUP ====================
void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Wait up to 3 seconds for serial monitor (optional)
  unsigned long startTime = millis();
  while (!Serial && (millis() - startTime < 3000));
  
  Serial.println(F("========================================"));
  Serial.println(F("  Environmental Data Logger v1.0"));
  Serial.println(F("  5 Thermocouples + 8 SHT31 Sensors"));
  Serial.println(F("========================================"));
  Serial.println();
  
  // -------------------- Initialize I2C --------------------
  Wire.begin();
  Serial.println(F("I2C bus initialized."));
  
  // -------------------- Initialize SD Card --------------------
  Serial.print(F("Initializing SD card... "));
  
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println(F("FAILED!"));
    Serial.println(F("*** SD CARD ERROR ***"));
    Serial.println(F("Please check:"));
    Serial.println(F("  - SD card is inserted"));
    Serial.println(F("  - Wiring connections"));
    Serial.println(F("  - SD card is formatted (FAT16/FAT32)"));
    Serial.println(F("System halted."));
    while (1) {
      delay(1000);  // Halt forever
    }
  }
  Serial.println(F("OK"));
  
  // -------------------- Test I2C Multiplexer --------------------
  Serial.print(F("Testing TCA9548A multiplexer... "));
  Wire.beginTransmission(MUX_ADDRESS);
  byte error = Wire.endTransmission();
  
  if (error == 0) {
    Serial.println(F("OK"));
  } else {
    Serial.println(F("FAILED!"));
    Serial.println(F("*** MULTIPLEXER ERROR ***"));
    Serial.println(F("Check TCA9548A wiring (SDA->A4, SCL->A5)."));
    Serial.println(F("System halted."));
    while (1) {
      delay(1000);
    }
  }
  
  // -------------------- Initialize SHT31 Sensors --------------------
  Serial.println(F("Initializing SHT31 sensors..."));
  bool allSensorsOK = true;
  
  for (int i = 0; i < 8; i++) {
    selectMuxChannel(i);
    delay(50);  // Allow channel to stabilize
    
    if (sht31.begin(SHT31_ADDRESS)) {
      Serial.print(F("  Channel "));
      Serial.print(i);
      Serial.println(F(": OK"));
    } else {
      Serial.print(F("  Channel "));
      Serial.print(i);
      Serial.println(F(": FAILED"));
      allSensorsOK = false;
    }
  }
  disableMuxChannels();
  
  if (!allSensorsOK) {
    Serial.println(F("WARNING: Some SHT31 sensors failed."));
    Serial.println(F("Continuing anyway (failed sensors will log -999)."));
  }
  Serial.println();
  
  // -------------------- Create/Open CSV File --------------------
  Serial.print(F("Opening data file... "));
  File dataFile = SD.open(DATA_FILE, FILE_WRITE);
  
  if (!dataFile) {
    Serial.println(F("FAILED!"));
    Serial.println(F("*** FILE ERROR ***"));
    Serial.println(F("Cannot create/open data file."));
    Serial.println(F("System halted."));
    while (1) {
      delay(1000);
    }
  }
  
  // Write header if file is new
  if (dataFile.size() == 0) {
    Serial.println(F("Creating new file."));
    Serial.print(F("Writing CSV header... "));
    
    // Write header row
    dataFile.print(F("Sample,Time_ms"));
    
    // Thermocouple columns
    for (int i = 1; i <= 5; i++) {
      dataFile.print(F(",TC"));
      dataFile.print(i);
      dataFile.print(F("_C"));
    }
    
    // SHT31 columns (temp and humidity for each)
    for (int i = 1; i <= 8; i++) {
      dataFile.print(F(",SHT"));
      dataFile.print(i);
      dataFile.print(F("_Temp_C,SHT"));
      dataFile.print(i);
      dataFile.print(F("_RH_pct"));
    }
    dataFile.println();
    
    Serial.println(F("OK"));
  } else {
    Serial.println(F("Appending to existing file."));
  }
  
  dataFile.close();
  Serial.println();
  
  // -------------------- Sensor Warm-up --------------------
  Serial.println(F("Warming up sensors (1 second)..."));
  delay(1000);
  
  // -------------------- Ready to Log --------------------
  Serial.println(F("========================================"));
  Serial.println(F("  SYSTEM READY - LOGGING STARTED"));
  Serial.println(F("========================================"));
  Serial.print(F("Data file: "));
  Serial.println(DATA_FILE);
  Serial.print(F("Sample interval: "));
  Serial.print(SAMPLE_INTERVAL);
  Serial.println(F(" ms"));
  Serial.println();
  Serial.println(F("Sample | Time(s) | Sensors..."));
  Serial.println(F("-------|---------|------------"));
}

// ==================== MAIN LOOP ====================
void loop() {
  unsigned long currentTime = millis();
  
  // Check if it's time for the next sample
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime = currentTime;
    sampleCount++;
    
    // Print sample info
    Serial.print(sampleCount);
    Serial.print(F(" | "));
    Serial.print(currentTime / 1000.0, 1);
    Serial.print(F("s | "));
    
    // -------------------- Read Thermocouples --------------------
    float tcTemps[5];
    bool tcErrors = false;
    
    for (int i = 0; i < 5; i++) {
      tcTemps[i] = thermocouples[i].readCelsius();
      
      // Validate reading (MAX6675 range: 0-1024°C)
      if (isnan(tcTemps[i]) || tcTemps[i] < -50 || tcTemps[i] > 1100) {
        tcTemps[i] = -999.0;  // Error flag
        tcErrors = true;
      }
      
      delay(10);  // Small delay between readings
    }
    
    // -------------------- Read SHT31 Sensors --------------------
    float shtTemps[8];
    float shtHumidity[8];
    bool shtErrors = false;
    
    for (int i = 0; i < 8; i++) {
      selectMuxChannel(i);
      delay(20);  // Channel stabilization time
      
      float t = sht31.readTemperature();
      float h = sht31.readHumidity();
      
      // Validate readings
      if (!isnan(t) && !isnan(h) && t > -40 && t < 125 && h >= 0 && h <= 100) {
        shtTemps[i] = t;
        shtHumidity[i] = h;
      } else {
        shtTemps[i] = -999.0;
        shtHumidity[i] = -999.0;
        shtErrors = true;
      }
    }
    disableMuxChannels();
    
    // -------------------- Build CSV Data String --------------------
    String dataString = "";
    dataString += String(sampleCount);
    dataString += ",";
    dataString += String(currentTime);
    
    // Add thermocouple data
    for (int i = 0; i < 5; i++) {
      dataString += ",";
      dataString += String(tcTemps[i], 2);
    }
    
    // Add SHT31 data
    for (int i = 0; i < 8; i++) {
      dataString += ",";
      dataString += String(shtTemps[i], 2);
      dataString += ",";
      dataString += String(shtHumidity[i], 1);
    }
    
    // -------------------- Write to SD Card --------------------
    File dataFile = SD.open(DATA_FILE, FILE_WRITE);
    if (dataFile) {
      dataFile.println(dataString);
      dataFile.close();
      Serial.print(F("OK"));
    } else {
      Serial.print(F("SD_ERROR"));
    }
    
    // Print error flags
    if (tcErrors) Serial.print(F(" TC_ERR"));
    if (shtErrors) Serial.print(F(" SHT_ERR"));
    
    Serial.println();
  }
}