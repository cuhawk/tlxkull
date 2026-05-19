---
source: matt-brown
source_url: https://brownfinesecurity.com/blog/hanwha-firmware-file-decryption
title: "Reverse Engineering Hanwha Security Camera Firmware File Decryption with IDA Pro - Brown Fine Security"
---

# Reverse Engineering Hanwha Security Camera Firmware File Decryption with IDA Pro

I recently took a look at a commercial-grade IoT security camera made by Hanwha: the WiseNet XNF-8010RW. I wanted to perform a security audit of this device just like I would do during an IoT pentest.

The first thing I did was to disassemble the device and trace the UART console on an unpopulated ribbon cable connector.

Next, I dumped the device firmware by desoldering the BGA nand flash chip.

## The Encrypted Firmware File

Even though I had the firmware of my device, I thought it would be interesting to see if firmware was available on the company's website. [I was in luck!](https://hanwhavisionamerica.com/product/xnf-8010rw/)

I downloaded the `XNF-8010R_2.10.04_20230328_R640.zip`

file and unzipped it. This resulted in the file `XNF-8010R_2.10.04_20230328_R640.img`

.

By running the `file`

command on this firmware file, I could determine right away that it is encrypted via openssl.

```
$ file XNF-8010R_2.10.04_20230328_R640.img
XNF-8010R_2.10.04_20230328_R640.img: openssl enc'd data with salted password
```


How does the `file`

command know this is encrypted with `openssl`

? It's all in the file header:

```
$ xxd XNF-8010R_2.10.04_20230328_R640.img | head -n5
00000000: 5361 6c74 6564 5f5f 95e9 1365 22a5 73f1 Salted__...e".s.
00000010: dcc2 fda7 37f3 8b52 a3cf 241a ce25 212a ....7..R..$..%!*
00000020: a619 033a 68fa 85a0 3b94 8e9f 1db2 5eb9 ...:h...;.....^.
00000030: 5531 12fc feb4 8062 e299 7ad7 289c fa13 U1.....b..z.(...
00000040: 8b2e bade b5a1 0aaa 4967 f099 143d 8e4d ........Ig...=.M
```


That `Salted__`

string at the beginning is a dead giveaway.

Now the million dollar question is: **What's the encryption password?**

## The Chicken and Egg Problem

We are presented with a dilemma. The password to decrypt the firmware file is contained somewhere inside the firmware itself.

But let's think about that... The decryption password needs to be somewhere on the running device in order to decrypt the firmware file and apply the upgrade.

Luckily we already performed the beginning steps to break out of our chicken and egg-style dilemma. We've already dumped the firmware from the physical device! Let's dig into the firmware dump.

## Firmware Analysis

We performed a chip-off firmware extraction of a BGA Nand flash chip on the camera. If you watched the video embedded above, you will remember that our Nand flash chip contained spare area. We dumped the firmware twice: once including and once excluding that spare area from the firmware dump file. For our analysis, we are going to use the version without the spare area include. We will name this file `wisenet-nospare.bin`

.

The first thing we want to do with this firmware file is to split it up into the various partitions that exist. You may recall that we saw the partition table addresses nicely printed out in the UART logs:

We can then use `dd`

to split the single files into all of the partitions with the following bash script:

```
#!/bin/bash
dd if=wisenet-nospare.bin of=partitions/part1.bin bs=1 skip=0 count=1572864
dd if=wisenet-nospare.bin of=partitions/part2.bin bs=1 skip=1572864 count=524288
dd if=wisenet-nospare.bin of=partitions/part3.bin bs=1 skip=2097152 count=524288
dd if=wisenet-nospare.bin of=partitions/part4.bin bs=1 skip=2621440 count=4194304
dd if=wisenet-nospare.bin of=partitions/part5.bin bs=1 skip=6815744 count=6291456
dd if=wisenet-nospare.bin of=partitions/part6.bin bs=1 skip=13107200 count=6291456
dd if=wisenet-nospare.bin of=partitions/part7.bin bs=1 skip=19398656 count=20971520
dd if=wisenet-nospare.bin of=partitions/part8.bin bs=1 skip=40370176 count=104857600
dd if=wisenet-nospare.bin of=partitions/part9.bin bs=1 skip=145227776 count=68157440
dd if=wisenet-nospare.bin of=partitions/part10.bin bs=1 skip=213385216 count=4194304
dd if=wisenet-nospare.bin of=partitions/part11.bin bs=1 skip=217579520 count=4194304
dd if=wisenet-nospare.bin of=partitions/part12.bin bs=1 skip=221773824 count=20971520
dd if=wisenet-nospare.bin of=partitions/part13.bin bs=1 skip=242745344 count=17301504
dd if=wisenet-nospare.bin of=partitions/part14.bin bs=1 skip=260046848 count=4194304
dd if=wisenet-nospare.bin of=partitions/part15.bin bs=1 skip=264241152 count=4194304
```


