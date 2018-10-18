# HiyaCFW-Helper

In order to make things easier for me, and because I don't have Windows, I edited the HiyaCFW Helper Python script by jerbear64 and LmN in order to add a graphical user interface to it.

![Screenshot](https://image.ibb.co/hhzKRL/Screen-Shot-2018-10-18-at-16-30-18.png)

## What it does:
* Allows you to browse for your NAND backup, no need to place it at the same folder.
* Downloads the latest HiyaCFW release and decompress it.
* Autodetects the console region from the NAND dump, downloads and decrypts its v512 launcher.
* Creates the patched _00000002.app_ and _bootloader.nds_ for the custom firmware.
* Uses your platform's twltool (binaries for Linux and MacOS included) to decrypt the NAND.
* Mounts the decrypted NAND (OSFMount required for Windows) and extracts it to a folder named "out".
* Installs the HiyaCFW and the patched files on the "out" folder.
* (Optional) installs the latest release of TWiLightMenu++ on the "out" folder.

All that you have to do then is copy the contents of the "out" folder onto your (preferably empty) SD card.

### _NAND mode:_
Clicking on the integrated circuit button will give you a NAND mode, where you can uninstall unlaunch or install its v1.4 stable release, remove the No$GBA footer or add it. Recommended only for those with a hardmod.

## Requirements:
### _Windows:_
* OSFMount.
* You will need to run the _HiyaCFW_Helper.exe_ file as administrator in order to mount the decrypted NAND.

### _Linux:_
* Python 2.7 with the Tk library (I had to do `sudo apt-get install python python-tk -y` in my LUbuntu virtual machine; `sudo dnf install python-tkinter` in Fedora).
* You will need to run the script as sudo in order to mount the decrypted NAND.

### _MacOS:_
* Nothing, as it already includes Python 2.7 with the Tk library and doesn't need root to mount the decrypted NAND.

## What it includes:
* 7za binaries for Windows, Linux and MacOS. It's used to decompress the HiyaCFW latest release as [@RocketRobz](https://github.com/RocketRobz) uploaded it as a 7z archive. Compiled from the [kornelski's GitHub repo](https://github.com/kornelski/7z).
* twltool binaries for Windows, Linux and MacOS. Compiled from the [WinterMute's GitHub repo](https://github.com/WinterMute/twltool).
* NDS bootloader creator binaries for Linux and MacOS (based off devkitPro's ndstool v1.27). Compiled from [my GitHub repo](https://github.com/mondul/NDS-Bootloader-Creator). For Windows the ndstool included with HiyaCFW is used.
* In order to decrypt the launcher, the pyaes library by ricmoo, taken from [his GitHub repo](https://github.com/ricmoo/pyaes), was used.
* fatattr binary for Linux. It's used for setting FAT attributes in NAND mode. Compiled from the [Terseus' GitHub repo](https://github.com/Terseus/fatattr).

## How to use it:
### _Windows:_
* Go to the helper's folder.
* Right-click on the _HiyaCFW_Helper.exe_ file and click _Run as administrator_.

### _Linux:_
* Open a terminal.
* _cd_ to the helper's folder (`cd ~/Downloads/HiyaCFW-Helper` or whatever).
* Run `sudo ./HiyaCFW_Helper.py`.

### _MacOS:_
* Open a Terminal (⌘+Space and write _terminal_).
* _cd_ to the helper's folder (`cd ~/Downloads/HiyaCFW-Helper` or whatever).
* Run `./HiyaCFW_Helper.py`.

Thanks to:
* jerbear64 and LmN for the original script.
* [@RocketRobz](https://github.com/RocketRobz) for his HiyaCFW fork, its releases and for having the helper script on his repo.
* [@Sha8q](https://github.com/Sha8q) for the idea.
* WB3000 for his [NUS Downloader source code](https://code.google.com/archive/p/nusdownloader/source/default/source).

Download it from the releases page.
