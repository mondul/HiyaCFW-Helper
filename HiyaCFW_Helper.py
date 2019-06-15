#!/usr/bin/env python3

# HiyaCFW Helper
# Version 3.3
# Author: mondul <mondul@huyzona.com>

from tkinter import (Tk, Frame, LabelFrame, PhotoImage, Button, Entry, Checkbutton, Radiobutton,
    Label, Toplevel, Scrollbar, Text, StringVar, IntVar, RIGHT, W, X, Y, DISABLED, NORMAL, SUNKEN,
    END)
from tkinter.messagebox import askokcancel, showerror, showinfo, WARNING
from tkinter.filedialog import askopenfilename, askdirectory
from platform import system
from os import path, remove, chmod, rename, listdir
from sys import exit
from threading import Thread
from queue import Queue, Empty
from hashlib import sha1
from urllib.request import urlopen
from urllib.error import URLError
from json import loads as jsonify
from subprocess import Popen, DEVNULL
from struct import unpack_from
from shutil import rmtree, copyfile, copyfileobj
from distutils.dir_util import copy_tree, _path_created


####################################################################################################
# Thread-safe text class

class ThreadSafeText(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.queue = Queue()
        self.update_me()

    def write(self, line):
        self.queue.put(line)

    def update_me(self):
        try:
            while 1:
                self.insert(END, str(self.queue.get_nowait()) + '\n')
                self.see(END)
                self.update_idletasks()

        except Empty:
            pass

        self.after(500, self.update_me)


####################################################################################################
# Main application class

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.pack()

        # First row
        f1 = LabelFrame(self, text='NAND file with No$GBA footer', padx=10, pady=10)

        # NAND Button
        self.nand_mode = False

        nand_icon = PhotoImage(data=('R0lGODlhEAAQAIMAAAAAADMzM2ZmZpmZmczMzP///wAAAAAAAAA'
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAAYALAAAAAAQAB'
            'AAAARG0MhJaxU4Y2sECAEgikE1CAFRhGMwSMJwBsU6frIgnR/bv'
            'hTPrWUSDnGw3JGU2xmHrsvyU5xGO8ql6+S0AifPW8kCKpcpEQA7'))

        self.nand_button = Button(f1, image=nand_icon, command=self.change_mode, state=DISABLED)
        self.nand_button.image = nand_icon

        self.nand_button.pack(side='left')

        self.nand_file = StringVar()
        Entry(f1, textvariable=self.nand_file, state='readonly', width=40).pack(side='left')

        Button(f1, text='...', command=self.choose_nand).pack(side='left')

        f1.pack(padx=10, pady=10, fill=X)

        # Second row
        f2 = Frame(self)

        # Check box
        self.twilight = IntVar()
        self.twilight.set(1)

        self.chk = Checkbutton(f2, text='Install latest TWiLight Menu++ on custom firmware',
            variable=self.twilight)

        self.chk.pack(padx=10, anchor=W)

        # NAND operation frame
        self.nand_frame = LabelFrame(f2, text='NAND operation', padx=10, pady=10)

        self.nand_operation = IntVar()
        self.nand_operation.set(0)

        Radiobutton(self.nand_frame, text='Remove No$GBA footer', variable=self.nand_operation,
            value=0, command=lambda: self.enable_entries(False)).pack(anchor=W)

        Radiobutton(self.nand_frame, text='Add No$GBA footer', variable=self.nand_operation,
            value=1, command=lambda: self.enable_entries(True)).pack(anchor=W)

        fl = Frame(self.nand_frame)

        self.cid_label = Label(fl, text='eMMC CID', state=DISABLED)
        self.cid_label.pack(anchor=W, padx=(24, 0))

        self.cid = StringVar()
        self.cid_entry = Entry(fl, textvariable=self.cid, width=20, state=DISABLED)
        self.cid_entry.pack(anchor=W, padx=(24, 0))

        fl.pack(side='left')

        fr = Frame(self.nand_frame)

        self.console_id_label = Label(fr, text='Console ID', state=DISABLED)
        self.console_id_label.pack(anchor=W)

        self.console_id = StringVar()
        self.console_id_entry = Entry(fr, textvariable=self.console_id, width=20, state=DISABLED)
        self.console_id_entry.pack(anchor=W)

        fr.pack(side='right')

        f2.pack(fill=X)

        # Third row
        f3 = Frame(self)

        self.start_button = Button(f3, text='Start', width=16, command=self.hiya, state=DISABLED)
        self.start_button.pack(side='left', padx=(0, 5))

        Button(f3, text='Quit', command=root.destroy, width=16).pack(side='left', padx=(5, 0))

        f3.pack(pady=(10, 20))

        self.folders = []
        self.files = []


    ################################################################################################
    def change_mode(self):
        if (self.nand_mode):
            self.nand_frame.pack_forget()
            self.chk.pack(padx=10, anchor=W)
            self.nand_mode = False

        else:
            if askokcancel('Warning', ('You are about to enter NAND mode. Do it only if you know '
                'what you are doing. Proceed?'), icon=WARNING):
                self.chk.pack_forget()
                self.nand_frame.pack(padx=10, pady=(0, 10), fill=X)
                self.nand_mode = True


    ################################################################################################
    def enable_entries(self, status):
        self.cid_label['state'] = (NORMAL if status else DISABLED)
        self.cid_entry['state'] = (NORMAL if status else DISABLED)
        self.console_id_label['state'] = (NORMAL if status else DISABLED)
        self.console_id_entry['state'] = (NORMAL if status else DISABLED)


    ################################################################################################
    def choose_nand(self):
        name = askopenfilename(filetypes=( ( 'nand.bin', '*.bin' ), ( 'DSi-1.mmc', '*.mmc' ) ))
        self.nand_file.set(name)

        self.nand_button['state'] = (NORMAL if name != '' else DISABLED)
        self.start_button['state'] = (NORMAL if name != '' else DISABLED)


    ################################################################################################
    def hiya(self):
        if not self.nand_mode:
            showinfo('Info', 'Now you will be asked to choose the SD card path that will be used '
                'for installing the custom firmware (or an output folder).\n\nIn order to avoid '
                'boot errors please assure it is empty before continuing.')
            self.sd_path = askdirectory()

            # Exit if no path was selected
            if self.sd_path == '':
                return

        # If adding a No$GBA footer, check if CID and ConsoleID values are OK
        elif self.nand_operation.get() == 1:
            cid = self.cid.get()
            console_id = self.console_id.get()

            # Check lengths
            if len(cid) != 32:
                showerror('Error', 'Bad eMMC CID')
                return

            elif len(console_id) != 16:
                showerror('Error', 'Bad Console ID')
                return

            # Parse strings to hex
            try:
                cid = bytearray.fromhex(cid)

            except ValueError:
                showerror('Error', 'Bad eMMC CID')
                return

            try:
                console_id = bytearray(reversed(bytearray.fromhex(console_id)))

            except ValueError:
                showerror('Error', 'Bad Console ID')
                return

        dialog = Toplevel(self)
        # Open as dialog (parent disabled)
        dialog.grab_set()
        dialog.title('Status')
        # Disable maximizing
        dialog.resizable(0, 0)

        frame = Frame(dialog, bd=2, relief=SUNKEN)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.log = ThreadSafeText(frame, bd=0, width=52, height=20,
            yscrollcommand=scrollbar.set)
        self.log.pack()

        scrollbar.config(command=self.log.yview)

        frame.pack()

        Button(dialog, text='Close', command=dialog.destroy, width=16).pack(pady=10)

        # Center in window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        dialog.geometry('%dx%d+%d+%d' % (width, height, root.winfo_x() + (root.winfo_width() / 2) -
            (width / 2), root.winfo_y() + (root.winfo_height() / 2) - (height / 2)))

        # Check if we'll be adding a No$GBA footer
        if self.nand_mode and self.nand_operation.get() == 1:
            Thread(target=self.add_footer, args=(cid, console_id)).start()

        else:
            Thread(target=self.check_nand).start()


    ################################################################################################
    def check_nand(self):
        self.log.write('Checking NAND file...')

        # Read the NAND file
        try:
            with open(self.nand_file.get(), 'rb') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Read the footer's header :-)
                bstr = f.read(0x10)

                if bstr == b'DSi eMMC CID/CPU':
                    # Read the CID
                    bstr = f.read(0x10)
                    self.cid.set(bstr.hex().upper())
                    self.log.write('- eMMC CID: ' + self.cid.get())

                    # Read the console ID
                    bstr = f.read(8)
                    self.console_id.set(bytearray(reversed(bstr)).hex().upper())
                    self.log.write('- Console ID: ' + self.console_id.get())

                    # Check we are removing the No$GBA footer
                    if self.nand_mode:
                        Thread(target=self.remove_footer).start()

                    else:
                        Thread(target=self.get_latest_hiyacfw).start()

                else:
                    self.log.write('ERROR: No$GBA footer not found')

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not open the file ' +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def get_latest_hiyacfw(self):
        # Try to use already downloaded HiyaCFW archive
        filename = 'HiyaCFW.7z'

        try:
            if path.isfile(filename):
                self.log.write('\nPreparing HiyaCFW...')

            else:
                self.log.write('\nDownloading latest HiyaCFW release...')

                conn = urlopen('https://api.github.com/repos/RocketRobz/hiyaCFW/releases/latest')
                latest = jsonify(conn.read().decode('utf-8'))
                conn.close()

                with urlopen(latest['assets'][0]
                    ['browser_download_url']) as src, open(filename, 'wb') as dst:
                    copyfileobj(src, dst)

            self.log.write('- Extracting HiyaCFW archive...')

            proc = Popen([ _7z, 'x', '-bso0', '-y', filename, 'for PC', 'for SDNAND SD card' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(filename)
                self.folders.append('for PC')
                self.folders.append('for SDNAND SD card')
                # Got to decrypt NAND if bootloader.nds is present
                Thread(target=self.decrypt_nand if path.isfile('bootloader.nds')
                    else self.extract_bios).start()

            else:
                self.log.write('ERROR: Extractor failed. Try installing/updating 7zip.')

        except (URLError, IOError) as e:
            print(e)
            self.log.write('ERROR: Could not get HiyaCFW')

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def extract_bios(self):
        self.log.write('\nExtracting ARM7/ARM9 BIOS from NAND...')

        try:
            proc = Popen([ twltool, 'boot2', '--in', self.nand_file.get() ])

            ret_val = proc.wait()

            if ret_val == 0:
                # Hash arm7.bin
                sha1_hash = sha1()

                with open('arm7.bin', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- arm7.bin SHA1:\n  ' +
                    sha1_hash.digest().hex().upper())

                # Hash arm9.bin
                sha1_hash = sha1()

                with open('arm9.bin', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- arm9.bin SHA1:\n  ' +
                    sha1_hash.digest().hex().upper())

                self.files.append('arm7.bin')
                self.files.append('arm9.bin')

                Thread(target=self.patch_bios).start()

            else:
                self.log.write('ERROR: Extractor failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def patch_bios(self):
        self.log.write('\nPatching ARM7/ARM9 BIOS...')

        try:
            self.patcher(path.join('for PC', 'bootloader files', 'bootloader arm7 patch.ips'),
                'arm7.bin')

            self.patcher(path.join('for PC', 'bootloader files', 'bootloader arm9 patch.ips'),
                'arm9.bin')

            # Hash arm7.bin
            sha1_hash = sha1()

            with open('arm7.bin', 'rb') as f:
                sha1_hash.update(f.read())

            self.log.write('- Patched arm7.bin SHA1:\n  ' +
                sha1_hash.digest().hex().upper())

            # Hash arm9.bin
            sha1_hash = sha1()

            with open('arm9.bin', 'rb') as f:
                sha1_hash.update(f.read())

            self.log.write('- Patched arm9.bin SHA1:\n  ' +
                sha1_hash.digest().hex().upper())

            Thread(target=self.arm9_prepend).start()

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not patch BIOS')
            Thread(target=self.clean, args=(True,)).start()

        except Exception as e:
            print(e)
            self.log.write('ERROR: Invalid patch header')
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def arm9_prepend(self):
        self.log.write('\nPrepending data to ARM9 BIOS...')

        try:
            with open('arm9.bin', 'rb') as f:
                data = f.read()

            with open('arm9.bin', 'wb') as f:
                with open(path.join('for PC', 'bootloader files',
                    'bootloader arm9 append to start.bin'), 'rb') as pre:
                    f.write(pre.read())

                f.write(data)

            # Hash arm9.bin
            sha1_hash = sha1()

            with open('arm9.bin', 'rb') as f:
                sha1_hash.update(f.read())

            self.log.write('- Prepended arm9.bin SHA1:\n  ' +
                sha1_hash.digest().hex().upper())

            Thread(target=self.make_bootloader).start()

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not prepend data to ARM9 BIOS')
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def make_bootloader(self):
        self.log.write('\nGenerating new bootloader...')

        exe = (path.join('for PC', 'bootloader files', 'ndstool') if sysname == 'Windows' else
            path.join(sysname, 'ndsblc'))

        try:
            proc = Popen([ exe, '-c', 'bootloader.nds', '-9', 'arm9.bin', '-7', 'arm7.bin', '-t',
                path.join('for PC', 'bootloader files', 'banner.bin'), '-h',
                path.join('for PC', 'bootloader files', 'header.bin') ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append('bootloader.nds')

                # Hash bootloader.nds
                sha1_hash = sha1()

                with open('bootloader.nds', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- bootloader.nds SHA1:\n  ' +
                    sha1_hash.digest().hex().upper())

                Thread(target=self.decrypt_nand).start()

            else:
                self.log.write('ERROR: Generator failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def decrypt_nand(self):
        self.log.write('\nDecrypting NAND...')

        try:
            proc = Popen([ twltool, 'nandcrypt', '--in', self.nand_file.get(), '--out',
                self.console_id.get() + '.img' ])

            ret_val = proc.wait()
            print("\n")

            if ret_val == 0:
                self.files.append(self.console_id.get() + '.img')

                Thread(target=self.win_extract_nand if sysname == 'Windows'
                    else self.extract_nand).start()

            else:
                self.log.write('ERROR: Decryptor failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def win_extract_nand(self):
        self.log.write('\nExtracting files from NAND...')

        try:
            proc = Popen([ _7z, 'x', '-bso0', '-y', self.console_id.get() + '.img', '0.fat' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append('0.fat')

                proc = Popen([ _7z, 'x', '-bso0', '-y', '-o' + self.sd_path, '0.fat' ])

                ret_val = proc.wait()

                if ret_val == 0:
                    Thread(target=self.get_launcher).start()

                else:
                    self.log.write('ERROR: Extractor failed')
                    Thread(target=self.clean, args=(True,)).start()

            else:
                self.log.write('ERROR: Extractor failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def extract_nand(self):
        self.log.write('\nExtracting files from NAND...')

        try:
            # DSi first partition offset: 0010EE00h
            proc = Popen([ fatcat, '-O', '1109504', '-x', self.sd_path,
                self.console_id.get() + '.img' ])

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.get_launcher).start()

            else:
                self.log.write('ERROR: Extractor failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def get_launcher(self):
        app = self.detect_region()

        # Stop if no supported region was found
        if not app:
            Thread(target=self.clean, args=(True,)).start()
            return

        # Check if unlaunch was installed on the NAND dump
        tmd = path.join(self.sd_path, 'title', '00030017', app, 'content', 'title.tmd')

        # If it is installed, set the files in the content folder as read-write
        if path.getsize(tmd) > 520:
            self.log.write('- WARNING: Unlaunch installed on the NAND dump')

            _dir = path.join(self.sd_path, 'title', '00030017', app, 'content')

            for file in listdir(_dir):
                file = path.join(_dir, file)

                if sysname == 'Darwin':
                    Popen([ 'chflags', 'nouchg', file ], stdout=DEVNULL, stderr=DEVNULL).wait()

                elif sysname == 'Linux':
                    Popen([ fatattr, '-R', file ], stdout=DEVNULL, stderr=DEVNULL).wait()

                else:
                    chmod(file, 438)

        # Delete title.tmd in case it does not get overwritten
        remove(tmd)

        # Try to use already downloaded launcher
        try:
            if path.isfile(self.launcher_region):
                self.log.write('\nPreparing ' + self.launcher_region + ' launcher...')

            else:
                self.log.write('\nDownloading ' + self.launcher_region + ' launcher...')

                with urlopen('https://raw.githubusercontent.com'
                    '/mondul/HiyaCFW-Helper/master/launchers/' +
                    self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                    copyfileobj(src, dst)

            self.log.write('- Decrypting launcher...')

            proc = Popen([ _7z, 'x', '-bso0', '-y', '-p' + app, self.launcher_region,
                '00000002.app' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(self.launcher_region)
                self.files.append('00000002.app')

                # Hash 00000002.app
                sha1_hash = sha1()

                with open('00000002.app', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- Patched launcher SHA1:\n  ' +
                    sha1_hash.digest().hex().upper())

                Thread(target=self.install_hiyacfw, args=(path.join(self.sd_path, 'title',
                    '00030017', app, 'content', '00000002.app'),)).start()

            else:
                self.log.write('ERROR: Extractor failed')
                Thread(target=self.clean, args=(True,)).start()

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not download ' + self.launcher_region + ' launcher')
            Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def install_hiyacfw(self, launcher_path):
        self.log.write('\nCopying HiyaCFW files...')

        copy_tree('for SDNAND SD card', self.sd_path, update=1)

        copyfile('bootloader.nds', path.join(self.sd_path, 'hiya', 'bootloader.nds'))

        # Check if exists before moving it
        if (path.exists(launcher_path)):
            # If exists then remove it to avoid move error
            remove(launcher_path)

        copyfile('00000002.app', launcher_path)

        Thread(target=self.get_latest_twilight if self.twilight.get() == 1 else self.clean).start()


    ################################################################################################
    def get_latest_twilight(self):
        filename = 'TWiLightMenu.7z'

        try:
            self.log.write('\nDownloading latest TWiLight Menu++ release...')

            conn = urlopen('https://api.github.com/repos/DS-Homebrew/TWiLightMenu/releases/'
                'latest')
            latest = jsonify(conn.read().decode('utf-8'))
            conn.close()

            with urlopen(latest['assets'][0]
                ['browser_download_url']) as src, open(filename, 'wb') as dst:
                copyfileobj(src, dst)

            self.log.write('- Extracting ' + filename[:-3] + ' archive...')

            proc = Popen([ _7z, 'x', '-bso0', '-y', filename, '_nds', 'DSi - CFW users',
                'DSi&3DS - SD card users', 'roms' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(filename)
                self.folders.append('DSi - CFW users')
                self.folders.append('_nds')
                self.folders.append('DSi&3DS - SD card users')
                self.folders.append('roms')
                Thread(target=self.install_twilight, args=(filename[:-3],)).start()

            else:
                self.log.write('ERROR: Extractor failed')
                Thread(target=self.clean, args=(True,)).start()

        except (URLError, IOError) as e:
            print(e)
            self.log.write('ERROR: Could not get TWiLight Menu++')
            Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def install_twilight(self, name):
        self.log.write('\nCopying ' + name + ' files...')

        copy_tree(path.join('DSi - CFW users', 'SDNAND root'), self.sd_path, update=1)
        copy_tree('_nds', path.join(self.sd_path, '_nds'))
        copy_tree('DSi&3DS - SD card users', self.sd_path, update=1)
        copy_tree('roms', path.join(self.sd_path, 'roms'))

        # Set files as read-only
        twlcfg0 = path.join(self.sd_path, 'shared1', 'TWLCFG0.dat')
        twlcfg1 = path.join(self.sd_path, 'shared1', 'TWLCFG1.dat')

        if sysname == 'Darwin':
            Popen([ 'chflags', 'uchg', twlcfg0, twlcfg1 ], stdout=DEVNULL, stderr=DEVNULL).wait()

        elif sysname == 'Linux':
            Popen([ fatattr, '+R', twlcfg0, twlcfg1 ], stdout=DEVNULL, stderr=DEVNULL).wait()

        else:
            chmod(twlcfg0, 292)
            chmod(twlcfg1, 292)

        Thread(target=self.clean).start()


    ################################################################################################
    def clean(self, err=False):
        self.log.write('\nCleaning...')

        while len(self.folders) > 0:
            rmtree(self.folders.pop(), ignore_errors=True)

        while len(self.files) > 0:
            try:
                remove(self.files.pop())

            except:
                pass

        if err:
            self.log.write('Done')
            return

        self.log.write('Done!\nEject your SD card and insert it into your DSi')


    ################################################################################################
    def patcher(self, patchpath, filepath):
        patch_size = path.getsize(patchpath)

        patchfile = open(patchpath, 'rb')

        if patchfile.read(5) != b'PATCH':
            patchfile.close()
            raise Exception()

        target = open(filepath, 'r+b')

        # Read First Record
        r = patchfile.read(3)

        while patchfile.tell() not in [ patch_size, patch_size - 3 ]:
            # Unpack 3-byte pointers.
            offset = self.unpack_int(r)
            # Read size of data chunk
            r = patchfile.read(2)
            size = self.unpack_int(r)

            if size == 0:  # RLE Record
                r = patchfile.read(2)
                rle_size = self.unpack_int(r)
                data = patchfile.read(1) * rle_size

            else:
                data = patchfile.read(size)

            # Write to file
            target.seek(offset)
            target.write(data)
            # Read Next Record
            r = patchfile.read(3)

        if patch_size - 3 == patchfile.tell():
            trim_size = self.unpack_int(patchfile.read(3))
            target.truncate(trim_size)

        # Cleanup
        target.close()
        patchfile.close()


    ################################################################################################
    def unpack_int(self, bstr):
        # Read an n-byte big-endian integer from a byte string
        ( ret_val, ) = unpack_from('>I', b'\x00' * (4 - len(bstr)) + bstr)
        return ret_val


    ################################################################################################
    def detect_region(self):
        REGION_CODES = {
            '484e4145': 'USA',
            '484e414a': 'JAP',
            '484e4150': 'EUR',
            '484e4155': 'AUS'
        }

        # Autodetect console region
        base = self.mounted if self.nand_mode else self.sd_path

        try:
            for app in listdir(path.join(base, 'title', '00030017')):
                for file in listdir(path.join(base, 'title', '00030017', app, 'content')):
                    if file.endswith('.app'):
                        try:
                            self.log.write('- Detected ' + REGION_CODES[app] + ' console NAND dump')
                            self.launcher_region = REGION_CODES[app]
                            return app

                        except KeyError:
                            self.log.write('ERROR: Unsupported console region')
                            return False

            self.log.write('ERROR: Could not detect console region')

        except OSError as e:
            self.log.write('ERROR: ' + e.strerror + ': ' + e.filename)

        return False


    ################################################################################################
    def encrypt_nand(self):
        self.log.write('\nEncrypting back NAND...')

        try:
            proc = Popen([ twltool, 'nandcrypt', '--in', self.console_id.get() + '.img' ])

            ret_val = proc.wait()
            print("\n")

            if ret_val == 0:
                Thread(target=self.clean).start()

            else:
                self.log.write('ERROR: Encryptor failed')

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def remove_footer(self):
        self.log.write('\nRemoving No$GBA footer...')

        file = self.console_id.get() + '-no-footer.bin'

        try:
            copyfile(self.nand_file.get(), file)

            # Back-up footer info
            with open(self.console_id.get() + '-info.txt', 'w') as f:
                f.write('eMMC CID: ' + self.cid.get() + '\r\n')
                f.write('Console ID: ' + self.console_id.get() + '\r\n')

            with open(file, 'r+b') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Remove footer
                f.truncate()

            self.log.write('\nDone!\nModified NAND stored as\n' + file +
                '\nStored footer info in ' + self.console_id.get() + '-info.txt')

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not open the file ' +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def add_footer(self, cid, console_id):
        self.log.write('Adding No$GBA footer...')

        file = self.console_id.get() + '-footer.bin'

        try:
            copyfile(self.nand_file.get(), file)

            with open(file, 'r+b') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Read the footer's header :-)
                bstr = f.read(0x10)

                # Check if it already has a footer
                if bstr == b'DSi eMMC CID/CPU':
                    self.log.write('ERROR: File already has a No$GBA footer')
                    f.close()
                    remove(file)
                    return

                # Go to the end of file
                f.seek(0, 2)
                # Write footer
                f.write(b'DSi eMMC CID/CPU')
                f.write(cid)
                f.write(console_id)
                f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

            self.log.write('\nDone!\nModified NAND stored as\n' + file)

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not open the file ' +
                path.basename(self.nand_file.get()))


####################################################################################################
# Entry point

print('Opening HiyaCFW Helper...')

sysname = system()

twltool = path.join(sysname, 'twltool' + ('.exe' if sysname == 'Windows' else ''))

print('Initializing GUI...')

root = Tk()

if not path.exists(twltool):
    root.withdraw()
    showerror('Error', 'TWLTool not found. Please make sure the ' + sysname +
        ' folder is at the same location as this script' + ('.' if sysname == 'Windows'
        else ", or run it again from the terminal:\n\n$ ./HiyaCFW_Helper.py"))
    root.destroy()
    exit(1)

elif sysname == 'Windows':
    from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY

    print('Searching for 7-Zip in the Windows registry...')

    try:
        with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip', 0, KEY_READ | KEY_WOW64_64KEY) as hkey:
            _7z = path.join(QueryValueEx(hkey, 'Path')[0], '7z.exe')

            if not path.exists(_7z):
                raise WindowsError

    except WindowsError:
        print('Searching for 7-Zip in the 32-bit Windows registry...')

        try:
            with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip') as hkey:
                _7z = path.join(QueryValueEx(hkey, 'Path')[0], '7z.exe')

                if not path.exists(_7z):
                    raise WindowsError

        except WindowsError:
            root.withdraw()
            showerror('Error', 'This script needs 7-Zip to run. Please install it.')
            root.destroy()
            exit(1)

else:   # Linux and MacOS
    fatcat = path.join(sysname, 'fatcat')
    _7z = path.join(sysname, '7za')

    if sysname == 'Linux':
        fatattr = path.join('Linux', 'fatattr')

root.title('HiyaCFW Helper v3.3')
# Disable maximizing
root.resizable(0, 0)
# Center in window
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
app = Application(master=root)
app.mainloop()
