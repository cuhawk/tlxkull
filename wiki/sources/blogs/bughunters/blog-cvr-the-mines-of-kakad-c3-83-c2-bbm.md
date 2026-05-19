---
source: bughunters
source_url: https://bughunters.google.com/blog/cvr-the-mines-of-kakad%C3%83%C2%BBm
title: "CVR: The Mines of Kakadûm - Google Bug Hunters"
description: "In this document, Google's Cloud Vulnerability Research team (CVR) presents vulnerabilities in a third-party JPEG 2000 image library called Kakadu. Exploiting memory corruption vulnerabilities typically requires knowledge about the target environment; however, CVR outlines how to overcome these challenges with a technique called 'Conditional Corruption,' achieving remote code execution impact."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/cvr-the-mines-of-kakad%C3%83%C2%BBm#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# CVR: The Mines of Kakadûm

![](https://storage.googleapis.com/bughunters-article-images/blogs/simonscannell.jpg)

Simon Scannell

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/amlw.jpg)

Anthony Weems

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/jjlopezjaimez.jpg)

Juan José López Jaimez

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/ezp.jpg)

Ezequiel Pereira

Information Security Engineer

Published: Sep 10, 2024

Product Security Engineering  Cloud Vulnerability Research  Cloud CISO  Google Cloud

