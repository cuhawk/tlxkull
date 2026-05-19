---
source: spaceraccoon
source_url: https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/
title: "Beat The Clock: The CSIT InfoSecurity Challenge | Spaceraccoon's Blog"
published: 2020-09-18T03:44:44+00:00
description: "Last month, the Centre for Strategic Infocomm Technologies (CSIT) invited local cybersecurity enthusiasts to tackle the InfoSecurity Challenge (TISC). The Challenge was organized in a capture-the-flag format, with 6 cybersecurity and programming challenges of increasing difficulty unlocked one after another."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Beat The Clock: The CSIT InfoSecurity Challenge

Sep 18, 2020
·

4095 words

·

20 minute read


# Introduction: Red Alert! [🔗](https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/\#introduction-red-alert)

Last month, the Centre for Strategic Infocomm Technologies (CSIT) invited local cybersecurity enthusiasts to tackle the InfoSecurity Challenge (TISC). The Challenge was organized in a capture-the-flag format, with 6 cybersecurity and programming challenges of increasing difficulty unlocked one after another.

> On New Year’s Eve, hackers from the PALINDROME group launched a ransomware attack on a major finance company and encrypted some of its critical data servers. Your mission is to complete a series of tasks to recover as much data as possible to prevent the company from having to give in to PALINDROME’s demand. The tasks will increase in difficulty as you go along so be prepared to put up the fight of your life.

With this exciting introduction, I tackled a series of difficult problems that encompassed reverse engineering, binary exploitation, and cryptography. This took me far out of my comfort zone of application security, but since I wanted to build my skills in those areas, it was a welcome challenge.

# STAGE 1: What is this thing? [🔗](https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/\#stage-1-what-is-this-thing)

The first challenge explained the situation. A user had trusted a malicious StackOverflow answer and run an unknown script on their computer. As a result, the user unknowingly downloaded and executed ransomware.

The first stage presented us with a suspicious zip file that was downloaded by the script. According to the description, it was protected by a simple password (6 characters, hexadecimal) as well as several layers of compression. I had to extract the encrypted data within.

Breaking the password was straightforward. I attempted to generate the possible hexadecimal password combinations with `for i in {0..16777215}; do echo $(printf "%06X\n" $i) >> hex.txt; done` but it took too long, so I ran a Rust script instead:

```rust
fn main() {
    for n in 0..16777216 {
        println!("{:06x}", n);
    }
}
```

I built the executable with `rustc gen_hex.rs`, then redirected the output with `./gen_hex > hex.txt`. Next, I brute-forced the candidates with `fcrackzip -D -p  hex.txt suspicious.zip -u`. For cracking zip files, I prefer to use the `fcrackzip` tool because it automatically attempts to unzip the file when it thinks it has a matching password. This avoids false positives. In a few minutes, I received the password.