Next, we want to find where in the firmware the decryption is likely occurring. The only lead we currently have is the openssl is being used, but this actually tells us a lot. Our current hypothesis is that the `openssl enc`

command is being used. Let's start with strings!

### "openssl" String Analysis

```
$ strings partitions/* | grep "openssl "
strings: Warning: 'partitions/extractions' is a directory
openssl version
failed to initialize TLS servername callback, openssl library does not support TLS servername extension
openssl version
openssl rsautl -decrypt -inkey %s -in %s -out %s
openssl enc -d -aes-256-cbc -md md5 -in %s -out %s -pass file:%s
openssl enc -d -aes-256-cbc -md md5 -salt -in %s -out %s -k %s
openssl enc -d -aes-256-cbc -md sha256 -salt -in %s -out %s -k %s
openssl version
openssl x509 -noout -subject -in
openssl verify -verbose -CAfile
openssl x509 -pubkey -noout -in
openssl dgst -sha256 -verify
openssl req -x509
openssl enc -aes-256-cbc -md sha256 -salt -in %s.key -out %s.key -k %s
openssl enc -aes-256-cbc -md sha256 -salt -in %s.crt -out %s.crt -k %s
openssl enc -aes-256-cbc -md md5 -salt -in %s -out %s -k %s
openssl dgst -sha256 -verify %s -signature %s %s
openssl enc -aes-256-cbc -d -k
openssl version
openssl version
```


Here there are a couple of interesting strings. These are the ones we should focus on:

```
openssl rsautl -decrypt -inkey %s -in %s -out %s
openssl enc -aes-256-cbc -d -k
```


Both of those strings are performing decryption of a file with `openssl`

. The first one is using a keyfile and the second is using a password. We expect a password so let's look at what strings are before and after that string.

First we ID the partition that has the `openssl enc -aes-256-cbc -d -k `

string:

```
$ grep -r 'openssl enc -aes-256-cbc -d -k ' partitions/
grep: partitions/part8.bin: binary file matches
```


then we look at the adjacent strings:

```
$ strings partitions/part8.bin | grep -A10 -B10 "openssl enc -aes-256-cbc -d -k"
kill -9 `pidof %s` > /dev/null 2>&1
kill process :
/work/app/fwupgrader &
cp /mnt/install/fwupgrader /mirror_work/
cp /work/app/fwupgrader /mirror_work/
/mirror_work/fwupgrader &
umount /mnt/install
mount tmpfs /mnt/install -t tmpfs -o size=
free -m
rm -rf /mnt/install/*
openssl enc -aes-256-cbc -d -k
ls /mnt/install
rm -rf
sha256sum
| cut -c1-64 >
gunzip <
| tar xvpf - -C
php-cgi
agentx
snmpd
dhcp6c
```


Well look at that! We see mentions of `fwupgrader`

all around the openssl string.

### "decryption" String Analysis

We also find some interesting strings when looking for the term "decryption":

```
$ strings wisenet-nospare.bin | grep -i decryption
...
122,MODELINFO_MODEL_DECRYPTIONKEY,ZK5EA1tGT4AHOUCUU5tUMuQCfA2fbjnSEgOiLR104eI=,const char*
122,MODELINFO_MODEL_DECRYPTIONKEY,ZK5ECtTH+jkYs87uEEUrwyZ9+wsFkWpk3AbtnTEY3gs=,const char*
122,MODELINFO_MODEL_DECRYPTIONKEY,ZK5EA1tGT4AHOUCUU5tUMuQCfA2fbjnSEgOiLR104eI=,const char*
122,MODELINFO_MODEL_DECRYPTIONKEY,ZK5EA1tGT4AHOUCUU5tUMuQCfA2fbjnSEgOiLR104eI=,const char*
...
```


