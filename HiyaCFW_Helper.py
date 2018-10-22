#!/usr/bin/python

from Tkinter import (Tk, Frame, LabelFrame, PhotoImage, Button, Entry, Checkbutton, Radiobutton,
    Label, Toplevel, Scrollbar, Text, StringVar, IntVar, LEFT, RIGHT, W, X, Y, DISABLED, NORMAL,
    SUNKEN, END)
from tkMessageBox import showerror, askokcancel, WARNING
from tkFileDialog import askopenfilename
from platform import system
from os import path, remove, chmod, listdir, rename
from sys import exit, path as libdir
from threading import Thread
from Queue import Queue, Empty
from binascii import hexlify
from hashlib import sha1
from urllib2 import urlopen, URLError, Request
from urllib import urlretrieve
from json import loads as jsonify
from subprocess import Popen, PIPE
from struct import unpack_from
from re import search
from shutil import move, rmtree, copyfile
from distutils.dir_util import copy_tree

libdir.append('pyaes')

from pyaes import AESModeOfOperationCBC, Decrypter


####################################################################################################
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

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

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

        Radiobutton(self.nand_frame, text='Uninstall unlaunch or install v1.4 stable',
            variable=self.nand_operation, value=0,
            command=lambda: self.enable_entries(False)).pack(anchor=W)

        Radiobutton(self.nand_frame, text='Remove No$GBA footer', variable=self.nand_operation,
            value=1, command=lambda: self.enable_entries(False)).pack(anchor=W)

        Radiobutton(self.nand_frame, text='Add No$GBA footer', variable=self.nand_operation,
            value=2, command=lambda: self.enable_entries(True)).pack(anchor=W)

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

        self.nand_button['state'] = (NORMAL if self.nand_file.get() != '' else DISABLED)
        self.start_button['state'] = (NORMAL if self.nand_file.get() != '' else DISABLED)


    ################################################################################################
    def hiya(self):
        # If adding a No$GBA footer, check if CID and ConsoleID values are OK
        if self.nand_mode and self.nand_operation.get() == 2:
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
                cid = cid.decode('hex')

            except TypeError:
                showerror('Error', 'Bad eMMC CID')
                return

            try:
                console_id = bytearray(reversed(console_id.decode('hex')))

            except TypeError:
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
        if self.nand_mode and self.nand_operation.get() == 2:
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
                    self.cid.set(hexlify(bstr).upper())
                    self.log.write('- eMMC CID: ' + self.cid.get())

                    # Read the console ID
                    bstr = f.read(8)
                    self.console_id.set(hexlify(bytearray(reversed(bstr))).upper())
                    self.log.write('- Console ID: ' + self.console_id.get())

                    # Check we are making an unlaunch operation or removing the No$GBA footer
                    if self.nand_mode:
                        if self.nand_operation.get() == 0:
                            Thread(target=self.decrypt_nand).start()

                        else:
                            Thread(target=self.remove_footer).start()
                            pass

                    else:
                        Thread(target=self.get_latest_hiyacfw).start()

                else:
                    self.log.write('ERROR: No$GBA footer not found')

        except IOError:
            self.log.write('ERROR: Could not open the file ' +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def get_latest_hiyacfw(self):
        self.log.write('\nDownloading and extracting latest HiyaCFW release...')

        try:
            conn = urlopen('https://api.github.com/repos/RocketRobz/hiyaCFW/releases/latest')
            latest = jsonify(conn.read())
            conn.close()

            filename = urlretrieve(latest['assets'][0]['browser_download_url'])[0]

            exe = path.join(sysname, '7za')

            proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'for PC', 'for SDNAND SD card' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.folders.append('for PC')
                self.folders.append('for SDNAND SD card')
                self.files.append(filename)
                Thread(target=self.extract_bios).start()

            else:
                self.log.write('ERROR: Extractor failed')

        except (URLError, IOError) as e:
            self.log.write('ERROR: Could not get HiyaCFW')

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def extract_bios(self):
        self.log.write('\nExtracting ARM7/ARM9 BIOS from NAND...')

        exe = path.join(sysname, 'twltool')

        try:
            proc = Popen([ exe, 'boot2', '--in', self.nand_file.get() ])

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.patch_bios).start()

            else:
                self.log.write('ERROR: Extractor failed')

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def patch_bios(self):
        self.log.write('\nPatching ARM7/ARM9 BIOS...')

        try:
            self.patcher(path.join('for PC', 'bootloader files', 'bootloader arm7 patch.ips'),
                'arm7.bin')

            self.patcher(path.join('for PC', 'bootloader files', 'bootloader arm9 patch.ips'),
                'arm9.bin')

            self.files.append('arm7.bin')
            self.files.append('arm9.bin')
            Thread(target=self.arm9_prepend).start()

        except IOError:
            self.log.write('ERROR: Could not patch BIOS')

        except Exception:
            self.log.write('ERROR: Invalid patch header')


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

            Thread(target=self.make_bootloader).start()

        except IOError:
            self.log.write('ERROR: Could not prepend data to ARM9 BIOS')


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
                Thread(target=self.decrypt_nand).start()

            else:
                self.log.write('ERROR: Generator failed')

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def decrypt_nand(self):
        self.log.write('\nDecrypting NAND...')

        exe = path.join(sysname, 'twltool')

        try:
            proc = Popen([ exe, 'nandcrypt', '--in', self.nand_file.get(), '--out',
            	self.console_id.get() + '.img' ])

            ret_val = proc.wait()

            if ret_val == 0:
                if not self.nand_mode:
                    self.files.append(self.console_id.get() + '.img')

                Thread(target=self.mount_nand).start()

            else:
                self.log.write('ERROR: Decryptor failed')

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def mount_nand(self):
        self.log.write('\nMounting decrypted NAND...')

        try:
            if sysname == 'Windows':
                exe = osfmount

                cmd = [ osfmount, '-a', '-t', 'file', '-f', self.console_id.get() + '.img', '-m',
                    '#:', '-o', 'ro,rem' ]

                if self.nand_mode:
                    cmd[-1] = 'rw,rem'

                proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

                outs, errs = proc.communicate()

                if proc.returncode == 0:
                    self.mounted = search(r'[a-zA-Z]:\s', outs).group(0).strip()
                    self.log.write('- Mounted on drive ' + self.mounted)

                else:
                    self.log.write('ERROR: Mounter failed')
                    return

            elif sysname == 'Darwin':
                exe = 'hdiutil'

                cmd = [ exe, 'attach', '-imagekey', 'diskimage-class=CRawDiskImage', '-nomount',
                    self.console_id.get() + '.img' ]

                if not self.nand_mode:
                    cmd.insert(2, '-readonly')

                proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

                outs, errs = proc.communicate()

                if proc.returncode == 0:
                    self.raw_disk = search(r'^\/dev\/disk\d+', outs).group(0)
                    self.log.write('- Mounted raw disk on ' + self.raw_disk)

                    cmd = [ exe, 'mount', self.raw_disk + 's1' ]

                    if not self.nand_mode:
                        cmd.insert(2, '-readonly')

                    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

                    outs, errs = proc.communicate()

                    if proc.returncode == 0:
                        self.mounted = search(r'\/Volumes\/.+', outs).group(0)
                        self.log.write('- Mounted volume on ' + self.mounted)

                    else:
                        self.log.write('ERROR: Mounter failed')
                        return

                else:
                    self.log.write('ERROR: Mounter failed')
                    return

            else:  # Linux
                exe = 'losetup'

                cmd = [ exe, '-P', '-f', '--show', self.console_id.get() + '.img' ]

                if not self.nand_mode:
                    cmd.insert(2, '-r')

                proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                outs, errs = proc.communicate()

                if proc.returncode == 0:
                    self.loop_dev = search(r'\/dev\/loop\d+', outs).group(0)
                    self.log.write('- Mounted loop device on ' + self.loop_dev)

                    exe = 'mount'

                    self.mounted = '/mnt'

                    cmd = [ exe, '-t', 'vfat', self.loop_dev + 'p1', self.mounted ]

                    if not self.nand_mode:
                        cmd.insert(1, '-r')

                    proc = Popen(cmd)

                    ret_val = proc.wait()

                    if ret_val == 0:
                        self.log.write('- Mounted partition on ' + self.mounted)

                    else:
                        self.log.write('ERROR: Mounter failed')
                        return

                else:
                    self.log.write('ERROR: Mounter failed')
                    return

            # Check we are making an unlaunch operation
            Thread(target=self.unlaunch_proc if self.nand_mode else self.extract_nand).start()

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def extract_nand(self):
        self.log.write('\nExtracting files from NAND...')

        rmtree('out', ignore_errors=True)
        copy_tree(self.mounted, 'out')

        Thread(target=self.unmount_nand).start()


    ################################################################################################
    def unmount_nand(self):
        self.log.write('\nUnmounting NAND...')

        try:
            if sysname == 'Windows':
                exe = osfmount

                proc = Popen([ osfmount, '-D', '-m', self.mounted ])

            elif sysname == 'Darwin':
                exe = 'hdiutil'

                proc = Popen([ exe, 'detach', self.raw_disk ])

            else:  # Linux
                exe = 'umount'

                proc = Popen([ exe, self.mounted ])

                ret_val = proc.wait()

                if ret_val == 0:
                    exe = 'losetup'

                    proc = Popen([ exe, '-d', self.loop_dev ])

                else:
                    self.log.write('ERROR: Unmounter failed')
                    return

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.encrypt_nand if self.nand_mode else self.install_hiyacfw).start()

            else:
                self.log.write('ERROR: Unmounter failed')

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def install_hiyacfw(self):
        self.log.write('\nCopying HiyaCFW files...')

        copy_tree('for SDNAND SD card', 'out', update=1)
        move('bootloader.nds', path.join('out', 'hiya', 'bootloader.nds'))

        Thread(target=self.get_launcher).start()


    ################################################################################################
    def get_launcher(self):
        self.log.write('\nDownloading launcher...')

        HEADER = { 'User-Agent': 'Opera/9.50 (Nintendo; Opera/154; U; Nintendo DS; en)' }

        C_K = '\xAF\x1B\xF5\x16\xA8\x07\xD2\x1A\xEAE\x98O\x04t(a'

        app = self.detect_region()

        # Stop if no supported region was found
        if not app:
            return

        title_url = 'http://nus.cdn.t.shop.nintendowifi.net/ccs/download/00030017' + app + '/'

        # Download ticket to memory
        self.log.write('- Downloading ticket...')
        try:
            conn = urlopen(Request(title_url + 'cetk', None, HEADER));
            ticket_raw = conn.read()
            conn.close()

        except URLError:
            self.log.write('ERROR: Could not download ticket')
            return

        # Load encrypted title key
        encrypted_title_key = unpack_from('16s', ticket_raw, 0x1BF)[0]

        # Decrypt it
        iv = unpack_from('8s', ticket_raw, 0x1DC)[0].ljust(16, '\0')

        title_key = AESModeOfOperationCBC(C_K, iv).decrypt(encrypted_title_key)

        # Download TMD to memory
        self.log.write('- Downloading TMD...')
        try:
            conn = urlopen(Request(title_url + 'tmd.512', None, HEADER))
            tmd_raw = conn.read()
            conn.close()

        except URLError:
            self.log.write('ERROR: Could not download TMD')
            return

        # Load number of contents
        num_contents = unpack_from('>H', tmd_raw, 0x1DE)[0]

        # Read and download contents, decrypt and save them
        content_offset = 0x1E4

        for i in range(num_contents):
            content_id = hexlify(unpack_from('4s', tmd_raw, content_offset)[0])

            # Check if it is the content we are looking for
            if content_id != '00000002':
                content_offset += 36
                continue

            content_offset += 4

            iv = unpack_from('2s', tmd_raw, content_offset)[0].ljust(16, '\0')
            content_offset += 4

            content_size = unpack_from('>Q', tmd_raw, content_offset)[0]
            content_offset += 8

            content_hash = unpack_from('20s', tmd_raw, content_offset)[0]
            content_offset += 20

            # Download content
            self.log.write('- Downloading encrypted content...')
            try:
                conn = urlopen(Request(title_url + content_id, None, HEADER))
                content_raw = conn.read()
                conn.close()

            except URLError:
                self.log.write('ERROR: Could not download ' + content_id)
                return

            self.log.write('- Decrypting content...')
            decrypted_content = Decrypter(AESModeOfOperationCBC(title_key,
                iv)).feed(content_raw).ljust(content_size, '\xFF')

            sha1_hash = sha1()
            sha1_hash.update(decrypted_content)

            if sha1_hash.digest() == content_hash:
                self.log.write('- Saving 00000002.app...')

                self.launcher_file = path.join('out', 'title', '00030017', app, 'content',
                    '00000002.app')

                with open(self.launcher_file, 'wb') as f:
                    f.write(decrypted_content)

                Thread(target=self.decrypt_launcher).start()

            else:
                self.log.write('ERROR: Hash did not match, file not saved')

            return

        self.log.write('ERROR: No valid content found')


    ################################################################################################
    def decrypt_launcher(self):
        self.log.write('\nDecrypting launcher...')

        exe = path.join(sysname, 'twltool')

        try:
            proc = Popen([ exe, 'modcrypt', '--in', self.launcher_file ])

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.patch_launcher).start()

            else:
                self.log.write('ERROR: Decryptor failed')

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def patch_launcher(self):
        self.log.write('\nPatching launcher...')

        patch = path.join('for PC', 'v1.4 Launcher (00000002.app)' +
            (' (JAP-KOR)' if self.launcher_region == 'JAP' else '') + ' patch.ips')

        try:
            self.patcher(patch, self.launcher_file)

            Thread(target=self.get_latest_twilight if self.twilight.get() == 1
                else self.clean).start()

        except IOError:
            self.log.write('ERROR: Could not patch launcher')

        except Exception:
            self.log.write('ERROR: Invalid patch header')


    ################################################################################################
    def get_latest_twilight(self):
        self.log.write('\nDownloading and extracting latest')
        self.log.write('TWiLight Menu++ release...')

        try:
            conn = urlopen('https://api.github.com/repos/RocketRobz/TWiLightMenu/releases/latest')
            latest = jsonify(conn.read())
            conn.close()

            filename = urlretrieve(latest['assets'][0]['browser_download_url'])[0]

            exe = path.join(sysname, '7za')

            proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'Autoboot for HiyaCFW',
                'CFW - SDNAND root', 'DSiWare (' + self.launcher_region + ')', '_nds', 'roms',
                'BOOT.NDS' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.folders.append('Autoboot for HiyaCFW')
                self.folders.append('CFW - SDNAND root')
                self.folders.append('DSiWare (' + self.launcher_region + ')')
                self.files.append(filename)
                Thread(target=self.install_twilight).start()

            else:
                self.log.write('ERROR: Extractor failed')

        except (URLError, IOError) as e:
            self.log.write('ERROR: Could not get TWiLight Menu++')

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def install_twilight(self):
        self.log.write('\nCopying TWiLight Menu++ files...')

        copy_tree('CFW - SDNAND root', 'out', update=1)
        move('_nds', path.join('out', '_nds'))
        move('roms', path.join('out', 'roms'))
        move('BOOT.NDS', path.join('out', 'BOOT.NDS'))
        copy_tree('DSiWare (' + self.launcher_region + ')', path.join('out', 'roms', 'dsiware'),
            update=1)
        move(path.join('Autoboot for HiyaCFW', 'autoboot.bin'),
            path.join('out', 'hiya', 'autoboot.bin'))

        # Set files as read-only
        chmod(path.join('out', 'shared1', 'TWLCFG0.dat'), 292)
        chmod(path.join('out', 'shared1', 'TWLCFG1.dat'), 292)

        # Generate launchargs
        for app in listdir(path.join('out', 'title', '00030004')):
            try:
                for title in listdir(path.join('out', 'title', '00030004', app, 'content')):
                    if title.endswith('.app'):
                        with open(path.join('out', 'roms', 'dsiware', app + '.launcharg'),
                            'w') as launcharg:
                            launcharg.write('sd:/title/00030004/' + app + '/content/' + title)

            except:
                pass

        Thread(target=self.clean).start()


    ################################################################################################
    def clean(self):
        self.log.write('\nCleaning...')

        while len(self.folders) > 0:
            rmtree(self.folders.pop(), ignore_errors=True)

        while len(self.files) > 0:
            remove(self.files.pop())

        # Get logged user in Linux
        if sysname == 'Linux':
            from os import getlogin

            ug = getlogin()

        if (self.nand_mode):
            file = self.console_id.get() + self.suffix + '.bin'

            rename(self.console_id.get() + '.img', file)

            # Change owner of the file in Linux
            if sysname == 'Linux':
                Popen([ 'chown', '-R', ug + ':' + ug, file ]).wait()

            self.log.write('\nDone!\nModified NAND stored as\n' + file)
            return

        # Change owner of the out folder in Linux
        if sysname == 'Linux':
            Popen([ 'chown', '-R', ug + ':' + ug, 'out' ]).wait()

        self.log.write("\nDone!\nMove the contents of the out folder to your DSi's\nSD card")


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
        base = self.mounted if self.nand_mode else 'out'

        for app in listdir(path.join(base, 'title', '00030017')):
            for folder in listdir(path.join(base, 'title', '00030017', app)):
                if folder == 'data':
                    try:
                        self.log.write('- Detected ' + REGION_CODES[app] + ' console NAND dump')
                        self.launcher_region = REGION_CODES[app]
                        return app

                    except KeyError:
                        self.log.write('ERROR: Unsupported console region')
                        return False


    ################################################################################################
    def unlaunch_proc(self):
        self.log.write('\nChecking unlaunch status...')

        app = self.detect_region()

        # Stop if no supported region was found
        if not app:
            # TODO: Unmount NAND
            return

        tmd = path.join(self.mounted, 'title', '00030017', app, 'content', 'title.tmd')

        tmd_size = path.getsize(tmd)

        if tmd_size == 520:
            self.log.write('- Not installed. Downloading v1.4...')

            try:
                filename = urlretrieve('http://problemkaputt.de/unlau14.zip')[0]

                exe = path.join(sysname, '7za')

                proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'UNLAUNCH.DSI' ])

                ret_val = proc.wait()

                if ret_val == 0:
                    self.files.append(filename)
                    self.files.append('UNLAUNCH.DSI')

                    self.log.write('- Installing unlaunch...')

                    self.suffix = '-unlaunch'

                    with open(tmd, 'ab') as f:
                        with open('UNLAUNCH.DSI', 'rb') as unl:
                            f.write(unl.read())

                    # Set files as read-only
                    for file in listdir(path.join(self.mounted, 'title', '00030017', app,
                        'content')):
                        file = path.join(self.mounted, 'title', '00030017', app, 'content', file)

                        if sysname == 'Darwin':
                            Popen([ 'chflags', 'uchg', file ]).wait()

                        elif sysname == 'Linux':
                            Popen([ path.join('Linux', 'fatattr'), '+R', file ]).wait()
   
                        else:
                            chmod(file, 292)

                else:
                    self.log.write('ERROR: Extractor failed')
                    # TODO: Unmount NAND


            except IOError:
                self.log.write('ERROR: Could not get unlaunch')
                # TODO: Unmount NAND

            except OSError:
                self.log.write('ERROR: Could not execute ' + exe)
                # TODO: Unmount NAND

        else:
            self.log.write('- Installed. Uninstalling...')

            self.suffix = '-no-unlaunch'

            # Set files as read-write
            for file in listdir(path.join(self.mounted, 'title', '00030017', app, 'content')):
                file = path.join(self.mounted, 'title', '00030017', app, 'content', file)

                if sysname == 'Darwin':
                    Popen([ 'chflags', 'nouchg', file ]).wait()

                elif sysname == 'Linux':
                    Popen([ path.join('Linux', 'fatattr'), '-R', file ]).wait()
   
                else:
                    chmod(file, 438)

            with open(tmd, 'r+b') as f:
                f.truncate(520)

        Thread(target=self.unmount_nand).start()


    ################################################################################################
    def encrypt_nand(self):
        self.log.write('\nEncrypting back NAND...')

        exe = path.join(sysname, 'twltool')

        try:
            proc = Popen([ exe, 'nandcrypt', '--in', self.console_id.get() + '.img' ])

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.clean).start()

            else:
                self.log.write('ERROR: Encryptor failed')

        except OSError:
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def remove_footer(self):
        self.log.write('\nRemoving No$GBA footer...')

        file = self.console_id.get() + '-no-footer.bin'

        try:
            copyfile(self.nand_file.get(), file)

            # Back-up footer info
            with open(self.console_id.get() + '-info.txt', 'wb') as f:
                f.write('eMMC CID: ' + self.cid.get() + '\r\n')
                f.write('Console ID: ' + self.console_id.get() + '\r\n')

            with open(file, 'r+b') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Remove footer
                f.truncate()

            # Change owner of the file in Linux
            if sysname == 'Linux':
                from os import getlogin

                ug = getlogin()

                Popen([ 'chown', '-R', ug + ':' + ug, file ]).wait()

            self.log.write('\nDone!\nModified NAND stored as\n' + file +
                '\nStored footer info in ' + self.console_id.get() + '-info.txt')

        except IOError:
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
                    return;

                # Go to the end of file
                f.seek(0, 2)
                # Write footer
                f.write(b'DSi eMMC CID/CPU')
                f.write(cid)
                f.write(console_id)
                f.write('\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

            self.log.write('\nDone!\nModified NAND stored as\n' + file)

        except IOError:
            self.log.write('ERROR: Could not open the file ' +
                path.basename(self.nand_file.get()))


####################################################################################################

sysname = system()

root = Tk()

if sysname == 'Windows':
    from ctypes import windll
    from _winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE

    if windll.shell32.IsUserAnAdmin() == 0:
        root.withdraw()
        showerror('Error', 'This script needs to be run with administrator privileges.')
        root.destroy()
        exit(1)

    # Search for OSFMount in the Windows registry
    try:
        with OpenKey(HKEY_LOCAL_MACHINE,
            'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\OSFMount_is1') as hkey:

            osfmount = path.join(QueryValueEx(hkey, 'InstallLocation')[0], 'OSFMount.com')

            if not path.exists(osfmount):
                raise WindowsError

    except WindowsError:
        root.withdraw()
        showerror('Error', 'This script needs OSFMount to run. Please install it.')
        root.destroy()
        exit(1)

elif sysname == 'Linux':
    from os import getuid

    if getuid() != 0:
        root.withdraw()
        showerror('Error', 'This script needs to be run with sudo.')
        root.destroy()
        exit(1)

root.title('HiyaCFW Helper')
# Disable maximizing
root.resizable(0, 0)
# Center in window
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
app = Application(master=root)
app.mainloop()
