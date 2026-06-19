import requests
import sys
import argparse
import time

# ANSI Color Codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# Safe operating ranges (matches bitaxe_benchmark_config.json)
MIN_VOLTAGE_MV = 1000
MAX_VOLTAGE_MV = 1400
MIN_FREQUENCY_MHZ = 400
MAX_FREQUENCY_MHZ = 1200

def parse_arguments():
    parser = argparse.ArgumentParser(description="Bitaxe Settings Tool - Set voltage and frequency")
    parser.add_argument(
        "bitaxe_ip", 
        help="IP address of the Bitaxe (e.g., 192.168.2.26)"
    )
    parser.add_argument(
        "-v",
        "--voltage",
        type=int,
        required=True,
        help="Core voltage in mV (e.g., 1150)"
    )
    parser.add_argument(
        "-f",
        "--frequency",
        type=int,
        required=True,
        help="Frequency in MHz (e.g., 500)"
    )
    parser.add_argument(
        "--no-restart",
        action="store_true",
        help="Don't restart the system after applying settings"
    )

    # If no arguments are provided, print help and exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if not (MIN_VOLTAGE_MV <= args.voltage <= MAX_VOLTAGE_MV):
        parser.error(
            f"voltage {args.voltage}mV out of range "
            f"[{MIN_VOLTAGE_MV}, {MAX_VOLTAGE_MV}]mV"
        )
    if not (MIN_FREQUENCY_MHZ <= args.frequency <= MAX_FREQUENCY_MHZ):
        parser.error(
            f"frequency {args.frequency}MHz out of range "
            f"[{MIN_FREQUENCY_MHZ}, {MAX_FREQUENCY_MHZ}]MHz"
        )

    return args

def get_current_settings(bitaxe_ip):
    """Fetch and display current settings"""
    try:
        response = requests.get(f"{bitaxe_ip}/api/system/info", timeout=10)
        response.raise_for_status()
        info = response.json()
        
        voltage = info.get("coreVoltage", "N/A")
        frequency = info.get("frequency", "N/A")
        
        print(GREEN + "Current Settings:" + RESET)
        print(f"  Core Voltage: {voltage}mV")
        print(f"  Frequency: {frequency}MHz")
        print()
        
        return voltage, frequency
    except requests.exceptions.RequestException as e:
        print(YELLOW + f"Warning: Could not fetch current settings: {e}" + RESET)
        return None, None

def set_system_settings(bitaxe_ip, core_voltage, frequency, restart=True):
    """Apply voltage and frequency settings"""
    settings = {
        "coreVoltage": core_voltage,
        "frequency": frequency
    }
    
    try:
        print(YELLOW + f"Applying settings:" + RESET)
        print(f"  Core Voltage: {core_voltage}mV")
        print(f"  Frequency: {frequency}MHz")
        
        response = requests.patch(f"{bitaxe_ip}/api/system", json=settings, timeout=10)
        response.raise_for_status()
        
        print(GREEN + "Settings applied successfully!" + RESET)
        
        if restart:
            print(YELLOW + "Restarting system..." + RESET)
            time.sleep(2)
            restart_response = requests.post(f"{bitaxe_ip}/api/system/restart", timeout=10)
            restart_response.raise_for_status()
            print(GREEN + "System restarted. Please wait for it to stabilize." + RESET)
        else:
            print(YELLOW + "Note: Settings applied but system not restarted. Changes may not take effect until restart." + RESET)
            
    except requests.exceptions.RequestException as e:
        print(RED + f"Error applying settings: {e}" + RESET)
        sys.exit(1)

def main():
    args = parse_arguments()
    bitaxe_ip = f"http://{args.bitaxe_ip}"
    
    print(GREEN + "=" * 50 + RESET)
    print(GREEN + "Bitaxe Settings Tool" + RESET)
    print(GREEN + "=" * 50 + RESET)
    print()
    
    # Get current settings
    get_current_settings(bitaxe_ip)
    
    # Apply new settings
    set_system_settings(
        bitaxe_ip, 
        args.voltage, 
        args.frequency,
        restart=not args.no_restart
    )
    
    print()
    print(GREEN + "Done!" + RESET)

if __name__ == "__main__":
    main()
