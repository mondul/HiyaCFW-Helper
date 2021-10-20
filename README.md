# HiyaCFW-Helper

In order to make things easier for me, and because I don't have Windows, I edited the HiyaCFW Helper Python script by jerbear64 and LmN in order to add a graphical user interface to it.

![Screenshot](https://image.ibb.co/hhzKRL/Screen-Shot-2018-10-18-at-16-30-18.png)

## What it does:
* Allows you to browse for your NAND backup, no need to place it at the same folder.
* Shows the option to choose the output destination, which should be a (preferably empty) FAT formatted SD card or any other folder.
* Downloads the latest HiyaCFW release and decompress it.
* Autodetects the console region from the NAND dump, downloads and decrypts its v512 launcher.
* Creates the patched _00000002.app_ and _bootloader.nds_ for the custom firmware.
* Uses your platform's twltool (binaries for Linux and MacOS included) to decrypt the NAND.
* Extracts the decrypted NAND to the chosen output destination.
* Installs the HiyaCFW and the patched files on the chosen output destination.
* (Optional) installs the latest release of TWiLightMenu++ on the chosen output destination.

### _NAND mode:_
Clicking on the integrated circuit button will give you a NAND mode, where you can remove the No$GBA footer or add it.

## Requirements:
### _Windows:_
* None, everything needed is included in the release archive.

### _Linux:_
* Python 3.5 or greater with the Tk library (I had to do `sudo apt-get install python3-tk -y` in my Ubuntu virtual machine, `sudo dnf install python3-tkinter` in Fedora, `sudo pacman -S tk` in Arch Linux). You might need to install the Python 3 distutils package also.

### _macOS:_
* None, everything needed in included in the release archive.

## What it includes:
* 7za binaries for Windows, Linux and macOS. It's used to decompress the HiyaCFW latest release as [@RocketRobz](https://github.com/RocketRobz) uploaded it as a 7z archive. Compiled from the [kornelski's GitHub repo](https://github.com/kornelski/7z).
* twltool binaries for Linux and macOS. Compiled from the [WinterMute's GitHub repo](https://github.com/WinterMute/twltool). For Windows the twltool included with HiyaCFW is used.
* NDS bootloader creator binaries for Linux and macOS (based off devkitPro's ndstool v1.27). Compiled from [my GitHub repo](https://github.com/mondul/NDS-Bootloader-Creator). For Windows the ndstool included with HiyaCFW is used.
* fatcat binaries for Windows, Linux and mxacOS. Compiled from the [Gregwar's GitHub repo](https://github.com/Gregwar/fatcat).

## How to use it:
See the DS-Homebrew Wiki's [Installing hiyaCFW](https://wiki.ds-homebrew.com/hiyacfw/installing) page for instructions on how to use this.

Thanks to:
* jerbear64 and LmN for the original script.
* [@RocketRobz](https://github.com/RocketRobz) for his HiyaCFW fork, its releases and for having the helper script on his repo.
* [@Sha8q](https://github.com/Sha8q) for the idea.
* WB3000 for his [NUS Downloader source code](https://code.google.com/archive/p/nusdownloader/source/default/source).

Download it from the releases page.
