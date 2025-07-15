import serial
import pandas as pd
from datetime import datetime
import os
import threading
import time

# Global variables
recording = True
stop_flag = False

def get_keypress():
    """Windows function to detect key press"""
    import msvcrt
    while not stop_flag:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'q':
                return 'q'
    return None

def keyboard_listener():
    """Listens for keyboard input in a separate thread"""
    global recording, stop_flag
    key = get_keypress()
    if key == 'q':
        recording = False
        stop_flag = True
        print("\nStopping data recording...")

def create_filename(base_name, flow_rate, deseccant_amount):
    """Creates filename with flow rate and deseccant amount parameters"""
    filename = f"{base_name}_FR{flow_rate}_D{deseccant_amount}.csv"
    return filename

def setup_serial_connections():
    """Setup serial connections for both Arduino boards"""
    print("Setting up serial connections...")
    print("Available COM ports - check Device Manager if unsure")
    
    inflow_port = input("Enter COM port for INFLOW Arduino (e.g., COM3): ").strip()
    outflow_port = input("Enter COM port for OUTFLOW Arduino (e.g., COM4): ").strip()
    
    try:
        ser_inflow = serial.Serial(inflow_port, 9600, timeout=1)
        ser_outflow = serial.Serial(outflow_port, 9600, timeout=1)
        print(f"Connected to {inflow_port} (Inflow) and {outflow_port} (Outflow)")
        time.sleep(2)  # Give Arduino time to initialize
        return ser_inflow, ser_outflow
    except Exception as e:
        print(f"Error connecting to serial ports: {e}")
        return None, None

def read_arduino_data(ser, sensor_name):
    """Reads humidity data from Arduino (expects AH and temp on separate lines)"""
    try:
        # Read absolute humidity (first line)
        ah_line = ser.readline().decode().strip()
        if not ah_line:
            return None, None, None
        
        # Read temperature (second line)
        temp_line = ser.readline().decode().strip()
        if not temp_line:
            return None, None, None
        
        absolute_humidity = float(ah_line)
        temperature = float(temp_line)
        
        # Calculate relative humidity from absolute humidity and temperature
        # Using inverse of the Arduino calculation
        # AH = (VP * 100 * 18.016) / (8.314 * (temp + 273.15))
        # VP = (AH * 8.314 * (temp + 273.15)) / (100 * 18.016)
        VP = (absolute_humidity * 8.314 * (temperature + 273.15)) / (100 * 18.016)
        
        # SVP = 6.112 * exp((17.67 * temp) / (temp + 243.5))
        import math
        SVP = 6.112 * math.exp((17.67 * temperature) / (temperature + 243.5))
        
        # RH = (VP / SVP) * 100
        relative_humidity = (VP / SVP) * 100
        
        return temperature, absolute_humidity, relative_humidity
        
    except Exception as e:
        print(f"Error reading {sensor_name} data:", e)
        return None, None, None

def save_to_csv(inflow_data, outflow_data, filename):
    """Saves the humidity data to a CSV file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Unpack data tuples
    inflow_temp, inflow_ah, inflow_rh = inflow_data
    outflow_temp, outflow_ah, outflow_rh = outflow_data
    
    # Create a DataFrame with all columns
    data = pd.DataFrame([[timestamp, inflow_temp, inflow_ah, inflow_rh, 
                         outflow_temp, outflow_ah, outflow_rh]], 
                        columns=["Timestamp", "Inflow Temp", "Inflow Absolute Humidity", 
                                "Inflow Relative Humidity", "Outflow Temp", 
                                "Outflow Absolute Humidity", "Outflow Relative Humidity"])
    
    try:
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(filename)
        data.to_csv(filename, mode='a', index=False, header=not file_exists)
        print(f"Saved: {timestamp}")
        print(f"  Inflow - Temp: {inflow_temp:.2f}°C, AH: {inflow_ah:.2f}, RH: {inflow_rh:.2f}%")
        print(f"  Outflow - Temp: {outflow_temp:.2f}°C, AH: {outflow_ah:.2f}, RH: {outflow_rh:.2f}%")
        print("-" * 50)
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main():
    """Main function to run the humidity logger"""
    global recording, stop_flag
    
    print("Dual Arduino Humidity Data Logger")
    print("Press 'q' to stop recording and create a new file")
    print("=" * 60)
    
    # Setup serial connections
    ser_inflow, ser_outflow = setup_serial_connections()
    if not ser_inflow or not ser_outflow:
        print("Failed to setup serial connections. Exiting...")
        return
    
    try:
        while True:
            # Get parameters for new file
            base_name = input("Enter base filename (press Enter for 'AbsoluteHumidityData'): ").strip()
            if not base_name:
                base_name = "AbsoluteHumidityData"
            
            try:
                flow_rate = float(input("Enter FlowRate: "))
                deseccant_amount = float(input("Enter Amount of deseccant: "))
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                continue
            
            # Create filename
            filename = create_filename(base_name, flow_rate, deseccant_amount)
            
            print(f"\nCurrent working directory: {os.getcwd()}")
            print(f"CSV file will be saved at: {os.path.join(os.getcwd(), filename)}")
            print(f"Recording data to: {filename}")
            print("Press 'q' to stop recording...\n")
            
            # Reset flags
            recording = True
            stop_flag = False
            
            # Start keyboard listener thread
            keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
            keyboard_thread.start()
            
            # Main data recording loop
            while recording:
                # Read data from both Arduinos
                inflow_data = read_arduino_data(ser_inflow, "Inflow")
                outflow_data = read_arduino_data(ser_outflow, "Outflow")
                
                # Only save if both readings are valid
                if (inflow_data[0] is not None and outflow_data[0] is not None):
                    save_to_csv(inflow_data, outflow_data, filename)
                else:
                    print("Waiting for valid data from both sensors...")
                
                time.sleep(1)  # Small delay between readings
            
            # Ask if user wants to create another file
            print(f"\nData recording stopped. File saved as: {filename}")
            
            choice = input("Do you want to create a new file? (y/n): ").strip().lower()
            if choice != 'y' and choice != 'yes':
                break
            
            print("\n" + "=" * 60)
    
    finally:
        print("Closing serial connections...")
        ser_inflow.close()
        ser_outflow.close()
        print("Exiting humidity logger...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")