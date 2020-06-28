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

### _MacOS:_
* Python 3.5 or greater, you can install it with one of these options:
  * _[Recommended]_ Homebrew (install homebrew by running `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"` in a terminal window, then `brew install python`).
  * _[Might have issues]_ The latest installer from the [python.org releases page](https://www.python.org/downloads/release) ([3.8.3](https://www.python.org/ftp/python/3.8.3/python-3.8.3-macosx10.9.pkg) at the time of this writing).
 
 **NOTE:** If you get the `"Could not get HiyaCFW"` error, run ``pip install certifi`` to install the needed certificates for python.

## What it includes:
* 7za binaries for Windows, Linux and MacOS. It's used to decompress the HiyaCFW latest release as [@RocketRobz](https://github.com/RocketRobz) uploaded it as a 7z archive. Compiled from the [kornelski's GitHub repo](https://github.com/kornelski/7z).
* twltool binaries for Linux and MacOS. Compiled from the [WinterMute's GitHub repo](https://github.com/WinterMute/twltool). For Windows the twltool included with HiyaCFW is used.
* NDS bootloader creator binaries for Linux and MacOS (based off devkitPro's ndstool v1.27). Compiled from [my GitHub repo](https://github.com/mondul/NDS-Bootloader-Creator). For Windows the ndstool included with HiyaCFW is used.
* fatcat binaries for Windows, Linux and MacOS. Compiled from the [Gregwar's GitHub repo](https://github.com/Gregwar/fatcat).

## How to use it:
### _Windows:_
* Go to the helper's folder.
* Double-click on the _HiyaCFW_Helper.exe_ file.

### _Linux:_
* Open a terminal.
* _cd_ to the helper's folder (`cd ~/Downloads/HiyaCFW-Helper` or whatever).
* Run `./HiyaCFW_Helper.py`.

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
