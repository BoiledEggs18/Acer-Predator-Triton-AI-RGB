import hid
import time
import select
import sys

## for testing only
# dev = hid.device()
# dev.open_path(b"3-6:1.3")


## these turn off all modes. They are not always needed, but it ensures changes will happen.
reset_packets = [ 
    [0x08,0x02,0x40,0x0a,0x1e,0x00,0x00,0x8d],  
    [0x88,0x00,0x00,0x00,0x00,0x00,0x00,0x77],  
    [0xb1,0x00,0x00,0x00,0x00,0x00,0x00,0x4e],  
    [0x08,0x02,0x00,0x00,0x00,0x00,0x00,0xf5], 
    [0x08,0x02,0x01,0x0a,0x32,0x00,0x00,0xb8], 
    [0x14,0x00,0x00,0x00,0x00,0x00,0x00,0xeb],  
]

## known modes
non_static_modes_flagged = {
    "breathing": 0x02,
    "dazzling": 0x2a,
    "fireball": 0x27,
    "raindrop": 0x0a,
    "ripple": 0x06,
    "snake": 0x05,
}
non_static_modes_unflagged = {
    "disco": 0x2f,
    "lightshow": 0x32,
    "pingpong": 0x30,
    "racing": 0x2d,
    "sprouting": 0x2e,
    "swiping": 0x2c,
    "wave": 0x31,
}

dev = None

def checksum(packet):
    return (0xff - (sum(packet[:7]) & 0xff)) & 0xff

def check_range(dec):
    while True:
        if 0 <= dec <= 255 :
            return dec
        dec = int(input("Please use a number between 0 and 255: "))



def send_packets(packets):
    for p in packets:
            dev.send_feature_report(bytes([0] + p))
            time.sleep(0.1)

def timed_input(prompt, timeout, default):
    print(prompt, end='', flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().rstrip('\n')
    print(f"\nNo input received, defaulting to '{default}'...")
    return default

def reset_device():
    try:
        send_packets(reset_packets)
    except:
        print("Something bad happened (likely your device was not found). Please try selecting your device again.\n Aborting now...")
        exit()

def find_device():
    global dev
#    print("This action is only necessary once. \n") ~~~ this is not currently true ):
    print("Below is a list of your HID Devices; please choose your RGB controller. \nIf you are unsure, try selecting one; if your keyboard doesn't go black, select another one.")
    print("\nWARNING: Your keyboard may become unresponsive if you chose the keyboard. This is only temporary; if this happens, simply choose another device.\n")

    time.sleep(3)

    devices = hid.enumerate()
    try:
        dev = hid.device()
    except:
        print("Please use python-hidapi instead of python-hid \nExiting now...")
        exit()

    if not devices: 
        print("No HID devices found. Ensure python-hidapi is installed and that your laptop is supported.")
        exit()

    for i, device in enumerate(devices,1):
        path = device['path'].decode()
        print(f"Interface: {device['interface_number']} | {path} | {device['manufacturer_string']} | Vendor: {device['vendor_id']} | Product: {device['product_id']}")

    while True:
        try:
            cdev = int(input("Select a device by interface number (usually interface 3): "))
            matches = [d for d in devices if d['interface_number'] == cdev]
            if not matches:
                print("No device found with that interface number.")
                continue
            kbdpath = matches[0]['path'] 
            dev.open_path(kbdpath) 
        except Exception as e:
            print(f"Error: {e}")
            print("If the error is 'open failed', please try running again with sudo. A fix is planned")
#            print("Invalid input. Please enter a valid interface number."
            continue

        reset_device()

        print("\nYour keyboard should now be black and you can continue. If not, try selecting a different interface number and try again.")
        cont = timed_input("[1] Continue | [2] Select another interface \nAuto-selecting [2] in 10 seconds... \n", 10, "2")

        if cont == "1":
#          may be used later            
#          with open("vars.config", "w") as file: 
#               file.write(f"Path: {kbdpath}\n")
            break
        else:
            dev.close()  

    return kbdpath, dev

def set_static(r, g, b):
    cs = checksum([0x14, 0x00, 0x00, r, g, b, 0x00])
    reset_device()
    send_packets([[0x14, 0x00, 0x00, r, g, b, 0x00, cs]])
    print(r, g, b, cs)

def set_non_static(mode, brightness, speed):
    if mode in non_static_modes_flagged:
        mm = non_static_modes_flagged[mode]
        ff = 0xe0
    elif mode in non_static_modes_unflagged:
        mm = non_static_modes_unflagged[mode]
        ff = 0x00
    else:
        print("Something evil happened (mode not found). Aborting now...")
        exit()
    
    cs = checksum([0x08, 0x02, mm, speed, brightness, ff, 0x00])
    reset_device()
    send_packets([[0x08, 0x02, mm, speed, brightness, ff, 0x00, cs]])

def main():
    while True:
        choice = input("What would you like to do? \n1. Choose RGB device (must be done first) \n2. Set a static mode (all keys) \n3. Set a non-static mode (all keys) \n4. Exit\n")
        if choice == "1" :
            find_device()
        elif choice == "2" :
            r = check_range(int(input("Red Brightness (0-255): ")))
            g = check_range(int(input("Green Brightness (0-255): ")))
            b = check_range(int(input("Blue Brightness (0-255): ")))
            set_static(r, g, b)
        elif choice == "3" :
            print("\nAvailable modes: breathing, dazzling, disco, fireball, lightshow, pingpong, racing, raindrop, ripple, snake, sprouting, swiping, wave\n")
            m = input("Select mode: ")
            b = check_range(int(input("Brightness (0-50, higher yields *unique* colors): ")))
            s = check_range(int(input("Speed (1-9, 9 being the slowest): ")))
            set_non_static(m, b, s)
        elif choice == "4" :
           exit()
        else: 
            print("Please choose a valid option")

main()