![Output of fcrackzip](https://spaceraccoon.dev/images/8/output_of_fcrackzip.png)

When I unzipped the file, it extracted a `temp.mess` file. Running `file temp.mess` returned `temp.mess: zlib compressed data`. So this was a zlib file. According to the evidence, the malicious script also ran `sudo apt install git wget zip unzip lzma gzip bzip2 python3 pip3`, so I expected to encounter several different compression formats. When I decompressed the zlib file with `pigz -d < temp.mess > temp.mess2`, `file temp.mess2` returned `temp.mess2: bzip2 compressed data, block size = 900k`. After this, there was another compressed file, and so on. It was a terrifying Russian Doll of nested compression. By the 20th layer, I decided I had to automate it. After all, it was also a programming challenge.

With a bit of trial and error, I narrowed down the various compression formats and the proper commands to decompress them. I collated these into a bash script:

```bash
#!/bin/bash

i=1
while :
do
    file=$(file compressed$i.unk);
    echo $file;
    let "next = i + 1";
    if [[ "$file" == *zlib* ]] || [[ "$file" == *TeX* ]]; then
        echo "compressed$i.unk is zlib";
        pigz -d < compressed$i.unk > compressed$next.unk;
    elif [[ "$file" == *bzip2* ]]; then
        echo "compressed$i.unk is bzip2";
        bzip2 -dc compressed$i.unk > compressed$next.unk;
    elif [[ "$file" == *gzip* ]]; then
        echo "compressed$i.unk is gzip";
        gunzip -c compressed$i.unk > compressed$next.unk;
    elif [[ "$file" == *XZ* ]]; then
        echo "compressed$i.unk is XZ";
        unxz compressed$i.unk -S unk -c > compressed$next.unk;
    elif grep -q -E "^([0-9A-Fa-f]{2})+$" "compressed$i.unk"; then
        echo "compressed$i.unk is hex";
        cat compressed$i.unk | xxd -r -p > compressed$next.unk;
    elif grep -q -E "(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?" "compressed$i.unk"; then
        echo "compressed$i.unk is base64";
        base64 -d compressed$i.unk > compressed$next.unk;
    else
        exit 1;
    fi
    let "i+=1";
done
```

You might be wondering why I checked for a TeX format file. This is because halfway through the compression layers, the challenge throws you a curveball, returning a file that `file` identified as `TeX font metric data ((w\332\203\326\335\367\275\365\276\256\262\356\316\271\232\225y\262\345\327P\027\257u\265\265\266\273\233\226w,wf7w(;\356\344u1\214\373\276]=\266\225\272\367y\324\236\367n\275\272\275\334\256\257\276\367\243\357\271\332n\367\274\227\275\207ml\271\261\355\323\255+\034\335s{\275y\346\325\267\313_})`. This stumped me as I couldn’t figure out how to deal with a TeX font file. Forutnately, when I double-checked the file with `binwalk` instead of `file`, I found that it was just containing another zlib file.

```console
$ binwalk -e compressed36.unk

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             Zlib compressed data, default compression
7             0x7             bzip2 compressed data, block size = 900k
```

With this addition, my script completed the decompression perfectly, going through about 150 layers of compression!

![Output of unzip script](https://spaceraccoon.dev/images/8/output_of_unzip_script.png)

The final file was a simple JSON with the flag:

```json
{
   "anoroc":"v1.320",
   "secret":"TISC20{q1_418f04b27e58165f62b6bddfc47cf6d1}",
   "desc":"Submit this.secret to the TISC grader to complete challenge",
   "constants":[\
      1116352408,\
      1899447441,\
      3049323471,\
      3921009573,\
      961987163,\
      1508970993,\
      2453635748,\
      2870763221\
   ],
   "sign":"0lqcBkBNXPqA"
}
```

# STAGE 2: Find me some keys [🔗](https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/\#stage-2-find-me-some-keys)

The next stage provided the ransomware sample itself and asked for the public key that was embedded in the binary as a base64 string. The ransomware was called anoroc in keeping with the palindrome theme. Although the challenge provided a Dockerfile to run the ransomware in a container, I decided to work like a normal human being and popped it into a virtual machine so I could use the graphical interface.

I began with static analysis and opened anoroc in IDA. Unfortunately, it failed to analyze the binary. When I checked the strings subview, I found the following string: `$Info: This file is packed with the UPX executable packer http://upx.sf.net $\n`.

![Strings subview in IDA](https://spaceraccoon.dev/images/8/strings_subview_in_ida.png)

Aha! All I had to do was to unpack it with `upx -d anorocware`.

![Output of upx](https://spaceraccoon.dev/images/8/output_of_upx.png)

With the newly-unpacked file, IDA analyzed anoroc properly as a 64-bit ELF binary, returning lots of debugging symbols. On first glance at the functions subview, I guessed that it was a Golang binary because of imported functions like net/http and encoding/json. Unsurprisingly, the public key could not be found in the strings subview. It was probably instantiated within a function. As such, I turned to dynamic analysis with GDB.

In IDA’s pseudocode, I noticed that `encoding_base64__ptr_Encoding_DecodeString` was called before `encoding_pem_Decode` and `crypto_x509_ParsePKIXPublicKey`. I concluded this was most likely where the public key was being read and used by anoroc.

![Pseudocode of reading public key](https://spaceraccoon.dev/images/8/pseudocode_of_reading_public_key.png)

I opened the executable in GDB with `gdb anorocware2`, then ran `info functions` to get a list of the functions’ proper names (see `anoroc_functions.txt`). Next, I set a breakpoint for the base64 decode function with `b encoding/base64.(*Encoding).DecodeString` and ran the ransomware with `r`. Once it stopped at my breakpoint, I dumped the arguments with `info args` and there was a truncated base64 string! I configured GDB with `set print elements 0` to print the full string.

![Output of debugging DecodeString in GDB](https://spaceraccoon.dev/images/8/output_of_debugging_decodestring_in_gdb.png)

I confirmed that the base64 string decoded into a public key, then hashed it to get my flag.

# STAGE 3: Recover some files [🔗](https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/\#stage-3-recover-some-files)

Along with the ransomware sample, the challenge provided several files that had been encrypted by anoroc. I had to extract the flag from one of the encrypted database files.

From my dynamic testing, I knew that anoroc encrypted all files without `.txt` or `.anoroc` extensions. I began to reconstruct the encryption algorithm from IDA’s pesudocode output. I noticed that in the `main` function, there was the `main_visit` function before the `path_filepath_Walk` call. Additionally, there was a `main_visit_func1` function that ran `crypto_aes_NewCipher`, `crypto_cipher_NewCTR`, and `io_ioutil_WriteFile`. These calls used arguments like `main_encKey` and `main_encIV`. This was most likely how the files were encrypted using a AES CTR stream cipher.

![Pseudocode of walking files](https://spaceraccoon.dev/images/8/pseudocode_of_walking_files.png)

![Pseudocode of encrypting files](https://spaceraccoon.dev/images/8/pseudocode_of_encrypting_files.png)

Additionally, by tracing back the references to `main_encKey` and `main_encIV`, I found another code section where these variables were initialized using `math_rand___Rand__Intn`. Each byte of the variables was set to `byte(rand.Intn(1337))`.

![Pseudocode of initializing encKey and encIV](https://spaceraccoon.dev/images/8/pseudocode_of_initializing_enckey_and_enciv.png)

Based on the [Golang documentation](https://golang.org/pkg/math/rand/#Seed), the random function defaults to a seed of `1`. However, since the encrypted files changes every time I ran `anoroc`, I decided that it was probably set to some pseudorandom value. Where was this happening?

Looking back at the list of functions in IDA, I noticed `main_init_0`, which executed `time_Now` before `math_rand__ptr_Rand_Seed`. So it appeared that the seed was set to the time that the ransomware was executed!

![Pseudocode of seeding Rand](https://spaceraccoon.dev/images/8/pseudocode_of_seeding_rand.png)

Based on all this information, I recreated the encryption algorithm in `main_visit_func1`:

```go
package main

import (
	"crypto/aes"
	"crypto/cipher"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
)

func main() {
    // Victim file
	plainFile := "secret_investments.db"
	plaintext, err := ioutil.ReadFile(plainFile)
	if err != nil {
		log.Fatal(err)
	}

	var seed int64
	encKey := make([]byte, 16)
	encIV := make([]byte, 16)

	// Initialize seed
	seed := time.Now().UnixNano() / 1000
	rand.Seed(seed)

	// Initialize encKey
	for i := range encKey {
		encKey[i] = byte(rand.Intn(1337))
	}

	// Initialize encIV
	for i := range encIV {
		encIV[i] = byte(rand.Intn(1337))
	}
	// Change first 2 bytes of encIV to first two bytes of file name
	encIV[0] = byte(encryptedFile[0])
	encIV[1] = byte(encryptedFile[1])

	// Initialize cipher from encKey
	block, err := aes.NewCipher(encKey)
	if err != nil {
		log.Fatal(err)
	}

	// Initialize cipher stream from cipher and envIV
	stream := cipher.NewCTR(block, encIV)

	// Encrypt plaintext with cipher stream
	ciphertext := make([]byte, len(plaintext))
	stream.XORKeyStream(ciphertext, plaintext)

	err = ioutil.WriteFile(plainFile+".anoroc", ciphertext, 0644)
	if err != nil {
		log.Fatal(err)
	}
}
```

Next, I verified this in GDB. I set a breakpoint in `math/rand.(*Rand).Seed` to dump the value of the seed, then inserted that seed value in my script. I then checked if it would encrypt a plaintext to the same ciphertext. One thing I missed in my initial code was that the algorithm set the first two bytes of the initialization vector (IV) to the first two letters of the file. I only figured this out after debugging the executable in GDB and dumping the arguments to the `cipher.NewCTR` function, where I noticed the discrepancy. Finally, my outputs matched!

Next, I performed cryptoanalysis on the algorithm. There are a few weaknesses in the encryption algorithm:

1. The encryption key and IV are initialized with `rand.Intn(1337)`, thus restricting the possible byte range to `1337`.
2. The first two bytes of the IV are set to the first two letters of the filename. Since the key and IV are never changed, this means that files with the same first two letters will be encrypted against the same AES-CTR keystream, a weakness I had exploited previously in a [Cryptopals challenge](https://cryptopals.com/sets/3/challenges/19).
3. The random seed is set to a timestamp, which I can derive from the encrypted files’ modified timestamp.

However, I could not exploit 1) and 2). 1) still meant that there were `1337 ** 16` possible combinations, which was far too many to brute-force. 2) required many samples of the ciphertext that had been encrypted against the keystream, but only a few met this criteria. Moreover, none of my target database files met this criteria.

I began looking into the timestamps. Strangely, the timestamp generated by anoroc was different from what I generated with `time.Now()`. For example, even though an encrypted file was modified on `2020-08-07 01:49:10.000000000 +0800` and thus had a Unix timestamp of `1596736150000000`, the seed used to encrypt it was actually `1559245967038138`. This was probably some sort of jitter introduced to make it less straightforward.

After testing multiple encryption rounds in my virtual machine and comparing the seed used to the “real” Unix timestamp, I narrowed the jitter down to about `-37486400000000`. Still, there was a huge margin of error, which meant that I had to brute-force tens of billions of candidates! As such, I initially rejected the brute-force route and spent many hours trying to find a cryptographic weakness. Eventually I realized that brute-forcing was the only option.

Fortunately, there were a few things I could do to optimize my attack. Golang supports built-in concurrency with Goroutines, speeding up my tests. After some performance tweaks, I settled on one million concurrent Goroutines. Using more Goroutines would cause mutex/semaphore lock ups in my system. Additionally, I researched and asked how to speed up brute-forcing decryption, which led me to realize that since the encryption used an AES-CTR stream cipher, I only had to decrypt and check a few bytes instead of the whole file! In this case, I brute-forced against the provided encrypted PNG files and looked for the first five PNG magic bytes that all PNG files start with. This increased my speed by 10 times.

```go
package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"sync"
)

func main() {
	encryptedFile := "slopes.png.anoroc"
	// encryptedFile := "191px-PNG_Test.png.anoroc"
	// encryptedFile := "ransomnote-anoroc.db.anoroc"
	ciphertext, err := ioutil.ReadFile(encryptedFile)
	if err != nil {
		log.Fatal(err)
	}
	ciphertext = ciphertext[:5]

	var x int64
	var y int64
	var seed int64
	encKey := make([]byte, 16)
	encIV := make([]byte, 16)
	var wg sync.WaitGroup
	y = 0

	// Bruteforce last 8 digits of timestamp; run last 6 digits concurrently for performance
	for y = 8500; y < 10000; y = y + 1 {
		fmt.Printf("Currently bruteforcing %d\n", 1559240000000000+(y*1000000))
		for x = 0; x < 1000000; x = x + 1 {
			wg.Add(1)
			go func(x int64) {
				defer wg.Done()

				// Initialize random seed from bruteforced timestamp

				seed = 1559240000000000 + x + (y * 1000000)
				// seed = 1561925774299643
				rand.Seed(seed)

				// Initialize encKey
				for i := range encKey {
					encKey[i] = byte(rand.Intn(1337))
				}

				// Initialize encIV
				for i := range encIV {
					encIV[i] = byte(rand.Intn(1337))
				}
				// Change first 2 bytes of encIV to first two bytes of file name
				encIV[0] = byte(encryptedFile[0])
				encIV[1] = byte(encryptedFile[1])

				// Initialize cipher from encKey
				block, err := aes.NewCipher(encKey)
				if err != nil {
					log.Fatal(err)
				}

				// Initialize cipher stream from cipher and envIV
				stream := cipher.NewCTR(block, encIV)

				// Decrypt ciphertext with cipher stream
				plaintext := make([]byte, 5)
				stream.XORKeyStream(plaintext, ciphertext)

				// if bytes.Compare(plaintext[:5], []byte{10, 36, 36, 36, 36}) == 0 {
				// Check if PNG header matches to confirm bruteforce is successful
				if bytes.Compare(plaintext, []byte{137, 80, 78, 71, 13}) == 0 {
					fmt.Println("Found!")
					fmt.Printf("Seed is %d\n", seed)
				}
			}(x)
		}
		wg.Wait()
	}
}
```

Before I applied my optimizations, I left my brute-force to run overnight, but it failed. After optimizing my code, I increased the search space and ran it on several machines, including Amazon EC2 machines in the cloud. After a few hours, I successfully brute-forced the seed!

![Output of wide bruteforce](https://spaceraccoon.dev/images/8/output_of_wide_bruteforce.png)

However, due to inaccuracies caused by the Goroutines, I had to run a second script without Goroutines in the narrowed range to find my seed.

```go
package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
)

func main() {
	encryptedFile := "slopes.png.anoroc"
	// encryptedFile := "191px-PNG_Test.png.anoroc"
	// encryptedFile := "ransomnote-anoroc.db.anoroc"
	ciphertext, err := ioutil.ReadFile(encryptedFile)
	if err != nil {
		log.Fatal(err)
	}
	ciphertext = ciphertext[:5]

	var x int64
	encKey := make([]byte, 16)
	encIV := make([]byte, 16)

	// Bruteforce last 8 digits of timestamp; run last 6 digits concurrently for performance
	for x = 1559245967000000; x < 1559245968000000; x = x + 1 {
		// seed = 1561925774299643
		rand.Seed(x)

		// Initialize encKey
		for i := range encKey {
			encKey[i] = byte(rand.Intn(1337))
		}

		// Initialize encIV
		for i := range encIV {
			encIV[i] = byte(rand.Intn(1337))
		}
		// Change first 2 bytes of encIV to first two bytes of file name
		encIV[0] = byte(encryptedFile[0])
		encIV[1] = byte(encryptedFile[1])

		// Initialize cipher from encKey
		block, err := aes.NewCipher(encKey)
		if err != nil {
			log.Fatal(err)
		}

		// Initialize cipher stream from cipher and envIV
		stream := cipher.NewCTR(block, encIV)

		// Decrypt ciphertext with cipher stream
		plaintext := make([]byte, 5)
		stream.XORKeyStream(plaintext, ciphertext)

		// if bytes.Compare(plaintext[:5], []byte{10, 36, 36, 36, 36}) == 0 {
		// Check if PNG header matches to confirm bruteforce is successful
		if bytes.Compare(plaintext, []byte{137, 80, 78, 71, 13}) == 0 {
			fmt.Println("Found!")
			fmt.Printf("Seed is %d\n", x)
		}
	}
}
```

![Output of narrow bruteforce](https://spaceraccoon.dev/images/8/output_of_narrow_bruteforce.png)

With the matching seed, I decrypted the database files using the following script:

```go
package main

import (
	"crypto/aes"
	"crypto/cipher"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
)

func main() {
	encryptedFile := "secret_investments.db.anoroc"
	ciphertext, err := ioutil.ReadFile(encryptedFile)
	if err != nil {
		log.Fatal(err)
	}

	var seed int64
	encKey := make([]byte, 16)
	encIV := make([]byte, 16)

	// Correct seed
	seed = 1559245967038138
	rand.Seed(seed)

	// Initialize encKey
	for i := range encKey {
		encKey[i] = byte(rand.Intn(1337))
	}

	// Initialize encIV
	for i := range encIV {
		encIV[i] = byte(rand.Intn(1337))
	}
	// Change first 2 bytes of encIV to first two bytes of file name
	encIV[0] = byte(encryptedFile[0])
	encIV[1] = byte(encryptedFile[1])

	// Initialize cipher from encKey
	block, err := aes.NewCipher(encKey)
	if err != nil {
		log.Fatal(err)
	}

	// Initialize cipher stream from cipher and envIV
	stream := cipher.NewCTR(block, encIV)

	// Decrypt ciphertext with cipher stream
	plaintext := make([]byte, len(ciphertext))
	stream.XORKeyStream(plaintext, ciphertext)

	fmt.Printf("%s\n", plaintext)
}
```

![Output of decrypt](https://spaceraccoon.dev/images/8/output_of_decrypt.png)

With that, I got the flag!

# STAGE 4: Where is the C2? [🔗](https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/\#stage-4-where-is-the-c2)

The next challenge asked me to figure out how the ransomware generated its command and control (C2) server domain names. It would then prompt me with a series of timestamps and ask me what domain name would be generated at that time.

Indeed, in my earlier testing of anoroc using Wireshark, I noticed that it would make HTTP POST requests to strange domains like `z1l2bnump3mdiclqv01eaqvytgxbjqxyq4qjic5ey.nyaa.net` and `okjm5qovulpji1n2r4jbjdwysa1cwa75e5.cf` with the encryption IV and key.

![C2 request](https://spaceraccoon.dev/images/8/c2_request.png)

Before sending this request, it would also an encrypted HTTPS request which I could not read in Wireshark. Going back to the pseudocode in IDA, I realized that before calling `net_http___Client__PostForm` in `main`, the ransomware would run `main_QbznvaAnzrTrarengvbaNytbevguz`. In turn, this function called `net_http___Client__Get` followed by `encoding_json___Decoder__Decode`. There were also calls to `math_rand___Rand__Intn` and `runtime_concatstring3`, which suggested that `main_QbznvaAnzrTrarengvbaNytbevguz` was the domain generating function.

![Pseudocode of generating domain](https://spaceraccoon.dev/images/8/pseudocode_of_generating_domain.png)

By debugging `net/http.(*Client).Get` in GDB and dumping the arguments passed to it, I discovered that the HTTPS request was a GET request to `https://worldtimeapi.org/api/timezone/Etc/UTC.json` which returned a bunch of time-related data:

```json
{
   "abbreviation":"UTC",
   "client_ip":"<IP ADDRESS>",
   "datetime":"2020-09-07T18:29:49.031611+00:00",
   "day_of_week":1,
   "day_of_year":251,
   "dst":false,
   "dst_from":null,
   "dst_offset":0,
   "dst_until":null,
   "raw_offset":0,
   "timezone":"Etc/UTC",
   "unixtime":1599503389,
   "utc_datetime":"2020-09-07T18:29:49.031611+00:00",
   "utc_offset":"+00:00",
   "week_number":37
}
```

Thus, I suspected that the ransomware used the data in the API response to generate the C2 domain. I decided to test my hypothesis by redirecting the request to `worldtimeapi.org` to my own local server. Unfortunately, my first attempt at redirection failed. I edited `/etc/hosts` to point `worldtimeapi.org` to `127.0.0.1` (where my local server was running) but the malware failed with `panic: Get "https://worldtimeapi.org/api/timezone/Etc/UTC.json": tls: first record does not look like a TLS handshake`. It was probably checking for a secure HTTPS/TLS connection. As such, I ran a HTTPS server with my self-signed certificate using a snippet from the web:

```python
# python3 version, derived from python2 version https://gist.github.com/dergachev/7028596
#
# taken from http://www.piware.de/2011/01/creating-an-https-server-in-python/
# generate server.xml with the following command:
#    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# run as follows:
#    python3 simple-https-server.py
# then in your browser, visit:
#    https://localhost:4443

import http.server
import ssl

httpd = http.server.HTTPServer(('localhost', 4443), http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='./server.pem', server_side=True)
httpd.serve_forever()
```

Unfortunately, this did not fool the ransomware, which failed again with `panic: Get "https://worldtimeapi.org/api/timezone/Etc/UTC.json": x509: certificate signed by unknown authority`. This was a dead end due to the HTTPS protocol used by the malware.

I decided to patch the executable at runtime, using GDB to modify the URL passed to the `net/http.(*Client).Get` function. After some trial-and-error, I managed to change the string from `https://worldtimeapi.org/api/timezone/Etc/UTC.json` to `http://xworldtimeapi.org/api/timezone/Etc/UTC.json` with `set {int64}0x6f9966 = 0x782f2f3a70747468` (the hex decodes to `x//:ptth` which is reversed for the little-endian format). By changing the start of the URL from `https://` to `http://`, I effectively changed the request protocol from HTTPS to HTTP, which would not check for a valid certificate! Next, I modified my hosts file to point `xworldtimeapi.org` to my local server I had started with `python3 -m http.server 80`. With this, the malware ran successfully and sent the API request to my server.

![Output of debugging net in GDB](https://spaceraccoon.dev/images/8/output_of_debugging_net_in_gdb.png)

However, it would be really time-consuming to constantly patch the argument on each run, so I wrote a GDB script to automate this.

```console
b main.QbznvaAnzrTrarengvbaNytbevguz
b net/http.(*Client).Get
r
c
c
set {int64}0x6f9966 = 0x782f2f3a70747468
c
quit
```

Whenever I ran GDB with the script, the malware would be patched automatically.

Immediately, I noticed that if I sent the same JSON response from my server, anoroc would always request the same domain. This confirmed that anoroc generated the domain based on some value in the JSON response. Next, I tweaked each value in the JSON one by one until the requested domain changed. As it turned out, `unixtime` was the seed.

Even with this knowledge, I could not reverse-engineer the algorithm to generate the domain as that code section was well-obfuscated. Nevertheless, with my existing set-up, I realized I could still solve the challenge by modifying the value of `unixtime` in my server’s JSON response to match the timestamps given by the challenge, then checking the DNS queries sent by the patched malware in Wireshark to retrieve the generated domain. This allowed me to completely skip reverse-engineering the complex obfuscated code.

This worked… for the first 20 answers. At that point, I realized the challenge probably expected some sort of automation. This would have been simple if I had reverse-engineered the algorithm. However, I found a way around this by automating my dynamic solver as much as possible. For example, I wrote a script to automatically edit the JSON file based on the input:

```python
import json
import sys

with open("/home/ubuntu/Documents/fakeworldtimeapi/api/timezone/Etc/UTC.json", "r") as jsonFile:
    data = json.load(jsonFile)

data["unixtime"] = int(sys.argv[1])

with open("/home/ubuntu/Documents/fakeworldtimeapi/api/timezone/Etc/UTC.json", "w") as jsonFile:
    json.dump(data, jsonFile)
```

Next, I combined all my scripts to retrieve the challenge, update the JSON, and then launch the patched binary:

```python
from pwn import *
import subprocess

conn = remote('fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg', 31090)

conn.recvuntil('SUBMISSION_TOKEN?')
conn.send('mVwoHxiiprhNnxtEghHOHeylkAYLEGKRnPLoMTCgkfArVTkgkAOgKQPpwudgmCbl\r\n')

#'220 FTP server (vsftpd)'
while True:
    try:
        question = conn.recvuntil('? ')
        print(question)
    except:
        conn.interactive()
    timestamp = question.split()[-1][:-1]
    print("Timestamp: {}".format(timestamp))
    subprocess.Popen(['python3', '/home/ubuntu/Documents/fakeworldtimeapi/updatejson.py', timestamp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(['gdb', '/home/ubuntu/Desktop/anorocware2', '--command=/home/ubuntu/Desktop/gdbcommands'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    domain = str.encode(input("Enter domain: ").strip())
    conn.send(domain + b'\r\n')

#'331'
conn.recvline()
#'Please specify the password.\r\n'
conn.close()
```

However, Python’s `input` was somewhat finicky and would fail immediately if I accidentally entered the wrong key, so I fell back to the netcat session to enter my answers. With the help of the scripts and some copy-and-pasting, I eventually solved the series of questions (about 100) and got the flag!

![Output of flag server](https://spaceraccoon.dev/images/8/output_of_unzip_script.png)

# STAGE 5: Bulletin Board System [🔗](https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/\#stage-5-bulletin-board-system)

The next stage presented me with a service running on the attacker’s C2 and asked me to hack back! It also provided the binary of the running service - some sort of message board system. The implication was that I had to find an exploit in the binary to pwn the attacker’s C2 server. However, when I opened the binary in IDA, it warned me that the headers were corrupted. I checked this with `readelf -h bbs`:

```console
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 03 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - GNU
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x400a60
  Start of program headers:          64 (bytes into file)
  Start of section headers:          65535 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         6
  Size of section headers:           64 (bytes)
  Number of section headers:         65535
  Section header string table index: 65535 (3539421402)
readelf: Error: Reading 4194240 bytes extends past end of file for section headers
```

![Output of readelf](https://i.snap.as/l7DKClN.png)

It seemed like 3 headers were corrupted: `Start of section headers`, `Number of section headers`, and `Section header string table index`. Using the file layout from [Wikipedia](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format), I fixed these headers at their correct offsets by setting them to `0` in a hex editor.

![Hex Editor view of binary](https://i.snap.as/AxfGS7F.png)

Next, when I ran the binary, it prompted for a username and password, although only a guest account was available. I had to figure out the password for the guest account. I looked into the assembly code surrounding the validation but found it hard to understand the assembly fully. The challenge resembled a [CrackMe challenge](https://re.kv.io/crackme/14.html), which is what I would have based my approach on.

# Clocking Out [🔗](https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/\#clocking-out)

Unfortunately, at this point I was running out of time, and ended my 48 hours. Although it would’ve been nice to use it fully, we all have lives to live! I will try cracking the binary at my leisure.

The challenge truly pushed me to pick up new reverse-engineering and cryptography skills. Although I was new to these domains, applying them in a CTF format taught me many practical tricks and built my confidence. There were absolutely zero application security challenges, and that forced me to Try Harder.

In the end, I placed 6th. I was happy that I did well for my first competitive reverse-engineering/binary CTF after beginning to learn the ropes. However, there was a clear difference between the top 4 (who got to stage 6) and the rest (who only completed stage 4 at best); the difference lay in being able to go beyond pseudocode and dynamic analysis to deep static analysis of assembly and advanced binary exploitation (Use-After-Frees). There is a lot more for me to learn!

I hope you enjoyed this writeup and look forward to others’ sharings on the challenge.

# Completers’ Writeups [🔗](https://spaceraccoon.dev/beat-the-clock-the-csit-infosecurity-challenge/\#completers-writeups)

1. [Calvin](https://blog.idiot.sg/2020-09-18/tisc-ctf-2020/)
2. [Jeremy](https://nandynarwhals.org/tisc-2020-writeups/)

[binary](https://spaceraccoon.dev/tags/binary) [reverse engineering](https://spaceraccoon.dev/tags/reverse-engineering)