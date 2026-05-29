# Acer Predator Triton AI RGB Reverse Engineering
## Background
This was all tested with an Acer Predator Triton 14 AI (PT14-52T) under Fedora Linux 44, but it should work across distros since it only uses HID calls, which also means that this works without super user privileges!

RGB is (officially) supported on Windows 11 only, so there are several unsupported features under Linux. [Jafar Akhondali](https://github.com/JafarAkhondali/acer-predator-turbo-and-rgb-keyboard-linux-module), [0x7375646](https://github.com/0x7375646F/Linuwu-Sense), and [fcrespo82](https://github.com/fcrespo82/acer-lighting-daemon) attempt so solve these issues, but they do not fully support this laptop, so I decided to make my own project that aims to support it. 

This also serves as a compatability guide for other PT14-52T laptops since there were many things that did not work out of the box (but had community patches or workarounds!)

---

<details>
<summary>Expand for information about how this works...</summary>

  ## General impressions

Without this control, the RGB on the keyboard defaults to the wave mode, and turns off after 30 seconds. Listed below are the packets that I have found to control the RGB on the keyboard only.

To send the packets, I am using the hid module from Python and using the ```send_feature_report``` function to send these bytes. I found what device to apply this to by running ```hid.enumerate()``` in Python, then sending control commands to each device and looking for changes; for me, this was the last device printed by this command.

It seems that the controller will only apply these changes if the checksums match their own internal algorithms, but I've derived the algorithm through packet analysis.

Sometimes, I need to clear the previous modes for it to change, and they are also listed below; these were pulled direcltly from wireshark.

It seems the keyboard is the only thing that uses USB HID to control RGB, but since it is HID, there is no root access needed! The modes I have found are listed below.

---

**Universal Checksum Value:** ```(0xFF - (sum(packett[:7]) & 0xFF)) & 0xFF```
If not correct, the keyboard will go black. I've included simplified formulas for each type of mode

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

XX is speed in odd numbers \ CS must match this checksum formula or no changes will apply: ```cs = (0xff - sum(packet[:7])) & 0xff```

Breathing:  ```08 02 02 XX 32 e0 00 CS```, tested xx values 1-9 with corresponding chesksums \
Dazzling:   ```08 02 2a XX 32 e0 00 CS```, tested w/ xx 01, cs b8 \
Disco:      ```08 02 2f XX 32 00 00 CS```, tested w/ xx 01, cs 93 \
Fireball:   ```08 02 27 XX 32 e0 00 CS```, tested w/ xx 01, cs bb \
Light Show: ```08 02 32 XX 32 00 00 CS```, tested w/ xx 01, cs 90 \
Ping Pong:  ```08 02 30 XX 32 00 00 CS```, tested w/ xx 01, cs 92 \
Racing:     ```08 02 2d XX 32 00 00 CS```, tested w/ xx 01, cs 95 \
Rain Drop:  ```08 02 0a XX 32 e0 00 CS```, tested w/ xx 01, cs d8 \
Ripple:     ```08 02 06 XX 32 e0 00 CS```, tested w/ xx 01, cs dc \
Snake:      ```08 02 05 XX 32 e0 00 CS```, tested w/ xx 01, cs dd \
Sprouting:  ```08 02 2e XX 32 00 00 CS```, tested w/ xx 05, cs 90 \
Swiping:    ```08 02 2c XX 32 00 00 CS```, tested w/ xx 01, cs 96 \
Wave:       ```08 02 31 XX 32 00 00 CS```, tested w/ xx 01, cs 91 


 ## STATIC MODE

RR, GG, BB, are the brightness of each led. FF 00 00 would be red, 00 FF 00 would be green, 00 00 FF would be blue. \ CS is also checksum but uses this different formula: ```cs = (0xeb - ((r + g + b) & 0xff)) & 0xff```

Static (any color): ```14 00 00 RR GG BB 00 CS```


## 30 SECOND KEYBOARD TIMEOUT

On:         ```30 01 01 00 00 00 00 cd``` \
Off:        ```30 01 00 00 00 00 00 ce```

</details>

---


> [!warning]
> This is currently a very early proof of concept and is still in development, so unexpected things may happen

## Usage
Change the r, g, and b variables in clrchange.py to desired values **in hex format** and run (very crude but **WILL** change)
## Road Map/Future Plans
- [x] Support modes other than static
- [x] Speed control for other modes
- [ ] Brightness control within the app
- [ ] Support individual keys
- [ ] Make this a daemon (so rgb can turn off/on from sleep/wake events)
- [ ] Make this easier to control (gui or tui maybe)
- [ ] Support changing the lights found on the touchpad 
- [ ] Support (really integrate) all other rgb lights found elsewhere (there already exists slightly broken support from [acer-lighting-daemon](https://github.com/fcrespo82/acer-lighting-daemon), but i may have to fix it, and I will attempt to include controls for it