[RSS Feed](https://bughunters.google.com/feed/en)

# CVR: The Mines of Kakadûm

Exploits leveraging memory corruption vulnerabilities typically require some
knowledge about the target environment, such as the binary, OS, and allocator.
These insights are required to e.g. prepare the heap and deploy ROP chain
gadgets. As a result, exploits typically target client-side software such as
browsers and phones. When server-side software vulnerabilities are exploited,
they usually target distributed software where the deployed binary and
environment is at least partially known.

Due to these knowledge requirement constraints, a large attack-surface is rarely
reported to be successfully exploited. As an example, this includes memory
corruption exploits against server-side software with no access to the source
code or binary. This includes open-source libraries with known CVE's being
compiled into an unknown environment. An additional challenge is dealing with
load-balanced environments. Even if an attacker can defeat ASLR in one request,
they have no guarantee that they are targeting the same worker in a follow-up
request.

In this document, Google's Cloud Vulnerability Research team (CVR) presents
[vulnerabilities](https://github.com/google/security-research/security/advisories/GHSA-g6qc-fhcq-vhf9)
in a third-party [JPEG 2000](https://en.wikipedia.org/wiki/JPEG_2000) image
library called [Kakadu](https://en.wikipedia.org/wiki/Kakadu_(software)). We
outline the challenges an external attacker would face in exploiting these
vulnerabilities in an unknown environment and how to overcome them with a
technique we internally call "Conditional Corruption" that allowed us to craft a
self-modifying image for exploitation and achieve Remote-Code-Execution impact.

In a [2007 study](https://en.wikipedia.org/wiki/Kakadu_(software)#:~:text=Kakadu%20library%20is%20heavy%20optimized%20and%20is%20a%20fully%20compliant%20implementation.%20Also%2C%20it%20has%20built%2Din%20multi%2Dthreading.%5B2%5D%20In%20a%202007%20study%20Kakadu%20outperformed%20the%20JasPer%20library%20in%20terms%20of%20speed.),
Kakadu outperformed other JPEG 2000 libraries and described itself as the
leading JPEG 2000 development kit. It is likely that major companies are
affected by the vulnerabilities we reported, including a Google service.

## Technical Details

In the following sections, we provide necessary background information on
[JPEG 2000](https://en.wikipedia.org/wiki/JPEG_2000).
Then, we outline our vulnerability discovery process and explain the
vulnerabilities we exploited. Finally, we document our exploitation strategy,
along with the obstacles we encountered during exploit development.

We provide code snippets taken from decompiled code of the [freely available demonstration](https://kakadusoftware.com/documentation-downloads/downloads/)
binaries of Kakadu. The code snippets we show are simplified for clarity. We use
the binaries of version 8.41 of the demo binaries to generate code snippets for
this report.

### JPEG 2000 Technical Background

[JPEG 2000](https://en.wikipedia.org/wiki/JPEG_2000) is an image compression
standard and coding system. To simplify things, the file-format itself can be
divided into two concepts that need to be understood: Boxes and Codestream
Segment Markers.

#### JP2 Boxes

Boxes are Length-Type-Value containers for Metadata relating to the image. They
contain information such as the image width, height and provide information
about the color. They can also contain data such as the position of the actual
Codestream within the image.

According to the standard, a Box has the following fields:

| **Field** | **Size** | **Description** |
| --- | --- | --- |
| **`LBox`** | 32 bits | Length of the box. |
| **`TBox`** | 32 bits | Box type, typically a 4-byte ASCII sequence with the box name.<br> For example, `ftyp` is the name for the _File-Type_ box. |
| **`XLBox`** | 64 bits | Extended length, only present if _Lbox_ is set to 1. |
| **`DBox`** | Variable | Box data (variable length based on _LBox_ and the box type). |

Boxes can also contain other Boxes. For example, the JP2 header Box may contain
Boxes that provide more information about the image, such as a `colr` (Color)
Box. The following graphic shows how an image could be organized:

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum02.png)

#### Codestream Segment Markers

The Codestream contains the actual image data and is located within a Codestream
Box. The CodeStream consists of Type-Length-Value containers called Segment
Markers.

The first 2 bytes are a unique value telling the parser what Segment Marker is
currently being parsed. Segment Markers always begin with _0xFF_. The second
byte is a code and can have any value in the range _0x01_ to _0xFE_.

The next two bytes are a length field of the marker-specific data that follows.
The length contains the two bytes for the length itself. As the length field is
only 2 bytes large, a Segment Marker can have a maximum length of 65535.

#### Tiles

The rectangular, decompressed image is made up of rectangular tiles. Tiles all
have the same size. Each of the tile's data is compressed individually and can
have completely different parameters for the decoder, such as the number of
decoding passes for example. Importantly, there can be up to 65535 tiles.

Tiles may be included in the codestream in arbitrary order. Each tile must
contain at least two markers, Start-of-Tile (`SOT`) and Start-of-Data (`SOD`).
The `SOT` marker contains a "tile index" field (`Isot`) which determines where
in the image the tile is located. The `SOT` layout is shown below:

| **Field** | **Size** | **Description** |
| --- | --- | --- |
| **`SOT`** | 16 bits | Segment Marker (0xFF90). |
| **`Lsot`** | 16 bits | Marker segment length in bytes (not including the marker). |
| **`Isot`** | 16 bits | Tile index used to calculate the (x, y) coordinates of a tile. |
| **`Psot`** | 32 bits | Length of the tile data. |
| **`TPsot`** | 8 bits | Tile-part index, zero if there are no tile-parts. |
| **`TNsot`** | 8 bits | Number of tile-parts. |

The Start-of-Data (`SOD`) marker is one of the simplest markers and simply
contains the compressed tile data. Note that `SOD` does not itself contain a
length field. Instead, its length is determined by the `Psot` field of the
preceding `SOT` marker.

| **Field** | **Size** | **Description** |
| --- | --- | --- |
| **`SOD`** | 16 bits | Segment Marker (0xFF93). |
| **`Data`** | Variable | Tile data (variable length). |

The X, Y coordinates of a tile can be calculated using only the tile index, the
image width/height, and the tile width/height. From the `SIZ` marker, these
values are _Xsiz_, _Ysiz_, _XTsiz_, _YTsiz_ respectively. The layout of tiles by
index can be shown in the diagram below.

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum06.png)

_Tile dimensions in context of the larger image._

### Service Discovery

We crafted images that rely on Kakadu quirks and features that are only
implemented by Kakadu to fingerprint endpoints that use Kakadu to convert JPEG
2000 images. The feature we rely on is "Codestream fragmentation", a feature
that is defined in the second part of the JPEG 2000 standard. This feature is
explained in more detail in the 'Vulnerability Discovery' section, as it also
allows for an arbitrary file-read.

### Vulnerability Discovery

Aside from reading the JPEG 2000
[standard](https://www.iso.org/standard/78321.html), we invested time in reading
the [Kakadu source code](https://github.com/wallscavesurvey/walls/tree/master/Kakadu6_4) to
understand the parsing flow and internal data structures that we could exploit.
Through fuzzing, we were able to discover an internal variant of
[TALOS-2017-0309](https://talosintelligence.com/vulnerability_reports/TALOS-2017-0309),
an Out-of-Bounds Write on the Heap due to signed integer multiplication.

### Vulnerabilities

In this section, we provide details about 2 vulnerabilities that we discovered.
One is Arbitrary File Read. In short, the Codestream is read by Kakadu as a
linear stream of bytes. However, under the hood, one or more bytes in the
Codestream can be substituted by a local file, allowing for exfiltration of
these files.

The second vulnerability is an Heap Out-Of-Bounds Write due to multiplication
with a signed integer.

#### Arbitrary File Read

The [ISO/IEC 15444-2](https://www.iso.org/standard/81547.html) standard
specifies an extended format for JPEG 2000 files, called JPX, and one feature of
this extended format is the ability to fragment an image's codestream within the
same file, across multiple files, or across multiple URLs on the Internet. This
optional extension as described in the specification is inherently vulnerable.

We found that Kakadu implements this feature, reading data from local files
referenced by a JPX image and using it to build the image's codestream. A high
level visualization of the JPX fragmentation feature is shown below:

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum07.png)

For this, a JPX image needs to include:

- A single Data Reference Box, which contains a list of Data Entry URL Boxes,
each of which contains the path to a file within the local filesystem as a
null-terminated string
- A Fragment Table Box, which contains a single Fragment List Box that specifies
fragments from which to build the continuous codestream

The Fragment table Box has the following fields:

| **Field** | **Size** | **Description** |
| --- | --- | --- |
| **`NF`** | 16 bits | Total number of fragments. |
| **`OFFi`** | 64 bits | Offset to the start of the i-th fragment in the file specified by **`DRi`**, relative to the first byte of the file. |
| **`LENi`** | 32 bits | Length of the i-th fragment. |
| **`DRi`** | 16 bits | Data reference index, determines which file to load fragment data from. If zero, the current file is used. |

By crafting JPX images with these Boxes, we were able to inject into the
codestream precise amounts of bytes read at specific offsets from specific local
files, and have resulting images with such data encoded within their properties
or pixels.

Assuming an environment where we can view the output image after processing, it
is possible to achieve an arbitrary file-read.

In the next subsections, we will describe how we utilized the ability to insert
bytes of local files anywhere into the Codestream to exfiltrate those bytes.

#### Size-based read

The first proof-of-concept we came up with for this arbitrary file read was a
JPX image that would read the first and second bytes (starting from a given
offset) of a given file. One of the Segment markers we mentioned previously is
the `SIZ` Segment marker. It contains multiple 4-byte fields that contain the
decompressed image's width and height. Since we could see the width and height
of the exploit image, we could substitute some of the height and width values
with bytes from a local file and derive those bytes based on the decompressed
image's dimensions.

Since neither the width or the height of an image can be zero, and they are
32-bit unsigned integers, we encoded each as (`0x00`, `0x00`, `0x01`, `read byte`),
thus each would end up being `0x100` \+ the value of the respective read byte,
giving us a range from `0x100` to `0x1FF`.

Given that we control both the file to be read, and the offset to start reading
from, this already represented an exploitable arbitrary file read, with a full
file being leakable by uploading images specifying increasing starting read
offsets.

However, this primitive was insufficient for leaking `/proc/self/maps` as we
could only leak 2 bytes per request. Even though we could use increasing
offsets, the contents would change depending on the worker handling the request.
As a result, the output file would be a mix of different workers.

While leaking through the image size could be improved a little bit by
accurately leaking up to 3 bytes at once in each property, so 6 bytes per JPX
image, it would require huge image sizes that are likely to exceed safety
limits, and also it still wouldn't be enough to leak highly-variable files.

#### Dynamic Tile read

To leak more data in a single image, we needed to either find a single segment
marker with a large array of data that could be reliably decoded from the output
image OR find a segment marker that could be repeated in the image to have some
noticeable effect.

One tempting target is the tile data itself. What if we created an image with a
single large tile, and then used a large number of leaked bytes in the
compressed pixel data within this tile. Unfortunately, the compression applied
to tiles made this impossible. The tile data is encoded using a variable length
encoding technique, and does not permit the _0xFF_ byte in the stream.
Additionally, the compression used in JPEG 2000 is incredibly complex, using
wavelet transforms with dynamic coefficients. The length of the tile and meaning
of the tile changed based on the data that we leaked, and changed in such a way
that almost guaranteed parsing errors.

We set out looking for a segment marker that could be repeated with a useful
effect and settled on the Comment (`COM`) marker. The `COM` marker includes an
arbitrary number of bytes of unstructured data. However, the `COM` marker was
not saved to the output image, otherwise we could have easily leaked data in the
`Ccomi` bytes. In spite of this, the `COM` marker
was valid in any part of the codestream and had variable length, which made it
quite useful for us.

The `COM` marker has the following fields:

| **Field** | **Size** | **Description** |
| --- | --- | --- |
| **`COM`** | 16 bits | Segment Marker (0xFF64). |
| **`Lcom`** | 16 bits | Marker segment length in bytes (not including the marker). |
| **`Rcom`** | 16 bits | String encoding, 0 for binary, 1 for Latin. |
| **`Ccomi`** | 8 bits | Byte of comment data (variable length). |

We devised a mechanism to leak a single byte per tile with a jump table based on
leaked bytes. We used three types of codestream marker to craft this primitive:
Start-of-tile (`SOT`), Comment (`COM`), and Start-of-Data (`SOD`).

For each tile, we included a `COM` marker with variable length depending on a
leaked byte (`d<sub>i</sub>`). We then included a table of 256 entries, each
with tile data and another `COM` marker. In each entry, we included tile data
encoding a different pixel color. Each of these entries was exactly 256 bytes
long, meaning depending on the value of the leaked byte, a different entry would
be "chosen". An example of this encoding is shown below:

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum10.png)

_SOT+COM table layout._

Using this mechanism, we managed to leak 20KB of data in a single image. We
could theoretically have leaked 65535 bytes (the maximum number of tiles),
however, Kakadu also limits the number of fragments to 65535 and our exploit
required ~3 fragments per leaked byte.

Since the pixel data is directly influenced by the leaked bytes, the image
itself can be used to visualize the leaked data (which can also be decoded by
examining the pixel values). The following image demonstrates what an output
image could look like, in this case we leaked bytes from Kakadu's `kdu_expand`
binary via `/proc/self/exe`.

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum11.png)

_Info leak of `/proc/self/exe` with Kakadu's `kdu_expand` binary._

This would have enabled the attacker to build ROP chain gadgets and gain an
understanding of the internals of the service, allowing for
Remote-Code-Execution without previous insider knowledge. Additionally,
`/proc/self/maps` and `/proc/self/environ` could be leaked to further gain an
understanding of the targeted environment. Another attack-path that opens up
with this primitive is leaking memory contents via `/proc/self/mem`.

#### Heap Overflow

The `SIZ` Segment Marker contains information about the size of the decompressed
image. The relevant `SIZ` marker fields are shown below:

| **Field** | **Size** | **Description** |
| --- | --- | --- |
| **`SIZ`** | 16 bits | Segment Marker (0xFF51). |
| **`Lsiz`** | 16 bits | Marker segment length in bytes (not including the marker). |
| **`Xsiz`** | 32 bits | Width of the reference grid. |
| **`Ysiz`** | 32 bits | Height of the reference grid. |
| **`XTsiz`** | 32 bits | Width of one reference tile with respect to the reference grid. |
| **`YTsiz`** | 32 bits | Height of one reference tile with respect to the reference grid. |
| **`Csiz`** | 16 bits | Number of components in the image (e.g. RGB). |

The final size of decompressed image data in memory is calculated as follows:

_Height \* Width \* Number of Components_

_Height_ and _Width_ correspond to _Xsiz_ and _Ysiz_ and can be fully
controlled. The number of _Components_ can also be controlled via the _Csiz_
field, but is limited to 16384 by the standard.

The multiplication above does not overflow when making the allocation for the
output image buffer, as Kakadu calls a Google internal callback which utilizes
8-byte integers to perform the multiplication:

```
  size_t buf_length = 0;
  size_t area = 0;
  if (!util_intops::SafeMultiply(width, height, &area)) {
    LOG(ERROR) << "Integer overflow when computing width*height.";
    return false;
  }

  if (!util_intops::SafeMultiply(area, num_components, &buf_length)) {
    LOG(ERROR) << "Integer overflow when computing area*num_components.";
    return false;
  }
```

However, an Integer Overflow occurs while writing to the image data as Kakadu
continues to use 4-byte variables. When writing a multi-row Tile, Kakadu writes
the tile data row by row, meaning it writes _Width \* Number of Components_ bytes
per-row.

Once the first row has been written, it advances a pointer to the next row by
adding the result of _Width \* Number of Components_ to the pointer. This
addition is done using a signed, 4-byte integer. As a result, the value can
overflow and the pointer points outside the image.

The `row_gap` is calculated in the snippet shown below, which is the 4-byte
signed integer that is added to the row pointer when writing row-by-row:

```
// from kdu_buffered_expand
00436eb4  int32_t row_gap
00436eb4  if (row_gaps == 0)
00436f10    row_gap = sample_gap * component_state->row_width
00436eb6  else
00436eb6    row_gap = *(row_gaps + i)
00436ebd  *(component_state - 8) = row_gap
```

Because the width can be controlled, we were able to write controlled data
backwards in memory with a controlled distance. This proved to be a powerful
primitive as will be discussed later in the 'Exploitation' section.

The following image visualizes the Out-Of-Bounds Write logic:

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum13.png)

### Exploitation

With our two primitives, we devised the following plan to achieve Remote-Code-Execution impact:

1. Use the info leak to read `/proc/self/maps` and learn the address of the
heap, executable, etc.
2. Send a second image to exploit the heap overflow, corrupting a predictable
object and obtaining code execution in the service
    a. The image reads a known byte from `/proc/self/mem` based on the address leaked in step 1. If this step fails, the exploit is not triggered. We do this to ensure the exploit triggers on the same worker with the known address layout
3. Run proof-of-concept code to verify Remote-Code-Execution impact
4. Perform all of the above with no impact to users

At this point, we set to work building the exploit, starting with exploration of
the heap layout.

#### Heap Overflow Distance

Using the heap overflow, we can write backwards in memory by a known, large
distance. To exploit this primitive, we had to gain an understanding of where
our image would get allocated on the Heap, as its location played an important
role in what data we could overwrite.

Because our image width is large, the memory requested for pixel data is over
4GB. Our target uses [tcmalloc](https://google.github.io/tcmalloc/overview.html)
as its allocator, which has specific behavior with large allocations that we can
use to our advantage. If the heap does not have available memory for the large
allocation, tcmalloc will expand the heap and place the allocation in a
predictable location. This effect can be observed in `/proc/self/maps` before
and after our allocation. When we submit an image of width `0x0040000000`, the
requested allocation is `0x0200000000` bytes.

|     |
| --- |
| `<br>      # /proc/self/maps before allocation<br>      256400000000-256432600000 ---p 032600000 00:00 0  [anon:tcmalloc_region_NORMAL]<br>      256432600000-25643d600000 rw-p 00b000000 00:00 0  [anon:tcmalloc_region_NORMAL]<br>      25643d600000-25643d7c0000 rw-p 0001c0000 00:00 0  [anon:tcmalloc_region_NORMAL]<br>      25643d7c0000-256440000000 rw-p 002840000 00:00 0  [anon:tcmalloc_region_NORMAL]<br>` |
| `<br>      # /proc/self/maps after allocation<br>      256400000000-256431400000 ---p 031400000 00:00 0  [anon:tcmalloc_region_NORMAL]<br>      256431400000-25643d600000 rw-p 00c200000 00:00 0  [anon:tcmalloc_region_NORMAL]<br>      25643d600000-25643d7c0000 rw-p 0001c0000 00:00 0  [anon:tcmalloc_region_NORMAL]<br>      25643d7c0000-256640000000 rw-p 202840000 00:00 0  [anon:tcmalloc_region_NORMAL]<br>` |

To accommodate this request, tcmalloc extends the `25643d7c0000-256440000000`
range to `25643d7c0000-256640000000`. This increase is exactly `0x0200000000`
bytes and the image buffer is allocated at address `256440000000`. Knowing the
address of our image buffer is incredibly helpful, as it allows us to calculate
the exact addresses we overwrite with our heap overflow.

#### 808080 Apocalypse

One problem with our heap overflow primitive is the large amount of data we must
write to the heap. Additionally, due to our large allocation, there is often a
large gap between our image buffer and any useful objects on the heap. We began
experimenting with different overflow distances and tile widths to find the
optimal values for more reliable objects. We crafted an image with a single tile
containing pixel data of all `0x41` and a dynamic width and tile width. We
fuzzed these values against a copy of the production job. We recorded the crash
locations and registers for each attempt to narrow down the optimal conditions.

After a few hours of experimentation, we were crashing reliably in the following
objects related to Kakadu:

- `kd_supp_local::jx_composition::~jx_composition`
- `kdu_supp::jp2_input_box::close`
- `kd_core_local::kd_precinct_server::get`
- `kd_supp_local::jx_codestream_source::~jx_codestream_source`
- `kd_supp_local::jx_layer_source::~jx_layer_source`
- `kd_supp_local::kdsd_tile::process`
- `kdu_core::kdu_params::access_unique`
- `kdu_supp::kdu_stripe_decompressor::pull_common`
- and a few crashes in non-Kakadu objects

However, while we sometimes saw segfaults on a controlled address (e.g.
`0x4141414141414141`), we often saw segfaults for the address
`0x8080808080808080`. In fact, the majority of our crashes at the time looked
something like the following:

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum14.png)

This value was nowhere in our input pixel data, but was being sprayed everywhere
over the heap. As a result, we were corrupting random objects with _0x80_'s and
segfaulting unpredictably. We dubbed this uncontrolled behavior the "808080 Apocalypse".
After a few hours of head scratching, we realized that Kakadu was writing our
crafted _0x41_ tile, followed by hundreds of tiles with "uninitialized" pixel
data set to _0x80_ (an arbitrary default value used by Kakadu).

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum15.png)

The 808080 Apocalypse would make exploitation incredibly difficult, since these
_0x80_ tiles almost always clobbered random objects on the heap. However, within
the tile processing code, we found a Kakadu-specific technique to write a single
tile and then cause an error, skipping the writes for uninitialized tiles. The
Start of tile-part (`SOT`) marker contains a 16-bit parameter `Isot`, which
indicates the tile index of the current tile.

If Kakadu encounters a tile index greater than the number of possible tiles in
the image, it throws an error and stops writing pixel data. We crafted our
exploit using the following tiles to write exactly one tile worth of controlled
data:

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum16.png)

Rendering this image threw the following error:

```
Corrupt SOT marker segment found in codestream: tile-number lies outside
  the range of available tiles derived from the SIZ marker segment.
```

We collected metrics on the observed crash fingerprints and after rolling out
the above fix to our exploit, observed a sharp increase in `~jx_composition`
crashes and the 808080 Apocalypse had ended.

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum17.png)

_Visualization of crash fingerprint prevalence over time._

#### Finding a reliable gadget on the heap

With the 808080 Apocalypse solved, we continued searching for an object to
target on the heap. As tcmalloc utilizes randomization, finding such a gadget
turned out to be fairly difficult. However, since we would reliably know the
memory location of the image buffer from which we would write backwards into the
Heap at a controlled offset up to -2GB, we had an "arbitrary Heap write
primitive", if the Heap of the worker was smaller than 2GB. That means we could
overwrite any object on the Heap, given we know its location.

#### Global Heap Pointers

Using this primitive, our first approach was to use the arbitrary file-read to
read `/proc/self/mem`. The idea was to find a global variable that points into
the heap. By doing this, we could bypass tcmalloc's randomization and write at a
known location. In theory, this could have resulted in a 100% reliable exploit,
as we could overwrite an object at a known location every single time. However,
this approach had one large issue:

Although we could reliably write to a known object, we did not have control over
the size that was written, which was around ~20KB on average. We did not find an
exploitable object of this size that was pointed to by a global variable. That
meant we would overwrite other, random data on the heap which would often lead
to an uncontrolled crash as another thread would use the corrupted data before
our target object would do so.

We discussed the approach of reading the data around our target address and
restoring the heap data to prevent these crashes. We did not follow this
approach in the end as we discovered another gadget and came to the conclusion
that even if we restore the data, there would still be a race condition where
the data is corrupted and would lead to a crash.

#### Large allocation to prevent randomization

The next approach we took was to find a way to make Kakadu allocate an array of
objects that when corrupted would yield in a reliable primitive, such as a
vtable overwrite.

After some searching, we found such a primitive which could be triggered by
including a _Composition Layer Extensions Box_ from
[Part 2 of the JPEG 2000](https://www.iso.org/standard/81547.html)
standard. The following, reduced, code-snippet shows the
attacker-controlled allocation:

```
// from kdu_expand
00476140 jx_container_source::parse_info(struct jx_container_source* this)
0047620c   if (jp2_input_box::read(&curr->__offset(0x140).q, &Mjclx) == 0)
00476466     box_reading_error:
00476466     kdu_core::kdu_error::kdu_error(&var_68)
00476473     kdu_core::kdu_error::put_text(&var_68)
00476473     goto label_47647b
00476221    if (jp2_input_box::read(&curr->__offset(0x140).q, &Cjclx) == 0)
00476221      goto box_reading_error
00476236    if (jp2_input_box::read(&curr->__offset(0x140).q, &Ljclx) == 0)
00476236      goto box_reading_error
0047624b    if (jp2_input_box::read(&curr->__offset(0x140).q, &Tjclx) == 0)
0047624b      goto box_reading_error
00476260    if (jp2_input_box::read(&curr->__offset(0x140).q, &Fjclx) == 0)
00476260      goto box_reading_error
0047626c    if (jp2_input_box::read(&curr->__offset(0x140).q, &Sjclx) == 0 && Tjclx != 0)
00476453      goto box_reading_error
// ...
00476875    struct j2_memsafe* allocator = curr->allocator.__offset(0x48).q
00476893    // 0x2c0 = size of individual jx_track_source objects
00476893    // 8 = alignment of allocation
00476893    // Tjclx = number of jx_track_source objects
00476893    struct jx_track_source *track_sources
00476893      = j2_memsafe::alloc(allocator, 0x2c0, 8, Tjclx)
```

An attacker could fully control the `Tjclx` value and make Kakadu allocate an
array of hundreds of megabytes in size. This had the advantages that (1) we
would never corrupt data outside of the array and (2) the size of the array made
it highly likely that we would 'hit it' if we used a memory corruption distance
that was reliable between this array and the output image buffer.

#### Write-What-Where

The destructor of each `jx_track_source` object would at some point call the
destructor of `jx_composition`, which in turn would call`jp2_input_box::close()`
method on a `jp2_input_box` object that was an inline member. Since we assume
that we fully control all fields in the inline objects due to our memory
corruption, we could trigger an arbitrary write primitive. A simplified version
of the corresponding `close()` code is shown in the snippet below:

```
// from kdu_buffered_expand
0041e800  uint64_t kdu_supp::jp2_input_box::close(struct jp2_input_box* this)
0041e812    if (this->is_opened != 0)
0041e840      bool dynamic_length = this->dynamic_length
0041e847      this->is_opened = false
0041e86d      struct jp2_input_box* parent_box = this->parent_box
0041e874      if (parent_box != 0)
0041e876        uint64_t next_box_position = this->next_box_position
0041e8b9        if (next_box_position == 0 && dynamic_length != 0)
0041e8bb          uint64_t box_position = this->box_position
0041e8c2          parent_box->__offset(0x96).b = 1
0041e8c9          parent_box->box_position = box_position
```

`parent_box` is a pointer we could fully control. If the `dynamic_length` value
was set to `true` and `next_box_position` was 0, we could write to
`parent_box-152` (the offset of the `box_position` member). We could write a
fully controlled 8 byte value.

Since we could corrupt an array of these objects, we could trigger the
arbitrary-write multiple times, making it a powerful primitive.

Unfortunately, while the `jx_track_source` array was reliably allocated _near_
our image buffer, the exact offset varied. To avoid unexpected behavior, we
needed to know the precise object alignment modulo the size of the object (696
bytes). This way, we could guarantee that our heap overflow could precisely
overwrite a slice of objects from the array.

#### Exploit Reliability Engineering

_Or, "finding a jx\_comp needle in a haystack"._

We puzzled over the object alignment problem for some time, hoping that with
enough experimentation we could find alignments that were more likely based on
the heap layout. There were some patterns in the alignment – approximately 14%
shared the same offset, but this wasn't reliable enough for us to use in
production since guessing wrong meant crashing the service.

If only we had a way to check the object alignment dynamically at runtime... And
then if only we had a way to dynamically change the exploit payload based on the
object alignment...

_Enter, stage right: The Kha-Kha Slide._

![](https://storage.googleapis.com/bughunters-article-images/blogs/kakadum18.png)

Using our experience from crafting the Dynamic Tile info leak, we created a
mechanism within the codestream to allow us to dynamically change the tile data
written using the heap overflow based on the data from the heap itself by
reading `/proc/self/mem`.

At the start of our slide, we include an `SOT` whose length encompasses the
entire slide. This means that somewhere within the slide, there must be a `SOD`
with tile data. However, there can also be an arbitrary number of other markers
before the `SOD`. We then craft a series of 696 lookup tables for each possible
offset of the `jx_composition` object. Using this mechanism, we effectively
search memory for a specific byte value that tells us the object offset.

Each table starts with a `COM` marker whose length is based on a leaked byte
from `/proc/self/mem`. Within the table are 256 additional `COM` markers, one
for each possible leaked byte value. Each `COM` has a variable length to jump
over the other markers and into the "`COM S`" marker at the end of the table. If
we find the byte value we're looking for ( _0x41_ in the above diagram), we jump
directly to a `SOD` marker with tile data specifically crafted for that offset.
If we do not find the byte we're looking for, the "`COM S`" marker jumps over
the exploit and onto the next `COM` table. We proceed through each `COM` table,
looking at a different address each time, hoping to find our target byte.
Eventually, one of the `COM` tables finds the byte and triggers the exploit.

The darker colored path in the diagram above shows an example path through the
`COM` tables. For example, if the first few bytes of memory are `01417fff`,
the parser will see the following markers:

```
// start of tile, index 0
SOT 00 0a 00 01 TL 00 01
// leaked byte at offset 1 is 0x01, jump over 1 COM
COM 01 06 00 00 41 41 <256 bytes>
// jump to end of COM table
COM L2 L2 00 00 <L2 bytes>
// jump over exploit to next COM table
COM SS SS 00 00 41 41
// leaked byte at offset 2 is 0x41, jump to exploit
COM 41 06 00 00 41 41 <16640 bytes>
// exploit with objects aligned at offset 2
SOD exploit[d2]
// jump to next COM table, continue the slide
COM E2 E2 00 00 41 41
...
// start of tile, index 0xffff to avoid 808080 apocalypse
SOT 00 0a ff ff 00 00 00 00 00 01
```

The `jx_composition` object is mostly initialized to zero, with a few heap
pointers and vtables. We can choose one of these vtables with a unique byte in
the pointer. For the production binary, the vtable address we chose was
`0x3f5a04f0`. The least significant byte, `0xf0`, was unique within the
`jx_composition` object, which gave us an oracle byte to search for with the
_Kha-Kha Slide_.

The Kha-Kha Slide increased our reliability significantly. However, we still had
one last bit of randomness to solve: the load balancer. Our exploit requires two
requests, one to leak `/proc/self/maps` and the next to perform the heap
overflow. Different workers might process these two requests. If this happened,
our exploit would have the wrong addresses and certainly segfault. To harden our
second payload against invalid addresses, we added one last info leak early in
the codestream. While reading fragments, if `fread()` returns zero, Kakadu will
exit early and set an error for the current marker. For most markers, Kakadu
simply ignores the error and continues parsing. However, for the `SIZ` marker,
Kakadu will throw the following error and skip all further parsing:

```
Code-stream must contain a valid SIZ marker segment, immediately after the SOC marker!
```

If we `seek()` to an address in `/proc/self/mem` that is not mapped, the
subsequent `fread()` will return zero (corresponding to an I/O error). We can
simply embed a known value from `/proc/self/mem` within the `SIZ` marker such
that, with a valid memory layout, the value completes the `SIZ` marker, and with
an invalid memory layout, we bail out and skip processing the image altogether.

We chose the `Rsiz` field of the `SIZ` marker, which has a null byte in it. For
the leak address, we chose the first null byte in the memory region containing
our executable. And with that, we crossed our final reliability hurdle.

#### Summary

_Putting it all together._

We utilized an arbitrary file-read in Kakadu to obtain information about the
server environment. Similar effects can be achieved with an arbitrary memory
read primitive, an example of which is another [bug CVR discovered](https://github.com/google/security-research/security/advisories/GHSA-r7c8-c243-93rg)
in PostgreSQL that allowed the attacker to fully obtain the target binary.

We then used the same file-read primitive to use "Conditional Corruption", a
technique CVR has published in 2023 when [targeting ClamAV](https://www.hexacon.fr/conference/speakers/#remotely_exploiting_antivirus_engine)
and has subsequently been awarded with a [Pwnie award](https://www.linuxadictos.com/en/estos-son-los-ganadores-de-los-pwnie-awards-2023.html).
This technique allowed us to target the same worker we leaked information from
in the first step of the exploit. Doing so greatly improves reliability and
removes chance from the exploit.

We used "Conditional Corruption" again to verify our exploit payload would
overwrite the correct data on the Heap before triggering to ensure reliability.
This allowed us to gain a write-what-where primitive.

With our info leak and the write-what-where primitive, we had the ability to
locate and modify global variables. We were able to hijack the control flow of
the process and execute arbitrary code without impact to users.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab