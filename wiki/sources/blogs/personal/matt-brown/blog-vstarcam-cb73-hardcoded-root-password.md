---
source: matt-brown
source_url: https://brownfinesecurity.com/blog/vstarcam-cb73-hardcoded-root-password
title: "Uncovering Hardcoded Root Password in VStarcam CB73 Security Camera - Brown Fine Security"
---

# Uncovering Hardcoded Root Password in VStarcam CB73 Security Camera

I often get questions on how to get started in IoT pentesting or hardware hacking. My usual suggestion is just to grab a device, open it up, and dive in! Recently, I acquired an interesting security camera in my travels to Southeast Asia: the VStarcam CB73. I thought this camera would be an excellent target for reverse engineering and hunting for security vulnerabilities.

We can see in the image below that this is an extremely small camera, about 1 square inch in size.

This device connects to the internet using WiFi and uses a mobile application to interact with the camera. In fact one of the reasons I'm targeting this device is because in its marketing material it boasts being able to view the camera video feed and receive alerts from anywhere using the mobile application. This tells me that the device communicates with a cloud server somewhere. As a hacker, I LOVE it when devices have complexity. The more complex the device is, the larger the attack surface and the higher likelihood that I will find some cool vulnerabilities.

## Device Analysis

The first thing to do with any IoT device is to open it up and pull out all of the Printed Circuit Boards (PCBs) and other connected components. After taking out a couple screws, and prying open the outer casing, we are able to remove the main PCB and the battery.

On the top side of the device PCB we can see a micro USB connector, two switches (one for power, one for WiFi), A Chip labeled "Ingenic T31" hiding behind the camera, and a set of 4 test pads labeled "G", "R", "T", "N". The two things on this side of the board that interest me most are the T31 chip and the 4 labeled test pads.

With a bit of internet searching, we can read about the Ingenic T31 chip and understand it's a module that has a MIPS CPU, onboard memory, and video encoding capabilities all in a single silicon package.

However the most interesting part of the top of the PCB are the labeled test pads. To a seasoned IoT hacker, it was immediately obvious that these test pads were UART. UART is a serial communication protocol that is often used on Linux IoT devices to provide developers access to the device console for debugging purposes. We will return to this UART interface in a bit.

On the bottom side of the device PCB we see the WiFi module, an SDcard slot, and an 8-pin SPI flash chip. Here the flash chip, labeled "25QH64CHIQ", is clearly the most interesting item. This will be where the device firmware is stored.

## Firmware Extraction

Now that we have identified the SPI flash chip we will remove the chip from the PCB and read out the firmware so we can analyze it for security issues.

In order to remove the SPI flash chip, we will use a hot air rework station.

I usually set my hot air station temperature to 465 Celsius (869 Fahrenheit) and set the airspeed to somewhere in the middle range. Then blast the flash chip with hot air and be patient! we don't want to pull the chip off too fast and rip any of the pads that connect the chip to the PCB off the board.

Once the chip is off, we put it into our XGecu T56 universal programmer with the correctly sized socket.

Now with the SPI flash chip placed into the XGecu T56 we need to run its Windows-only Xgpro software. we can either run it directly on Windows or under Linux with the help of Wine. In Wine, we need to use a special DLL provided by radiomanV's [TL866 project on GitHub](https://github.com/radiomanV/TL866/tree/master/wine).

First we search for our flash chip in the "Search Device" menu.

Then we then perform the READ operation.

Finally, we save the file as "cb73fw.bin".

After we have successfully read the contents of the flash chip we use our hot air rework station to reattach the 8-pin SPI flash chip to the device PCB.

## UART Console

Now we turn our attention back to the UART interface we discovered on 4 test pads on the top side of the PCB.

First, while the device is powered on, we use a multimeter to measure the voltage by touching the black multimeter probe to the GND test pad (labeled as "G") and the red probe to either the TX test pad (labeled as "T") or VCC test pad (labeled as "N"). We read a voltage of 3.3v which is the most common UART voltage on Linux IoT devices. We will use a FTDI TTL-232R-3V3 cable to connect to our PC.