When we use `strings wisenet-nospare.bin | less`

and search around the area, we see "MODELINFO_MODEL_DECRYPTIONKEY" referenced. We find more interesting strings in a similar structure:

```
modelinfo_XNF-8010R
0,MODELINFO_FEATURE_NUM,MF_CXF,MODEL_FEATURE
1,MODELINFO_AUX_COUNT,0,int
2,MODELINFO_BACKEND_VA,BACKEND_MD | BACKEND_TD | BACKEND_DF | BACKEND_DA,BACKND_VA_MASK_E
3,MODELINFO_CONFIG_BACKUP_KEY,dCTjgwaXvsPzQ0QRlweM7IP7T0ytT7G25rEM4g+17cQ=,const char*
...
119,MODELINFO_MAX_VIDEO_PACKET_SIZE,4587520,int
120,MODELINFO_SNMP_MODEL_OID,404,int
121,MODELINFO_NO_SUPPORT_EXTERNAL_DN,0,int
122,MODELINFO_MODEL_DECRYPTIONKEY,ZK5EA1tGT4AHOUCUU5tUMuQCfA2fbjnSEgOiLR104eI=,const char*
123,MODELINFO_DEFAULT_SMARTCODEC_LEVEL,1,int
```


We seem to have stumbled onto some sort of database. Let's gather up all of those keys for later:

```
$ strings wisenet-nospare.bin | grep "MODELINFO_CONFIG_BACKUP_KEY\|MODELINFO_MODEL_DECRYPTIONKEY" | sort | uniq
122,MODELINFO_MODEL_DECRYPTIONKEY,ZK5EA1tGT4AHOUCUU5tUMuQCfA2fbjnSEgOiLR104eI=,const char*
122,MODELINFO_MODEL_DECRYPTIONKEY,ZK5ECtTH+jkYs87uEEUrwyZ9+wsFkWpk3AbtnTEY3gs=,const char*
3,MODELINFO_CONFIG_BACKUP_KEY,dCTjgwaXvsPzFQeOg5gg6+uMOKSuoreXJ/o3UsgJY+o=,const char*
3,MODELINFO_CONFIG_BACKUP_KEY,dCTjgwaXvsPzFUpdPq8wCPu5bGNwygQ7fFBQp+bM+As=,const char*
3,MODELINFO_CONFIG_BACKUP_KEY,dCTjgwaXvsPzQ0QRlweM7IP7T0ytT7G25rEM4g+17cQ=,const char*
3,MODELINFO_CONFIG_BACKUP_KEY,fc7pA9zD9Qa3+CUjr4w5AglNX9LT3SihkH2mENLyYNc=,const char*
```


## Carving ELF Binaries with Binwalk

We know that our `openssl`

call occurs within partition 8. Let's use binwalk to carve only ELF binaries out of that partition binary file:

```
$ binwalk -c -yelf part8.bin
```


This results in the following binary files:

```
$ ls -l extractions/
total 102432
-rw-r--r-- 1 nmatt nmatt 4096 Jun 3 00:57 part8.bin_0_unknown.raw
-rw-r--r-- 1 nmatt nmatt 159744 Jun 3 00:57 part8.bin_10080256_elf.raw
-rw-r--r-- 1 nmatt nmatt 153600 Jun 3 00:57 part8.bin_10240000_elf.raw
-rw-r--r-- 1 nmatt nmatt 462848 Jun 3 00:57 part8.bin_10393600_elf.raw
-rw-r--r-- 1 nmatt nmatt 4499456 Jun 3 00:57 part8.bin_10856448_elf.raw
-rw-r--r-- 1 nmatt nmatt 1253376 Jun 3 00:57 part8.bin_1316864_elf.raw
-rw-r--r-- 1 nmatt nmatt 143360 Jun 3 00:57 part8.bin_15355904_elf.raw
-rw-r--r-- 1 nmatt nmatt 657408 Jun 3 00:57 part8.bin_15499264_elf.raw
-rw-r--r-- 1 nmatt nmatt 5339136 Jun 3 00:57 part8.bin_16156672_elf.raw
-rw-r--r-- 1 nmatt nmatt 14336 Jun 3 00:57 part8.bin_21495808_elf.raw
-rw-r--r-- 1 nmatt nmatt 11677696 Jun 3 00:57 part8.bin_21510144_elf.raw
-rw-r--r-- 1 nmatt nmatt 624640 Jun 3 00:57 part8.bin_2570240_elf.raw
-rw-r--r-- 1 nmatt nmatt 2437120 Jun 3 00:57 part8.bin_3194880_elf.raw
-rw-r--r-- 1 nmatt nmatt 16384 Jun 3 00:57 part8.bin_33187840_elf.raw
-rw-r--r-- 1 nmatt nmatt 7266304 Jun 3 00:57 part8.bin_33204224_elf.raw
-rw-r--r-- 1 nmatt nmatt 1282048 Jun 3 00:57 part8.bin_34816_elf.raw
-rw-r--r-- 1 nmatt nmatt 608256 Jun 3 00:57 part8.bin_40470528_elf.raw
-rw-r--r-- 1 nmatt nmatt 30720 Jun 3 00:57 part8.bin_4096_elf.raw
-rw-r--r-- 1 nmatt nmatt 24576 Jun 3 00:57 part8.bin_41078784_elf.raw
-rw-r--r-- 1 nmatt nmatt 677888 Jun 3 00:57 part8.bin_41103360_elf.raw
-rw-r--r-- 1 nmatt nmatt 505856 Jun 3 00:57 part8.bin_41781248_elf.raw
-rw-r--r-- 1 nmatt nmatt 722944 Jun 3 00:57 part8.bin_42287104_elf.raw
-rw-r--r-- 1 nmatt nmatt 14606336 Jun 3 00:57 part8.bin_43010048_elf.raw
-rw-r--r-- 1 nmatt nmatt 1001472 Jun 3 00:57 part8.bin_5632000_elf.raw
-rw-r--r-- 1 nmatt nmatt 40960 Jun 3 00:57 part8.bin_57616384_elf.raw
-rw-r--r-- 1 nmatt nmatt 47200256 Jun 3 00:57 part8.bin_57657344_elf.raw
-rw-r--r-- 1 nmatt nmatt 3446784 Jun 3 00:57 part8.bin_6633472_elf.raw
```


Next, it's a simple process to determine which binary has our string:

```
$ grep -r 'openssl enc -aes-256-cbc -d -k ' extractions/
grep: extractions/part8.bin_21510144_elf.raw: binary file matches
```


## Binary Reverse Engineering via IDA Pro

Now we can load `part8.bin_21510144_elf.raw`

into Ida Pro for analysis. It recognizes it as a ARM Little-endian binary. We keep all the default analysis options enabled and select "OK" to start.

The analysis takes a few minutes to complete. Then the first thing we want to do is look for our string that led us to this binary initially.

Navigation: View -> Open subviews -> Strings


We found our string and navigated to its address.

Navigation: Right Click on "aOpensslEncAes2_2" -> List cross references to...


Here we can see that the reference to this string is in a function called `decrypt_imageFile`

! We are on the right track.

After navigating to the decrypt_imageFile and running the decompiler we can see that a function `get_modelStr`

is passed two arguments. The first argument is 122 and the second is a buffer.

That number 122 looks familiar...

Remember this:

```
122,MODELINFO_MODEL_DECRYPTIONKEY,ZK5EA1tGT4AHOUCUU5tUMuQCfA2fbjnSEgOiLR104eI=,const char*
```


It clearly seems like it's referencing that `MODELINFO_MODEL_DECRYPTIONKEY`

! Let's try to decrypt! We will try all of the `MODELINFO_MODEL_DECRYPTIONKEY`

and `MODELINFO_CONFIG_BACKUP_KEY`

values we found to be sure.

