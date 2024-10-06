# CatGenie A.I. By Petnovations

Home Assistant Integration for Petnovations CatGenie A.I. using their Public API.

To utilize this integration, you'll need to obtain your 'refreshToken'. This can be done by utilizing a utility such as [Requestly](https://requestly.com/) on a macOS M1 to inspect the traffic of the 'CatGenie' mobile application. 

The integration will provide you with several sensors that provide the current state of your CatGenie A.I:

* BLE Address
* Cartridge Capacity (X Cycles)
* Cartidge Remaining (X Cycles)
* Cat Activation Delay (Disabled / X Minutes)
* Cat Sensitivity
* Do Not Disturb (XX:00 to XX:00)
* Extra Dry (True / False)
* Fan Shutter (True / False
* Last Clean (X minutes/hours/days ago)
* MAC Address
* Manual Mode (Enabled/Disabled)
* Network Status (Connected / Disconnected)
* Network Type (Wifi, etc)
* Operation Mode (Cat / Time / Manual Mode)
* Operation Error
* Operation Progress (Idle / X % Completed)
* Operation Status (Idle / Cleaning)
* Panel Lock (Enabled / Disabled)
* Panel Lock Delay (Disabled / X Minutes)
* Schedule Cycles (Disabled / [XX:XX:XX]
* Serial Number (CGXXXXXXX)
* Used Solution (XX.XXoz)
* Volume Level (1-7)

This is a publicly developed integration that is not supported by the vendor, use at your own risk.

![](https://github.com/PrimeAutomation/petnovations/blob/main/example.png)