By reviewing the [TTL-232R-3V3 Datasheet](https://ftdichip.com/wp-content/uploads/2023/07/DS_TTL-232R_CABLES.pdf) we find the cable pinout shown below.

One thing to be aware of is that when connecting the TX and RX wires from a target device to the cable, the signals need to be reversed. So the TX from the device needs to connect to the RX on the cable, and visa versa. This gives us the following wire connections:

| Device Pad | UART Cable Pin | UART Cable Color | | ------------- | ------------- | ------------- | | TX | RX | Yellow | | RX | TX | Orange | | GND | GND | Black |

Now the question is: how do we get these 3 wires connected to those tiny test pads? First off, we don't need to connect specifically to the GND test pad, we can find a more convient spot on the board to connect to Ground. In our case, we decided to connect an alligator clip to the WiFi antenna.

This just leaves us with 2 test pads we need to connect to our UART adapter. One method would be to solder some small wires to the test pads. This requires us to have some decent soldering equipment and to be careful not to rip the test pads off the PCB. Instead, for this task we will use our PCBite probes. These probes have a small needle on the end that is spring-loaded. This allows us to carefully rest the probe on the test pad.

Now with our UART adapter plugged into our Linux computer, we run the following:

```
picocom -b 115200 /dev/ttyUSB0
```


Picocom is a terminal emulator that will allow us to send and receive serial data over our UART cable. 115200 is the most common baud rate (bits transmitted per second) that one will find on IoT devices. In this case, our guess turns out to be correct. "/dev/ttyUSB0" is where our USB device gets mapped to on our Linux computer.

Now that `picocom`

is running, we can power on our device and observe the Linux console log during boot up. I make a habit of copying all of the output of the UART console on device boot up into a text file for reviewing later.

```
U-Boot SPL 2013.07-00014-g7e49a25-dirty (Jul 15 2022 - 19:00:08)
[ ---------- TRUNCATED ---------- ]
U-Boot 2013.07 (Aug 30 2022 - 17:52:01)
[ ---------- TRUNCATED ---------- ]
Hit any key to stop autoboot: 0
the manufacturer 20
SF: Detected XM25QH64C
--->probe spend 4 ms
SF: 2097152 bytes @ 0x40000 Read: OK
--->read spend 675 ms
## Booting kernel from Legacy Image at 80600000 ...
Image Name: Linux-3.10.14__isvp_swan_1.0__
Image Type: MIPS Linux Kernel Image (lzma compressed)
Data Size: 1480678 Bytes = 1.4 MiB
Load Address: 80010000
Entry Point: 803283a0
Verifying Checksum ... OK
Uncompressing Kernel Image ... OK
[ ---------- TRUNCATED ---------- ]
veepai login:
```


Notice that the UART console after the system has fully booted prompts us for a login. Currently we don't have the username and password and therefore can not login.

## Bootloader Menu to Shell

After we allow the device to boot up once without interruption, we want to see if the bootloader allows us to enter its bootloader menu. To do this, we power the device off, hold down the enter key in our `picocom`

window, and then power the device on again. This causes the boot process to stop and enter the U-Boot bootloader menu:

```
[ ---------- TRUNCATED ---------- ]
Hit any key to stop autoboot: 0
isvp_t31#
isvp_t31#
isvp_t31#
```


In this bootloader menu we can run the `help`

command to show what commands are supported on a specific device. This is helpful because when device developers compile U-Boot they have many optional utilities that may or may not be included in any specific build.

```
isvp_t31# help
? - alias for 'help'
boot - boot default, i.e., run 'bootcmd'
boota - boot android system
bootd - boot default, i.e., run 'bootcmd'
bootm - boot application image from memory
bootp - boot image via network using BOOTP/TFTP protocol
chpart - change active partition
coninfo - print console devices and information
echo - echo args to console
env - environment handling commands
ethphy - ethphy contrl
fatinfo - print information about filesystem
fatload - load binary file from a dos filesystem
fatls - list files in a directory (default /)
getadc - get adc val elapsed,
gettime - get timer val elapsed,
go - start application at address 'addr'
help - print command description/usage
loadb - load binary file over serial line (kermit mode)
loads - load S-Record file over serial line
loady - load binary file over serial line (ymodem mode)
mmc - MMC sub system
mmcinfo - display MMC info
mtdparts- define flash/nand partitions
printenv- print environment variables
reset - Perform RESET of the CPU
run - run commands in an environment variable
saveenv - save environment variables to persistent storage
setenv - set environment variables
sf - SPI flash sub-system
sleep - delay execution for some time
source - run script from memory
tftpboot- boot image via network using TFTP protocol
version - print monitor, compiler and linker version
watchdog- open or colse the watchdog
```


The first command we will run will be the `printenv`

command. This will print out the currently loaded U-Boot environmental variables. When doing this we see the following output:

```
isvp_t31# printenv
adcthreshold=1240
baudrate=115200
bootargs=console=ttyS1,115200n8 quiet mem=42M@0x0 rmem=22M@0x2A00000 init=/linuxrc rootfstype=squashfs root=/dev/mtdblock2 rw mtdparts=jz_sfc:256k(boot),1536k(kernel),4608k(root),1792k(appfs),8m@0(all)
bootcmd=sf probe;sf read 0x80600000 0x40000 0x200000; bootm 0x80600000
bootdelay=1
ethact=Jz4775-9161
ethaddr=00:d0:d0:00:95:27
gatewayip=192.168.1.1
ipaddr=192.168.1.126
loads_echo=1
netmask=255.255.255.0
serverip=192.168.1.101
stderr=serial
stdin=serial
stdout=serial
Environment size: 537/16380 bytes
```


The main environmental variable that I am interested is `bootargs`

:

bootargs=console=ttyS1,115200n8 quiet mem=42M@0x0 rmem=22M@0x2A00000 init=/linuxrc rootfstype=squashfs root=/dev/mtdblock2 rw mtdparts=jz_sfc:256k(boot),1536k(kernel),4608k(root),1792k(appfs),8m@0(all)


Notice the part `init=/linuxrc`

of the bootargs variable. This parameter is telling the Linux kernel how to execute the [Init System](https://en.wikipedia.org/wiki/Init), which is the first process started by the Linux kernel after the system boots up. On this device. and most IoT devices, this init system is provided by BusyBox. This init system will perform various actions like mounting filesystems other than the root filesystem, and running the `login`

program on the UART console. We can modify the init system from `init=/linuxrc`

to `init=/bin/sh`

to drop into a shell on boot instead of the default init system. To do this, we use the following `setenv`

command:

```
setenv bootargs console=ttyS1,115200n8 quiet mem=42M@0x0 rmem=22M@0x2A00000 init=/bin/sh rootfstype=squashfs root=/dev/mtdblock2 rw mtdparts=jz_sfc:256k(boot),1536k(kernel),4608k(root),1792k(appfs),8m@0(all)
```


Then we run the `boot`

command to boot the device using our new environment variable:

```
isvp_t31# boot
the manufacturer 20
SF: Detected XM25QH64C
--->probe spend 4 ms
SF: 2097152 bytes @ 0x40000 Read: OK
--->read spend 675 ms
## Booting kernel from Legacy Image at 80600000 ...
Image Name: Linux-3.10.14__isvp_swan_1.0__
Image Type: MIPS Linux Kernel Image (lzma compressed)
Data Size: 1480678 Bytes = 1.4 MiB
Load Address: 80010000
Entry Point: 803283a0
Verifying Checksum ... OK
Uncompressing Kernel Image ... OK
Starting kernel ...
[ 0.000000] Initializing cgroup subsys cpu
[ 0.000000] Initializing cgroup subsys cpuacct
[ 0.000000] Linux version 3.10.14__isvp_swan_1.0__ (madong@vstarcam) (gcc version 4.7.2 (Ingenic r2.3.3 2016.12) ) #7 PREEMPT Tue Aug 30 16:11:27 CST 2022
[ 0.000000] bootconsole [early0] enabled
[ 0.000000] CPU0 RESET ERROR PC:DA64E93C
[ 0.000000] CPU0 revision is: 00d00100 (Ingenic Xburst)
[ 0.000000] FPU revision is: 00b70000
[ 0.000000] CCLK:1104MHz L2CLK:552Mhz H0CLK:250MHz H2CLK:250Mhz PCLK:125Mhz
[ 0.000000] Determined physical RAM map:
[ 0.000000] memory: 00429000 @ 00010000 (usable)
[ 0.000000] memory: 00037000 @ 00439000 (usable after init)
[ 0.093754] drivers/rtc/hctosys.c: unable to open rtc device (rtc0)
/bin/sh: can't access tty; job control turned off
/ #
```


We then have to run a few commands to get the /system partition mounted:

```
mount -t proc proc /proc
mount -t tmpfs tmpfs /dev
mount -a
echo /sbin/mdev > /proc/sys/kernel/hotplug
/sbin/mdev -s
mount -t jffs2 /dev/mtdblock3 /system
```


Lets take a look at the `/etc/passwd`

file:

```
~ # ls -l /etc/passwd
lrwxrwxrwx 1 1001 1001 20 Jun 16 2021 /etc/passwd -> /system/param/passwd
```


Notice that `/etc/passwd`

is a symlink to `/system/param/passwd`

. Why is it a symlink? Let's check the `mount`

command:

```
~ # mount
rootfs on / type rootfs (rw)
/dev/root on / type squashfs (ro,relatime)
proc on /proc type proc (rw,relatime)
tmpfs on /dev type tmpfs (rw,relatime)
tmpfs on /tmp type tmpfs (rw,relatime)
tmpfs on /run type tmpfs (rw,nosuid,nodev,relatime,mode=755)
sysfs on /sys type sysfs (rw,relatime)
/dev/mtdblock3 on /system type jffs2 (rw,relatime)
```


Notice that the first line showns us that the root filesystem, mounted on `/`

, is read-only. In fact another way we know this partition is read-only is because it is a SquashFS filesystem. SquashFS, by its design, can't be mounted with write permissions. So if the developers of the system want something to be writable that normally would live in the root filesystem, they instead make the file in the root filesystem a symlink to a writable file in the JFFS2 partition mounted on `/system`

.

We can now obtain the administrative user's password hash:

```
# cat /etc/passwd
vstarcam2017:uTV43RfKc73oM:0:0:Administrator:/:/bin/sh
```


I attempted to crack this password hash with hashcat against multiple wordlists without success:

```
echo 'uTV43RfKc73oM' > hash.txt
hashcat -m1500 hash.txt wordlist1.txt wordlist2.txt ...
```


Let's see if we can figure out the password another way...

## Firmware Analysis

We will now return to the firmware we read off of the SPI flash chip. Let's use `binwalk`

to extract any filesystems that we can from the firmware image:

```
$ binwalk -e cb73fw.bin
DECIMAL HEXADECIMAL DESCRIPTION
--------------------------------------------------------------------------------
48253 0xBC7D JBOOT STAG header, image id: 2, timestamp 0x1400A420, image size: 554991616 bytes, image JBOOT checksum: 0xA020, header JBOOT checksum: 0x400
125385 0x1E9C9 JBOOT STAG header, image id: 2, timestamp 0x18A3A200, image size: 682602496 bytes, image JBOOT checksum: 0xA400, header JBOOT checksum: 0x2127
127813 0x1F345 JBOOT STAG header, image id: 2, timestamp 0xB024318, image size: 4278207360 bytes, image JBOOT checksum: 0x620F, header JBOOT checksum: 0x432
129749 0x1FAD5 JBOOT STAG header, image id: 5, timestamp 0x250411FA, image size: 537010824 bytes, image JBOOT checksum: 0xBC00, header JBOOT checksum: 0x218F
164817 0x283D1 JBOOT STAG header, image id: 3, timestamp 0xA004918, image size: 553722640 bytes, image JBOOT checksum: 0x4018, header JBOOT checksum: 0x2B00
186521 0x2D899 JBOOT STAG header, image id: 3, timestamp 0xD006210, image size: 2148810752 bytes, image JBOOT checksum: 0x9980, header JBOOT checksum: 0x308F
190224 0x2E710 CRC32 polynomial table, little endian
194484 0x2F7B4 LZO compressed data
197912 0x30518 Android bootimg, kernel size: 0 bytes, kernel addr: 0x70657250, ramdisk size: 543519329 bytes, ramdisk addr: 0x6E72656B, product name: "mem boot start"
262144 0x40000 uImage header, header size: 64 bytes, header CRC: 0xC5F74AE8, created: 2022-08-30 08:11:32, image size: 1480678 bytes, Data Address: 0x80010000, Entry Point: 0x803283A0, data CRC: 0x42B2FB8A, OS: Linux, CPU: MIPS, image type: OS Kernel Image, compression type: lzma, image name: "Linux-3.10.14__isvp_swan_1.0__"
262208 0x40040 LZMA compressed data, properties: 0x5D, dictionary size: 67108864 bytes, uncompressed size: -1 bytes
1301640 0x13DC88 JBOOT STAG header, image id: 14, timestamp 0xEA9BD3FE, image size: 3424185437 bytes, image JBOOT checksum: 0x9F9A, header JBOOT checksum: 0xD67
1835008 0x1C0000 Squashfs filesystem, little endian, version 4.0, compression:xz, size: 4680592 bytes, 376 inodes, blocksize: 65536 bytes, created: 2022-04-08 13:34:09
6553612 0x64000C JFFS2 filesystem, little endian
6586448 0x648050 Zlib compressed data, compressed
6586552 0x6480B8 JFFS2 filesystem, little endian
6587300 0x6483A4 Zlib compressed data, compressed
[ ---------- TRUNCATED ---------- ]
```


Looking inside the `_cb73fw.bin.extracted`

directory that `binwalk`

created, we can see a large amount of file and directories.

```
$ ls -l _cb73fw.bin.extracted/
total 657080
-rw-r--r-- 1 nmatt nmatt 4680592 Jul 26 15:18 1C0000.squashfs
[ ---------- TRUNCATED ---------- ]
drwxr-xr-x 6 nmatt nmatt 4096 Jul 26 15:18 jffs2-root
drwxr-xr-x 6 nmatt nmatt 4096 Jul 26 15:18 jffs2-root-0
drwxr-xr-x 6 nmatt nmatt 4096 Jul 26 15:18 jffs2-root-1
drwxr-xr-x 6 nmatt nmatt 4096 Jul 26 15:18 jffs2-root-2
[ ---------- TRUNCATED ---------- ]
drwxr-xr-x 19 nmatt nmatt 4096 Jun 15 2021 squashfs-root
```


Some of these are duplicates and false positives. The items that stand out are the squashfs filesytstem (`_cb73fw.bin.extracted/squashfs-root/`

) and the first JFFS2 filesystem listed (`_cb73fw.bin.extracted/jffs2-root`

).

Looking inside the SquashFS filesystem, we see what looks like the Linux root filesystem:

```
$ ls -l _cb73fw.bin.extracted/squashfs-root/
total 68
drwxr-xr-x 3 nmatt nmatt 4096 Jun 15 2021 addfs
drwxr-xr-x 2 nmatt nmatt 4096 Jun 15 2021 bin
drwxr-xr-x 2 nmatt nmatt 4096 Jun 15 2021 dev
drwxr-xr-x 4 nmatt nmatt 4096 Jul 26 15:18 etc
drwxr-xr-x 5 nmatt nmatt 4096 Jun 15 2021 lib
lrwxrwxrwx 1 nmatt nmatt 11 Jun 15 2021 linuxrc -> bin/busybox
drwxr-xr-x 2 nmatt nmatt 4096 Jun 29 2021 media
drwxr-xr-x 6 nmatt nmatt 4096 Jun 15 2021 mnt
drwxr-xr-x 2 nmatt nmatt 4096 Jun 15 2021 opt
drwxr-xr-x 2 nmatt nmatt 4096 Jun 15 2021 proc
drwx------ 2 nmatt nmatt 4096 Jun 15 2021 root
drwxr-xr-x 2 nmatt nmatt 4096 Jun 15 2021 run
drwxr-xr-x 2 nmatt nmatt 4096 Jun 16 2021 sbin
drwxr-xr-x 2 nmatt nmatt 4096 Jun 15 2021 sys
drwxr-xr-x 2 nmatt nmatt 4096 Jun 15 2021 system
drwxr-xr-x 2 nmatt nmatt 4096 Jun 15 2021 tmp
drwxr-xr-x 6 nmatt nmatt 4096 Jun 15 2021 usr
drwxr-xr-x 4 nmatt nmatt 4096 Jun 15 2021 var
```


But remember, the `passwd`

file contents don't actually live in this read-only root filesystem. So now let's look in the JFFS2 filesystem:

```
$ ls -l _cb73fw.bin.extracted/jffs2-root
total 16
drwxr-xr-x 2 nmatt nmatt 4096 Jul 26 15:18 init
drwxr-xr-x 2 nmatt nmatt 4096 Jul 26 15:18 param
drwxr-xr-x 4 nmatt nmatt 4096 Jul 26 15:18 system
drwxr-xr-x 3 nmatt nmatt 4096 Jul 26 15:18 www
```


If we remember from above, the passwd file `/etc/passwd`

is symlinked to `/system/param/passwd`

and the JFFS2 filesystem is mounted onto `/system`

. This means we should find that same passwd file at `_cb73fw.bin.extracted/jffs2-root/param/passwd`

.

```
$ cat _cb73fw.bin.extracted/jffs2-root/param/passwd
vstarcam2017:uTV43RfKc73oM:0:0:Administrator:/:/bin/sh
```


OK, we see that same file. But is there something that generates the file? Since it's stored in the writable filesystem? Let's look around our extracted firmware for any references to `passwd`

.

```
$ sudo grep -r "/etc/passwd" _cb73fw.bin.extracted/
grep: _cb73fw.bin.extracted/jffs2-root/system/bin/encoder: binary file matches
grep: _cb73fw.bin.extracted/jffs2-root-63/system/bin/encoder: binary file matches
grep: _cb73fw.bin.extracted/jffs2-root-4/system/bin/encoder: binary file matches
[ ---------- TRUNCATED ---------- ]
```


Interestingly, there is a file `_cb73fw.bin.extracted/jffs2-root/system/bin/encoder`

with the string `/etc/passwd`

inside it. Taking a closer look at this file, we see it is a MIPS binary executable.

```
$ file _cb73fw.bin.extracted/jffs2-root/system/bin/encoder
_cb73fw.bin.extracted/jffs2-root/system/bin/encoder: ELF 32-bit LSB executable, MIPS, MIPS32 rel2 version 1 (SYSV), dynamically linked, interpreter /lib/ld-uClibc.so.0, stripped
```


## Reverse Engineering Root Password for Ghidra

Next, we will open this program up in Ghidra, a reverse engineering tool created and open sourced by the NSA. After opening the binary we are prompted to allow the tool to perform some initial analysis. We will stick with all the default analysis options.

Once Ghidra finishes its analysis of the binary, we navigate to `Search`

-> `For Strings...`

-> `Search`

. Then we filter for the string `/etc/passwd`

.

We see that this string is located in the binary at address 0x004ef7d0. By clicking on this string, the main Ghidra window navigates to that address where see a string reference labeled `s_/etc/passwd_004ef7d0`

. On this string we perform the following navigation: `right click`

-> `References`

-> `Show References to s_/etc/passwd_004ef7d0`

. This will search the binary for any code that references this string.

The results show a single reference to the string `/etc/passwd`

at address 0x0047bcdc. By clicking on this address, the main Ghidra window navigates to this assembly instruction that references the string and the corresponding function in the decompilation window.

The entire function decompiled by Ghidra is as follows:

```
void FUN_0047bcc4(void)
{
FILE *pFVar1;
uint __seed;
long lVar2;
char *pcVar3;
size_t sVar4;
undefined4 local_10c;
undefined4 local_108;
undefined4 local_104;
undefined2 local_100;
char local_fe;
undefined4 local_8c;
undefined4 local_88;
undefined local_84;
undefined auStack_83 [119];
char acStack_c [4];
pFVar1 = fopen("/etc/passwd","wb");
if (pFVar1 != (FILE *)0x0) {
memset(&local_10c,0,0x80);
local_8c = 0x37313032;
local_88 = 0x32313930;
local_84 = 0;
memset(auStack_83,0,0x77);
__seed = time((time_t *)0x0);
srandom(__seed);
lVar2 = random();
FUN_0047bc60(acStack_c,lVar2,2);
pcVar3 = crypt((char *)&local_8c,acStack_c);
sprintf((char *)&local_10c,"vstarcam2017:%s:0:0:Administrator:/:/bin/sh",pcVar3);
sVar4 = strlen((char *)&local_10c);
fwrite(&local_10c,1,sVar4,pFVar1);
fclose(pFVar1);
pFVar1 = fopen("/etc/group","wb");
if (pFVar1 != (FILE *)0x0) {
memset(&local_10c,0,0x80);
local_10c._0_1_ = 'r';
local_10c._1_1_ = 'o';
local_10c._2_1_ = 'o';
local_10c._3_1_ = 't';
local_108._0_1_ = ':';
local_108._1_1_ = 'x';
local_108._2_1_ = ':';
local_108._3_1_ = '0';
local_104._0_1_ = ':';
local_104._1_1_ = 'a';
local_104._2_1_ = 'd';
local_104._3_1_ = 'm';
local_100._0_1_ = 'i';
local_100._1_1_ = 'n';
local_fe = '\0';
sVar4 = strlen((char *)&local_10c);
fwrite(&local_10c,1,sVar4,pFVar1);
fclose(pFVar1);
}
}
return;
}
```


We can see in the highlighted lines above, the `/etc/passwd`

file is opened in write mode. Then a few local variables are set that look interesting. One reason they look interesting is because `local_8c`

is referenced as being sent into the `crypt()`

function which is responsible for producing password hashes. Another reason they look interesting is because although Ghidra shows us a hex representation of this data, a careful observer would notice that all that hex data is in the printable ASCII range. In fact these lines of code code be rewritten as the following:

```
local_8c = "7102";
local_88 = "2190";
local_84 = 0;
```


This clearly looks like a null terminated string. However we need to understand that there is an endianess issue at play. So by reversing the order of the two 4 byte strings, we get `2017`

and `0912`

.

**Wait a minute... The administrative username is vstarcam2017. Surely, the developers would not have choosen a password that is the date they were developing this device??**

Let's attempt to confirm our password with hashcat.

```
echo 'uTV43RfKc73oM' > hash.txt
echo '20170912' > passwd.txt
hashcat -m1500 hash.txt passwd.txt
```


**It cracks successfully!**

## UART Login as Root

Now all we have to do is power cycle the device, allow it to boot up normally and wait for the login prompt.

We provide the username `vstarcam2017`

and the password `20170912`

.

```
veepai login: vstarcam2017
Password:
Nov 28 15:35:16 login[65]: root login on 'console'
[vstarcam2017@veepai:~]# id
uid=0(vstarcam2017) gid=0(root) groups=0(root)
```


## Next Steps

Now that we have a full dump of the firmware and a root shell we have all the tools we need to start looking for software vulnerabilities in various network services running on the device. We can also check the security of the communications the device makes with cloud servers. These are a number of the risks that may get discovered during an IoT pentest.

### Need IoT Security Expertise?

Brown Fine Security provides expert IoT penetration testing to help secure your connected devices. From hardware analysis to cloud API testing, we uncover vulnerabilities before attackers do.

[Get a Free Consultation](/contact)

### Want to Learn IoT Hacking?

Ready to break into IoT security? Our hands-on training courses teach real-world hardware hacking, firmware analysis, and IoT exploitation techniques used by professional pentesters.

[Explore Training Courses](https://training.brownfinesecurity.com/)