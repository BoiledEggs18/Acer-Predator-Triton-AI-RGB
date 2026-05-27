# Unofficial linux support for RGB on Acer Predator Triton AI laptops
## WARNING: This is currently a very early proof of concept and is still in development, so unexpected things may happen
This is based off of both [Jafar Akhondali's](https://github.com/JafarAkhondali/acer-predator-turbo-and-rgb-keyboard-linux-module) and [0x7375646's](https://github.com/0x7375646F/Linuwu-Sense) projects with very similar goals. I've noticed that with my new Acer Predator Triton 14 AI (PT14-52T), there is absolutely zero support for the keyboard rgb, so that means the keyboard stays on even during sleep! 

I haven't found any working drivers or patches from even the community, so I decided to reverse engineer my own. Since this laptop is so new, I hope that this will also come to support future laptops with per-key rgb. 

This also serves as a compatability guide for other PT14-52T laptops since there were many things that did not work out of the box (but had community patches or workarounds!)
## Usage:
Change the r, g, and b variables in clrchange.py to desired values **in hex format** and run (very crude but will change)
## Road Map/Future Plans
- [ ] Support modes other than static
- [ ] Speed control for other modes
- [ ] Brightness control within the app
- [ ] Support individual keys
- [ ] Make this a kernel module (so rgb can turn off/on from sleep/wake events)
- [ ] Make this easier to control (gui or tui maybe)
- [ ] Support changing the lights found on the touchpad 
- [ ] Support (really integrate) all other rgb lights found elsewhere (there already exists slightly broken support from [acer-lighting-daemon](https://github.com/fcrespo82/acer-lighting-daemon), but i may have to fix it, and I will attempt to include controls for it
