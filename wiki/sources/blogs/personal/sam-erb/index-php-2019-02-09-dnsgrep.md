---
source: sam-erb
source_url: https://blog.erbbysam.com/index.php/2019/02/09/dnsgrep
title: "DNSGrep — Quickly Searching Large DNS Datasets – blog.erbbysam.com"
---

The Rapid7 [Project Sonar](https://opendata.rapid7.com/) datasets are amazing resources. They represent scans across the internet, compressed and easy to download. This blog post will focus on two of these datasets:

[https://opendata.rapid7.com/sonar.rdns_v2/](https://opendata.rapid7.com/sonar.rdns_v2/) (rdns)[https://opendata.rapid7.com/sonar.fdns_v2/](https://opendata.rapid7.com/sonar.fdns_v2/) (fdns_a)

Unfortunately, working with these datasets can be a bit slow as the rdns and fdns_a datasets each contain over 10GB of compressed text. My old workflow for using these datasets was not efficient:

`ubuntu@client:~$ time gunzip -c fdns_a.json.gz | grep "erbbysam.com"`

{"timestamp":"1535127239","name":"blog.erbbysam.com","type":"a","value":"54.190.33.125"}

{"timestamp":"1535133613","name":"erbbysam.com","type":"a","value":"104.154.120.133"}

{"timestamp":"1535155246","name":"www.erbbysam.com","type":"cname","value":"erbbysam.com"}

real 11m31.393s

user 12m29.212s

sys 1m37.672s


I suspected there had to be a faster way of searching these two datasets.

(TLDR, reverse and sort domains then binary search)

## DNS Structure

A defining features of the DNS system is its tree-like structure. Visiting this page, you are three levels below the [root domain](https://en.wikipedia.org/wiki/Root_name_server#Root_domain):

com

com.erbbysam

com.erbbysam.blog

The grep query above looks for a domain name tied to the root domain, not an arbitrary string in the file. **If we could shape our dataset into a DNS tree, an equivalent lookup would just require a quick traversal of this tree.**

## Binary Search

The task of transforming a large dataset into a tree on disk and traversing this tree can be simplified further using a [binary search algorithm](https://en.wikipedia.org/wiki/Binary_search_algorithm).

The first step in using a binary search algorithm is to sort the data. One option, matching for format above, is the form “com.erbbysam.blog”. This would require a slightly more complex DNS reversal algorithm than neccessary. To simplify, reverse each line instead:

moc.masybbre.golb,521.33.091.4

moc.masybbre,331.021.451.40

moc.masybbre.www,moc.masybbre

There are no one-command solutions to sort a dataset that does not fit into memory (that I am aware of). To sort these large files, split the data into sorted chunks and then merge the results together:

```
# fetch the fdns_a file
wget -O fdns_a.gz https://opendata.rapid7.com/sonar.fdns_v2/2019-01-25-1548417890-fdns_a.json.gz
# extract and format our data
gunzip -c fdns_a.gz | jq -r '.value + ","+ .name' | tr '[:upper:]' '[:lower:]' | rev > fdns_a.rev.lowercase.txt
# split the data into chunks to sort
# via https://unix.stackexchange.com/a/350068 -- split and merge code
split -b100M fdns_a.rev.lowercase.txt fileChunk
# remove the old files
rm fdns_a.gz
rm fdns_a.rev.lowercase.txt
# Sort each of the pieces and delete the unsorted one
# via https://unix.stackexchange.com/a/35472 -- use LC_COLLATE=C to sort ., chars
for f in fileChunk*; do LC_COLLATE=C sort "$f" > "$f".sorted && rm "$f"; done
# merge the sorted files with local tmp directory
mkdir -p sorttmp
LC_COLLATE=C sort -T sorttmp/ -muo fdns_a.sort.txt fileChunk*.sorted
# clean up
rm fileChunk*
```


More detailed instructions for running this script and the rdns equivalent can be found here:[https://github.com/erbbysam/DNSGrep#run](https://github.com/erbbysam/DNSGrep#run)

## DNSGrep

Now we can search the data! To accomplish this, I built a simple golang utility that can be found here:[https://github.com/erbbysam/DNSGrep](https://github.com/erbbysam/DNSGrep)

```
ubuntu@client:~$ ls -lath fdns_a.sort.txt
-rw-rw-r-- 1 ubuntu ubuntu 68G Feb 3 09:11 fdns_a.sort.txt
ubuntu@client:~$ time ./dnsgrep -f fdns_a.sort.txt -i "erbbysam.com"
104.154.120.133,erbbysam.com
54.190.33.125,blog.erbbysam.com
erbbysam.com,www.erbbysam.com
real 0m0.002s
user 0m0.000s
sys 0m0.000s
```


That is significantly faster!

The algorithm is pretty simple:

- Use a binary search algorithm to seek through the file, looking for a substring match against the query.
- Once a match is found, the file is scanned backwards in 10KB increments looking for a non-matching substring.
- Once a non-matching substring is found, the file is scanned forwards until all exact matches are returned.

## PoC

**PoC** **disclaimer**: There is no uptime/performance guarantee of this service and I likely will take this offline at some point in the future. Keep in mind that the datasets here are from a scan on 1/25/19 — DNS records may have changed by the time you read this.

As these queries are so quick, I set up an AWS EC2 t2.micro instance with a spinning disk (Cold HDD sc1) and hosted a server that allows queries into these datasets:[https://github.com/erbbysam/DNSGrep/tree/master/experimentalServer](https://github.com/erbbysam/DNSGrep/tree/master/experimentalServer)

```
ubuntu@client:~$ curl 'https://dns.bufferover.run/dns?q=erbbysam.com'
{
"Meta": {
"Runtime": "0.000361 seconds",
"Errors": [
"rdns error: failed to find exact match via binary search"
],
"FileNames": [
"2019-01-25-1548417890-fdns_a.json.gz",
"2019-01-30-1548868121-rdns.json.gz"
],
"TOS": "The source of this data is Rapid7 Labs. Please review the Terms of Service: https://opendata.rapid7.com/about/"
},
"FDNS_A": [
"104.154.120.133,erbbysam.com",
"54.190.33.125,blog.erbbysam.com",
"erbbysam.com,www.erbbysam.com"
],
"RDNS": null
}
```


Having a bit of fun with this, I queried every North Korean domain name, grepping for the IPs not in [North Korean IP space](https://en.wikipedia.org/wiki/Internet_in_North_Korea#IP_address_ranges):[https://dns.bufferover.run/dns?q=.kp](https://dns.bufferover.run/dns?q=.kp)

```
ubuntu@client:~$ curl 'https://dns.bufferover.run/dns?q=.kp' 2> /dev/null | grep -v "\"175\.45\.17"
{
"Meta": {
"Runtime": "0.000534 seconds",
"Errors": null,
"FileNames": [
"2019-01-25-1548417890-fdns_a.json.gz",
"2019-01-30-1548868121-rdns.json.gz"
],
"TOS": "The source of this data is Rapid7 Labs. Please review the Terms of Service: https://opendata.rapid7.com/about/"
},
"FDNS_A": [
"175.45.0.178,ns1.portal.net.kp",
],
"RDNS": [
"185.33.146.18,north-korea.kp",
"66.23.232.124,sverjd.ouie.kp",
"64.86.226.78,ns2.friend.com.kp",
"103.120.178.114,dedi.kani28test.kp",
"198.98.49.51,gfw.kp",
"185.86.149.212,hey.kp"
]
}
```


That’s it! Hopefully this was useful! Give it a try: https://dns.bufferover.run/dns?q=<hostname>