```
#!/bin/bash
pass_list=("ZK5EA1tGT4AHOUCUU5tUMuQCfA2fbjnSEgOiLR104eI=" "ZK5ECtTH+jkYs87uEEUrwyZ9+wsFkWpk3AbtnTEY3gs=" "dCTjgwaXvsPzQ0QRlweM7IP7T0ytT7G25rEM4g+17cQ=" "dCTjgwaXvsPzFQeOg5gg6+uMOKSuoreXJ/o3UsgJY+o=" "dCTjgwaXvsPzFUpdPq8wCPu5bGNwygQ7fFBQp+bM+As=" "dCTjgwaXvsPzQ0QRlweM7IP7T0ytT7G25rEM4g+17cQ=" "fc7pA9zD9Qa3+CUjr4w5AglNX9LT3SihkH2mENLyYNc=")
# we need to try all of these since the camera might have a different default digest than our machine
digest_list=("md5" "sha1" "sha256" "sha384" "sha512")
fwfile="XNF-8010R_2.10.04_20230328_R640.img"
outdir="out"
mkdir -p $outdir
rm -rf ${outdir}/*
count=0
for pass in "${pass_list[@]}"; do
for digest in "${digest_list[@]}"; do
openssl enc -aes-256-cbc -d -md ${digest} -k "${pass}" -in ${fwfile} -out ${outdir}/try${count}_${digest}.bin
done
((count++))
done
```


That didn't work. All of those passwords and digest method combinations give us the same error:

```
*** WARNING : deprecated key derivation used.
Using -iter or -pbkdf2 would be better.
bad decrypt
80CB45AA4A7F0000:error:1C800064:Provider routines:ossl_cipher_unpadblock:bad decrypt:providers/implementations/ciphers/ciphercommon_block.c:107:
```


## We Need to Go Deeper

So clearly something else is at play. Let's look at one of those `MODELINFO_MODEL_DECRYPTIONKEY`

values:

```
$ echo ZK5ECtTH+jkYs87uEEUrwyZ9+wsFkWpk3AbtnTEY3gs= | base64 -d | xxd
00000000: 64ae 440a d4c7 fa39 18b3 ceee 1045 2bc3 d.D....9.....E+.
00000010: 267d fb0b 0591 6a64 dc06 ed9d 3118 de0b &}....jd....1...
```


Every "decryption key" value is 32 bytes when base64 decoded and seemingly random (high entropy). It's possible the decryption keys are themselves encrypted.

Let's follow get_modelStr() down a chain of wrapper functions.

UtilityWrapper::get_modelStr() -> Sysinfo::get_modelStr() -> SysinfoManager::get_featureData()


We are led to the `get_featureData`

function which makes reference to a global variable `unk_B6B250`

.

Looking at the cross-references to this `unk_B6B250`

global variable, we find that its used by three functions:

- get_featureData()
- set_featureData()
- replace_featureData()

The `replace_featureData`

function looks interesting. Why would we ever want to replace that data? Let's find out.

Looking at the cross-references to `replace_featureData`

, we find exactly what we are looking for: a function named `decrypt_modelfeature`

.

### decrypt_modelfeature() Function

This function is clearly the place that those encrypted + base64-encoded strings will be decrypted. Let's walk through the major parts of this function.

First, we see the string "zeppelin" be constructed into a string. Let's call this buffer `zeppelin_buff`

for now. This seems like the making of a hardcoded password...

Then we see the `HashedKeyCipher(out_buffer,1,6,zeppelin_buff)`

constructor called. So we are hashing the "zeppelin" string but with what function? We'll dig into that later.

Next we call `Utility::Security::HashedKeyCipher::get_decryptor`

on that object that was returned from the last call. So those arguments have a lot of weight in determining how things get decrypted.

### HashedKeyCipher() Constuctor

Down inside the constructor we eventually see a call like this in the decompiler:

```
hash = Utility::Security::HashFactory::create_hash(1);
```


Stepping into the create_hash() function we get the following decompilation:

```
HashSha256 *__fastcall Utility::Security::HashFactory::create_hash(int a1)
{
HashSha256 *v1; // r5
if ( a1 )
{
if ( a1 == 1 )
{
v1 = (HashSha256 *)operator new(4u);
HashSha256::HashSha256(v1);
}
else
{
return 0;
}
}
else
{
v1 = (HashSha256 *)operator new(0x5Cu);
HashMd5::HashMd5(v1);
}
return v1;
}
```


First problem solved! The hash function used to hash the key is Sha256.

Next we see a line like this:

```
decryptor = Utility::Security::DecryptorFactory::create_decryptor(*(_DWORD *)(a1 + 52), v4, 32);
```


A bit up in the code we notice that the `*(_DWORD *)(a1 + 52)`

is loaded with the 3rd argument of the `HashedKeyCipher`

