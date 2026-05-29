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

Without this control, the RGB on the keyboard defaults to the wave mode, and turns off after 30 seconds. Listed below are the packets that I have found to control the RGB on the keyboard only.

To send the packets, I am using the hid module from Python and using the ```send_feature_report``` function to send these bytes. I found what device to apply this to by running ```hid.enumerate()``` in Python, then sending control commands to each device and looking for changes; for me, this was the last device printed by this command.

It seems that the controller will only apply these changes if the checksums match their own internal algorithms, but I've derived the algorithm through packet analysis.

Sometimes, I need to clear the previous modes for it to change, and they are also listed below; these were pulled directly from Wireshark.

It seems the keyboard is the only thing that uses USB HID to control RGB, but since it is HID, there is no root access needed! The modes I have found are listed below.

---

**Universal Checksum Value:** ```(0xFF - (sum(packett[:7]) & 0xFF)) & 0xFF```

If the checksum is not correct, the keyboard will go black.

---

## BYTES TO CLEAR PREVIOUS MODES
   ```
   [0x88,0x00,0x00,0x00,0x00,0x00,0x00,0x77]
   [0xb1,0x00,0x00,0x00,0x00,0x00,0x00,0x4e]
   [0x08,0x02,0x00,0x00,0x00,0x00,0x00,0xf5]
   [0x14,0x00,0x00,0x00,0x00,0x00,0x00,0xeb]
   ```
--- 

## NON STATIC MODES

**General formula for non static modes:** ```08 02 MM SS BB FF 00 CS``` where: 
- MM is mode (see below for modes)
- SS is speed (from 01-09 in odd intervals; 01 being the fastest and 09 being slowest)
- BB is brightness (from 01-32; 01 being off, 32 being max brightness)
- FF is a flag (either 00 or e0, only certain modes need it)
- CS is the checksum 

**Modes:** \
Breathing:  ```02``` \
Dazzling:   ```2a``` \
Disco:      ```2f``` \
Fireball:   ```27``` \
Light Show: ```32``` \
Ping Pong:  ```30``` \
Racing:     ```2d``` \
Rain Drop:  ```0a``` \
Ripple:     ```06``` \
Snake:      ```05``` \
Sprouting:  ```2e``` \
Swiping:    ```2c``` \
Wave:       ```31``` 


## STATIC MODE

**General formula for static modes:**  ```14 00 00 RR GG BB 00 CS``` where: 
- RR is red brightness (from 00-FF)
- GG is green brightness (from 00-FF)
- BB is blue brightness (from 00-FF)
- CS is checksum \
Notes: \
There is no official brightness control as the app within windows just lowers each rgb value accordingly.

## 30 SECOND KEYBOARD TIMEOUT

On:         ```30 01 01 00 00 00 00 cd``` \
Off:        ```30 01 00 00 00 00 00 ce```

## Quirks:

Brightness higher than ```32```, or 50 in decimal format, will change the colors in very funny ways. It is extremely similar to how Tetris on the NES will shift colors after a certain amount of levels, but it is not caused the same way ):

---

Speed higher than 09 will effectively become a standstill.

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
- [ ] Support individual keys
- [ ] Make this easier to control (likely a tui)
- [ ] Make this a daemon (so rgb can turn off/on from sleep/wake events)
- [ ] Complete compatability guide for Acer Triton Ai laptops
- [ ] Support changing the lights found on the touchpad 
- [ ] Support (really integrate) all other rgb lights found elsewhere (there already exists slightly broken support from [acer-lighting-daemon](https://github.com/fcrespo82/acer-lighting-daemon), but i may have to fix it, and I will attempt to include controls for it)
