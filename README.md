# Acer Predator Triton AI RGB Reverse Engineering
## Background
Currently, this repo serves as my documentation of Acer's Keyboard RGB protocal which was found by reverse engineering. This also serves as a proof of concept for other laptops and **WILL** be developed into an app later.

This was all tested with an Acer Predator Triton 14 AI (PT14-52T) under Fedora Linux 44, but it should work across distros since it only uses HID calls, which also means that this works without super user privileges!

RGB is (officially) supported on Windows 11 only, so there are several unsupported features under Linux. [Jafar Akhondali](https://github.com/JafarAkhondali/acer-predator-turbo-and-rgb-keyboard-linux-module), [0x7375646](https://github.com/0x7375646F/Linuwu-Sense), and [fcrespo82](https://github.com/fcrespo82/acer-lighting-daemon) attempt so solve these issues, but they do not fully support this laptop, so I decided to make my own project that aims to support it. 

This will also serve as a compatability guide for other PT14-52T laptops since there is many things that did not work out of the box (but had community patches or workarounds!)

---

<details>
<summary>Expand for information about how this works...</summary>

## General impressions

Without this control, the RGB on the keyboard defaults to the wave mode, and turns off after 30 seconds. The packets within this documentation control the RGB on the **keyboard only**.

To send the packets, I am using the hid module from Python and using the ```send_feature_report``` or ```write()``` function to send these bytes. I found what device to apply this to by running ```hid.enumerate()``` in Python, then sending control commands to each device and looking for changes; for me, this was the last device printed by this command. 

When sending packets, each packet requires a leading zero byte, which can be sent with ```[0] + YOUR_PACKET_HERE```. If the leading byte is unsent, the keyboard will not respond. Similarly, every packet requires a valid checksum; it is always the last byte in each packet, and changes will not apply if it does not match the controller's own algorithm. However, the checksum formula has been reverse engineered too, and it is found within this documentation.

Sometimes, the controller needs to clear the previous modes for it to change. During my testing, I was unable to reliably replicate the conditions where this was necessary. I have had the highest success rate when repeatedly inputting incorrect modes or wrong checksums, but it was never 100%. The packets in question were pulled directly from Wireshark.

It seems the keyboard is the only thing that uses USB HID to control RGB, but since it is HID, there is no root access needed. The modes I have found are listed below.

---

## Universal Checksum Value: 
**```(0xFF - (sum(packet[:7]) & 0xFF)) & 0xFF```**

If the checksum is not correct, the keyboard will not apply any changes.

---

## BYTES TO CLEAR PREVIOUS MODES
   
   ```[0x88,0x00,0x00,0x00,0x00,0x00,0x00,0x77]``` \
   ```[0xb1,0x00,0x00,0x00,0x00,0x00,0x00,0x4e]``` \
   ```[0x08,0x02,0x00,0x00,0x00,0x00,0x00,0xf5]``` \
   ```[0x14,0x00,0x00,0x00,0x00,0x00,0x00,0xeb]``` 
   
--- 


## NON STATIC MODES 

### General formula for non static modes 
**```08 02 MM SS BB FF 00 CS```**

Where:
- MM is mode (see table below)
- SS is speed (Values range from 01 to 09, 01 being the fastest and 09 being slowest)
- BB is brightness (from 01-32; 01 being off, 32 being max brightness)
- FF is unknown, but likely a flag. Set to ```00``` unless otherwise observed for specific mode (see table below) 
- CS is the checksum

|   Mode   | Byte | Flag |
|----------|------|------|
| Breathing|  02  |  e0  |
| Dazzling |  2a  |  e0  |
| Disco    |  2f  |  00  |   
| Fireball |  27  |  e0  |
| LightShow|  32  |  00  |
| Ping Pong|  30  |  00  |
| Racing   |  2d  |  00  |
| Rain Drop|  0a  |  e0  |
| Ripple   |  06  |  e0  |
| Snake    |  05  |  e0  |
| Sprouting|  2e  |  00  |
| Swiping  |  2c  |  00  |
| Wave     |  31  |  00  |

--- 

## STATIC MODE

### General formula for static modes
**```14 00 00 RR GG BB 00 CS```**  

Where:
- RR is red brightness (from 00-FF)
- GG is green brightness (from 00-FF)
- BB is blue brightness (from 00-FF)
- CS is checksum 

---

## STATIC PER-KEY MODE

### Control Process
```88 00 00 00 00 00 00 77``` -- Clear previous modes (see notes and quirks)

```12 00 00 08 00 00 00 e5``` -- Enter custom per-key mode/prepare for 512 Byte array

*512 Byte framebuffer*        -- See the next section for layout and formula

```08 02 33 05 32 08 01 82``` -- Apply changes from 512 bytes. Byte 4 (```32```) is brightness.


### Framebuffer Layout
Each key gets 4 bytes: ```00 RR GG BB```. Only 408 bytes of the 512 are used, while the rest are empty.

There are 6 rows and 17 columns, however the layout is column-by-column, not row by row. 

This means the structure looks like: ```<ESCAPE_BYTES> <TILDE_BYTES> <TAB_BYTES> <CAPS_BYTES> <SHIFT_BYTES> <CTRL_BYTES> <F1_BYTES> <1_BYTES> <Q_BYTES> ...```

Therefore, this formula can be used to find the location of the first key's bytes in the array: ```location = 1 + (COLUMN · 24) + (ROW · 4)``` \
Where: **COLUMN** is the column from 0-16 and **ROW** is the row from 0-5

Below is a helpful table of the keys found in each row (Keyboard is standard US English layout):
|Row|         Keys         |
|---|----------------------|
| 0 |ESC, F1-F12, Hotkey, Print Screen, Delete, Power |
| 1 | ` through Backspace  |
| 2 |     Tab through \    |
| 3 |  Caps through Enter  |
| 4 | LShift through RShift|
| 5 | Ctrl through RArrow  |

### Example: 
To set the power button to white, set the 3 bytes following ```1 + (16 · 24) + (0 · 4)``` (the 385th byte) to ```FF```  


## 30 SECOND KEYBOARD TIMEOUT

**On:         ```30 01 01 00 00 00 00 cd```** \
**Off:        ```30 01 00 00 00 00 00 ce```**

# Notes and Quirks
 - Per-key mode **MUST** use the ```write()``` function on **the 512 Byte packet only** or it will not apply. All other 8 Byte packets (which includes other modes) should use ```send_feature_report``` instead.
 - In per-key mode, the apply changes packet (```08 02 33 05 32 08 01 82```) is the only observed case where bytes 5 and 6 use values other than ```e0``` or ```00```; their purpose is unknown.
 - In per-key mode, there will occasionally be locations that do not light a key. This is to ensure the furthermost right key is always on the 17th column regardless of the amount of keys on the row.
 - For static mode, there is no direct support for brightness. In Windows, it will just lower each value of red, green, and blue accordingly.
 - As stated in impressions, bytes to clear previous modes are not always necessary. Inclusion is a precaution because replication of the necessity is not consistent.
 - When brightness is brought to a value higher than ``0x32`` (or 50), the color palette will change. The source of these color palettes are unknown and are **not** found on clean 32 byte intervals.
 - When speed is brought to a higher value than 09, it will effectively become a standstill. Occasionally, there will be "islands of stability" where the speed appears to return to normal, but **more testing is needed to find the exact behavior.**

</details>

---


> [!warning]
> This is currently a very early proof of concept and is still in development, so unexpected things may happen

## Usage
Change the r, g, and b variables in clrchange.py to desired values **in hex format** and run (very crude but **WILL** change)
## Road Map/Future Plans
- [x] Support modes other than static
- [x] Speed control for other modes
- [x] Brightness control within the app
- [x] Support individual keys
- [ ] Make this easier to control (likely a tui)
- [ ] Make this a daemon (so rgb can turn off/on from sleep/wake events)
- [ ] Complete compatability guide for Acer Triton Ai laptops
- [ ] Support changing the lights found on the touchpad 
- [ ] Support (really integrate) all other rgb lights found elsewhere (there already exists slightly broken support from [acer-lighting-daemon](https://github.com/fcrespo82/acer-lighting-daemon), but i may have to fix it, and I will attempt to include controls for it)
