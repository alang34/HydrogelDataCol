import serial
import pandas as pd
from datetime import datetime
import os
import threading
import sys

# Set up Serial connection (change 'COM4' for Windows or '/dev/ttyUSB0' for Linux/Mac)
ser = serial.Serial('COM4', 9600, timeout=1)

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

def create_filename(base_name, air_pressure, wattage):
    """Creates filename with air pressure and wattage parameters"""
    filename = f"{base_name}_P{air_pressure}_W{wattage}.csv"
    return filename

def read_serial_data():
    """Reads temperature data from Arduino."""
    try:
        line = ser.readline().decode().strip()  # Read line from Arduino
        if line:
            temperature = float(line)  # Convert to float
            return temperature
    except Exception as e:
        print("Error:", e)
        return None

def save_to_csv(temperature, filename):
    """Saves the temperature data to a CSV file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get timestamp

    # Create a DataFrame
    data = pd.DataFrame([[timestamp, temperature]], 
                        columns=["Timestamp", "Temperature (°C)"])

    # Append data to CSV file
    try:
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(filename)
        data.to_csv(filename, mode='a', index=False, header=not file_exists)
        print(f"Saved: {timestamp}, Temperature: {temperature}°C")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main():
    """Main function to run the temperature logger"""
    global recording, stop_flag
    
    print("Temperature Data Logger")
    print("Press 'q' to stop recording and create a new file")
    print("=" * 50)
    
    while True:
        # Get parameters for new file
        base_name = input("Enter base filename (without extension): ").strip()
        if not base_name:
            base_name = "temperature_data"
        
        try:
            air_pressure = float(input("Enter air pressure value: "))
            wattage = float(input("Enter wattage value: "))
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            continue
        
        # Create filename
        filename = create_filename(base_name, air_pressure, wattage)
        
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
            temperature = read_serial_data()
            if temperature is not None:
                save_to_csv(temperature, filename)
        
        # Ask if user wants to create another file
        print(f"\nData recording stopped. File saved as: {filename}")
        
        choice = input("Do you want to create a new file? (y/n): ").strip().lower()
        if choice != 'y' and choice != 'yes':
            break
        
        print("\n" + "=" * 50)
    
    print("Exiting temperature logger...")
    ser.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        ser.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        ser.close()