constructor which was 6.

Here is the start of the `create_decryptor`

function:

```
Utility::Security::Seed128_Decryptor *__fastcall Utility::Security::DecryptorFactory::create_decryptor(
int a1,
int a2,
int a3,
int a4,
int a5)
{
Utility::Security::Seed128_Decryptor *v9; // r10
int v10; // r2
Utility::Security::Seed128_Decryptor *v11; // r0
switch ( a1 )
{
case 0:
v9 = (Utility::Security::Seed128_Decryptor *)operator new(8u);
Utility::Security::Seed128_Decryptor::Seed128_Decryptor(v9);
goto LABEL_3;
case 4:
v9 = (Utility::Security::Seed128_Decryptor *)operator new(8u);
Utility::Security::Aes128CBC_Decryptor::Aes128CBC_Decryptor(v9);
goto LABEL_3;
case 5:
v9 = (Utility::Security::Seed128_Decryptor *)operator new(8u);
Utility::Security::Aes256CBC_Decryptor::Aes256CBC_Decryptor(v9);
goto LABEL_3;
case 6:
v9 = (Utility::Security::Seed128_Decryptor *)operator new(0x10u);
Utility::Security::Aes256CFB8_Decryptor::Aes256CFB8_Decryptor(v9);
goto LABEL_3;
case 7:
v9 = (Utility::Security::Seed128_Decryptor *)operator new(4u);
Utility::Security::Aes128CBCTTA_Decryptor::Aes128CBCTTA_Decryptor(v9);
```


So now we can identify that the AES-256-CFB8 cipher is being used.

## Decrypting the Encryption Passphrase

Now we have all of the moving pieces we need to begin. The following bash script will perform the following actions:

- perform a sha256 hash of the string "zeppelin" to obtain the AES key
- loop over all ciphertext (encrypted passphrases) we found in the firmware blob
- set the IV to all zeros
- attempt to decrypt using the AES-256-CFB8 cipher

```
#!/bin/bash
key=$(echo -n zeppelin | sha256sum | awk '{print $1}')
ciphertexts=("ZK5EA1tGT4AHOUCUU5tUMuQCfA2fbjnSEgOiLR104eI=" "ZK5ECtTH+jkYs87uEEUrwyZ9+wsFkWpk3AbtnTEY3gs=" "dCTjgwaXvsPzQ0QRlweM7IP7T0ytT7G25rEM4g+17cQ=" "dCTjgwaXvsPzFQeOg5gg6+uMOKSuoreXJ/o3UsgJY+o=" "dCTjgwaXvsPzFUpdPq8wCPu5bGNwygQ7fFBQp+bM+As=" "dCTjgwaXvsPzQ0QRlweM7IP7T0ytT7G25rEM4g+17cQ=" "fc7pA9zD9Qa3+CUjr4w5AglNX9LT3SihkH2mENLyYNc=")
iv="00000000000000000000000000000000"
for c in ${ciphertexts[@]}; do
echo $c | base64 -d > /tmp/cipher.txt
openssl enc -aes-256-cfb8 -d -K "$key" -iv "$iv" -in /tmp/cipher.txt -out /tmp/out.txt
out=$(cat /tmp/out.txt | tr -d '\0')
echo $out
done
rm -f /tmp/out.txt /tmp/cipher.txt
```


This successfully outputs the following:

```
HTWXNF-8010R
HTWQNF-8010
XNF-8010R
XNF-8010RVM
XNF-8010RV
XNF-8010R
QNF-8010
```


## Decrypting the Firmware File

Now we have a few possible passphrases to decrypted the firmware file with. Let's update our script from before:

```
#!/bin/bash
pass_list=("XNF-8010R" "HTWQNF-8010" "HTWXNF-8010R" "XNF-8010RVM" "XNF-8010RV" "QNF-8010")
# we need to try all of these since the camera might have a different default digest than our machine
digest_list=("md5" "sha1" "sha256" "sha384" "sha512")
fwfile="XNF-8010R_2.10.04_20230328_R640.img"
outdir="out"
mkdir -p $outdir
rm -rf ${outdir}/*
count=0
for pass in "${pass_list[@]}"; do
for digest in "${digest_list[@]}"; do
openssl enc -aes-256-cbc -d -md ${digest} -k "${pass}" -in ${fwfile} -out ${outdir}/try${count}_${digest}.bin
done
((count++))
done
```


