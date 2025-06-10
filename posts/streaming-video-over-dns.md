---
title: "Streaming Bad Apple Over DNS"
date: "2025-06-09"
description: "Streaming the classic 'Bad Apple!!' music video through DNS queries, because apparently I have too much time and not enough sense."
---

Sometimes you look at a protocol specification and wonder: "What's the most inappropriate thing I could make this do?" DNS seemed like the perfect victim for this particular experiment. The result? Streaming the classic "Bad Apple!!" music video through DNS queries, because apparently I have too much time and not enough sense.

## The Basic Idea

DNS queries have a structure that can carry data beyond just domain names. By encoding video frame data into the query itself, we can effectively stream video through what's supposed to be a simple name resolution protocol. Each DNS query becomes a packet containing compressed frame data.

The approach breaks down into a few key components:

*   **Convert video frames to binary data (black and white pixels)**
*   **Compress the frame data using Brotli**
*   **Encode it as Base64 and split across DNS label segments**
*   **Send queries with embedded frame data to a custom DNS server**
*   **Decode and display the frames in real-time**

## Frame Processing and Delta Compression

The client loads PNG frames and converts them to binary arrays representing black and white pixels. To reduce bandwidth, I implemented delta compression - only keyframes contain full image data, while intermediate frames contain just the differences (XOR) from the previous frame.

```python
is_keyframe = (frame_number == 1) or (frame_number % KEYFRAME_INTERVAL == 1)

if is_keyframe:
    payload = np.packbits(current_frame_data).tobytes()
else:
    delta = np.bitwise_xor(current_frame_data, previous_frame_data)
    payload = np.packbits(delta).tobytes()
```

The `np.packbits` function compresses 8 boolean values into a single byte, significantly reducing the data size before compression. This optimization proved crucial for fitting frames within DNS query limits.

## DNS Query Construction

DNS labels are limited to 63 characters each, and the entire query can't exceed 253 characters. After Brotli compression and Base64 encoding, the frame data gets chunked into these segments and assembled into a query like:

```
[chunk3].[chunk2].[chunk1].[frame_number].[frame_type].[domain]
```

The chunks are reversed so the DNS server can easily parse them in order. Frame type is either 'k' for keyframe or 'd' for delta frame.

## The Server Side

The DNS server uses the `dnslib` library to handle incoming queries. When a query arrives, it parses the domain name to extract frame data:

```python
def resolve(self, request: DNSRecord, handler):
    qname_str = str(request.q.qname)
    parts = qname_str.rstrip('.').split('.')
    
    # Parse from the end: frame_type, frame_number, then data chunks
    frame_type = parts[-2]  # 'k' or 'd'
    frame_num = int(parts[-3])
    payload_chunks = list(reversed(parts[:-3]))
    payload_str = "".join(payload_chunks)
```

The server decompresses the data, unpacks the bits back to pixel arrays, and either displays a keyframe directly or applies a delta to the previous frame. The display uses `curses` to render ASCII art in the terminal - solid blocks (█) for white pixels, spaces for black.

## Performance and Limitations

The system manages around 15 FPS with reasonable compression, though this depends heavily on frame complexity. Simple scenes with large black areas compress extremely well, while detailed frames can exceed the DNS query size limit and get dropped.

The biggest limitation is the 253-character DNS query limit. Even with aggressive compression, complex frames sometimes can't fit. A production system would need adaptive quality or multi-query frames, but this was more about proving the concept than creating a robust streaming protocol.

## Why This Matters (Sort Of)

Beyond the obvious "because I could" factor, this project demonstrates some interesting concepts:

*   **Protocol abuse can be educational** - Understanding how protocols work by pushing their boundaries
*   **Compression techniques** - Delta encoding and bit-packing are widely applicable
*   **Network programming** - Custom DNS servers and client-server communication
*   **Real-time data processing** - Frame timing, buffering, and synchronization

It's also a reminder that protocols are just agreements, and creative interpretation of those agreements can lead to unexpected possibilities.

## The Code

The implementation consists of two main components: a client that reads video frames and sends DNS queries, and a server that receives queries and displays the video. The client handles frame loading, compression, and timing, while the server manages decompression, delta reconstruction, and terminal rendering.

Both use NumPy for efficient array operations and Brotli for compression. The server leverages Python's `curses` library for terminal graphics, creating a surprisingly smooth viewing experience for what amounts to ASCII art transmitted through DNS.

## Conclusion

Streaming video over DNS is technically impressive and practically useless, which makes it a perfect weekend project. It combines networking, compression, real-time processing, and creative problem-solving into something that definitely shouldn't work but somehow does.

Would I recommend this for actual video streaming? Absolutely not. Was it fun to build and surprisingly educational? Definitely. Sometimes the best projects are the ones that serve no practical purpose beyond satisfying curiosity and pushing boundaries.

The next time someone tells you a protocol can only do one thing, remember that with enough creativity and questionable decision-making, it can probably do something completely different.