Note that we are also looping over a bunch of different digest functions because we don't know what the default digest function the openssl version on the camera is.

Here is the result of running `file`

on all of our attempts:

```
$ file out/*
out/try0_md5.bin: data
out/try0_sha1.bin: data
out/try0_sha256.bin: data
out/try0_sha384.bin: data
out/try0_sha512.bin: data
out/try1_md5.bin: data
out/try1_sha1.bin: data
out/try1_sha256.bin: data
out/try1_sha384.bin: data
out/try1_sha512.bin: data
out/try2_md5.bin: gzip compressed data, last modified: Tue Mar 28 10:42:57 2023, from Unix, original size modulo 2^32 112394240
out/try2_sha1.bin: data
out/try2_sha256.bin: data
out/try2_sha384.bin: data
out/try2_sha512.bin: data
out/try3_md5.bin: data
out/try3_sha1.bin: data
out/try3_sha256.bin: data
out/try3_sha384.bin: data
out/try3_sha512.bin: data
out/try4_md5.bin: data
out/try4_sha1.bin: data
out/try4_sha256.bin: data
out/try4_sha384.bin: data
out/try4_sha512.bin: data
out/try5_md5.bin: data
out/try5_sha1.bin: data
out/try5_sha256.bin: data
out/try5_sha384.bin: data
out/try5_sha512.bin: data
```


We did it! Note that try2 corresponds to the passphrase "HTWXNF-8010R".

Let's unpack our freshly decrypted firmware:

```
$ cd out
$ mkdir fw
$ mv try2_md5.bin fw/fw.tar.gz
$ cd fw
$ tar -zxf fw.tar.gz
$ ls -l
total 155620
drwxr-xr-x 2 nmatt nmatt 4096 Mar 28 2023 BFRS
drwxr-xr-x 2 nmatt nmatt 4096 Mar 28 2023 boot_fw
-rw-r--r-- 1 nmatt nmatt 52144865 Jun 5 00:18 fw.tar.gz
drwxr-xr-x 2 nmatt nmatt 4096 Mar 28 2023 fwupgrade_data
-rwxr-xr-x 1 nmatt nmatt 559312 Mar 28 2023 fwupgrader
-rwxr-xr-x 1 nmatt nmatt 13604110 Mar 28 2023 ramdisk_xnf8010r.wn5.gz
-rwxr-xr-x 1 nmatt nmatt 4898638 Mar 28 2023 uImage
-rwxr-xr-x 1 nmatt nmatt 88121472 Mar 28 2023 work_xnf8010r.wn5
```


## Predictable Passphrases

So I mentioned at the beginning that the camera model I performed the firmware extraction on is `XNF-8010RW`

and we observe that the firmware decryption password was `HTWXNF-8010R`

. We can see that the firmware encryption passphrase is basically just the model number of the device!

Let's test this hypothesis on another firmware file that we don't have a physical device for.

For this test I selected the [WiseNet TNO-L4040TR device](https://www.hanwhavision.com/en/products/camera/network/bullet/tno-l4040tr/) which has a firmware image file called `TNO-L4040TR_2.21.11_20240923_R81.img`

.

Using the same patterns as we saw in the other device, we guessed that the passphrase is `HTWTNO-L4040TR`

.

This passphrase was found to be correct:

```
openssl enc -aes-256-cbc -d -md md5 -k "HTWTNO-L4040TR" -in TNO-L4040TR_2.21.11_20240923_R81.img -out out.bin
```


## Conclusion

This was a fun mental exercise and hopefully a good demonstration of how a persistent attacker is going to reverse-engineer your hardcoded password/encryption scheme. It is not a matter of "IF"; it's a matter of "WHEN".

### Need IoT Security Expertise?

Brown Fine Security provides expert IoT penetration testing to help secure your connected devices. From hardware analysis to cloud API testing, we uncover vulnerabilities before attackers do.

[Get a Free Consultation](/contact)

### Want to Learn IoT Hacking?

Ready to break into IoT security? Our hands-on training courses teach real-world hardware hacking, firmware analysis, and IoT exploitation techniques used by professional pentesters.

[Explore Training Courses](https://training.brownfinesecurity.com/)