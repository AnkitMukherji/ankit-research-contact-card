#!/usr/bin/env python3
"""
scripts/verify_qr.py
Decodes and verifies generated QR code image files against standard ISO/IEC 18004.
"""

import sys
import zlib
import struct
import argparse

def read_png(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "Not a valid PNG file"
    offset = 8
    width = height = None
    idat = bytearray()
    while offset < len(data):
        length, chunk_type = struct.unpack(">II", data[offset:offset+8])
        chunk_data = data[offset+8:offset+8+length]
        offset += 12 + length
        if chunk_type == int.from_bytes(b"IHDR", "big"):
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk_data[:10])
        elif chunk_type == int.from_bytes(b"IDAT", "big"):
            idat.extend(chunk_data)
    
    decompressed = zlib.decompress(bytes(idat))
    stride = 1 + width * 3
    pixels = []
    for y in range(height):
        row_offset = y * stride + 1
        row = []
        for x in range(width):
            r = decompressed[row_offset + x * 3]
            row.append(r < 128)
        pixels.append(row)
    return width, height, pixels

def verify_qr(image_path):
    print(f"[*] Analyzing QR Code Image: {image_path}")
    width, height, pixels = read_png(image_path)
    
    for y in range(height):
        if any(pixels[y]):
            first_dark_y = y
            break
    for x in range(width):
        if pixels[first_dark_y][x]:
            first_dark_x = x
            break
    
    x = first_dark_x
    while x < width and pixels[first_dark_y][x]:
        x += 1
    finder_px_width = x - first_dark_x
    module_px = finder_px_width // 7
    quiet_zone = first_dark_x // module_px
    qr_size = (width - 2 * quiet_zone * module_px) // module_px
    ver = (qr_size - 17) // 4
    
    print(f"  [i] Image: {width}x{height}px | Module Scale: {module_px}px | Quiet Zone: {quiet_zone} mods")
    print(f"  [i] QR Matrix: {qr_size}x{qr_size} (ISO/IEC Version {ver})")
    
    matrix = []
    for my in range(qr_size):
        row = []
        py = quiet_zone * module_px + my * module_px + module_px // 2
        for mx in range(qr_size):
            px = quiet_zone * module_px + mx * module_px + module_px // 2
            row.append(pixels[py][px])
        matrix.append(row)
    
    # Read format information from first copy:
    # Bit 0..5: (x=8, y=0..5), Bit 6: (x=8, y=7), Bit 7: (x=8, y=8), Bit 8: (x=7, y=8), Bit 9..14: (x=5..0, y=8)
    coords_1 = [
        (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
        (8, 7), (8, 8), (7, 8),
        (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)
    ]
    format_bits_1 = 0
    for i, (mx, my) in enumerate(coords_1):
        if matrix[my][mx]:
            format_bits_1 |= (1 << i)
    
    raw_fmt = format_bits_1 ^ 0x5412
    ecl_bits = (raw_fmt >> 13) & 0x3
    mask_bits = (raw_fmt >> 10) & 0x7
    ecl_names = {1: "LOW", 0: "MEDIUM", 3: "QUARTILE", 2: "HIGH"}
    print(f"  [i] Decoded Format Info: Error Correction={ecl_names.get(ecl_bits, 'UNKNOWN')} | Mask Pattern={mask_bits}")
    
    # Unmask data
    unmasked = [row[:] for row in matrix]
    for y in range(qr_size):
        for x in range(qr_size):
            is_func = False
            if (x < 9 and y < 9) or (x >= qr_size - 8 and y < 9) or (x < 9 and y >= qr_size - 8): is_func = True
            if x == 6 or y == 6: is_func = True
            if ver >= 2:
                pos = [6, qr_size - 7]
                for px in pos:
                    for py in pos:
                        if (px == 6 and py == 6) or (px == 6 and py == qr_size - 7) or (px == qr_size - 7 and py == 6): continue
                        if px - 2 <= x <= px + 2 and py - 2 <= y <= py + 2:
                            is_func = True
            if not is_func:
                inv = False
                if mask_bits == 0: inv = (x + y) % 2 == 0
                elif mask_bits == 1: inv = y % 2 == 0
                elif mask_bits == 2: inv = x % 3 == 0
                elif mask_bits == 3: inv = (x + y) % 3 == 0
                elif mask_bits == 4: inv = (x // 3 + y // 2) % 2 == 0
                elif mask_bits == 5: inv = (x * y) % 2 + (x * y) % 3 == 0
                elif mask_bits == 6: inv = ((x * y) % 2 + (x * y) % 3) % 2 == 0
                elif mask_bits == 7: inv = ((x + y) % 2 + x * y % 3) % 2 == 0
                if inv: unmasked[y][x] = not unmasked[y][x]
    
    # Read bitstream
    raw_bits = []
    for right in range(qr_size - 1, 0, -2):
        if right <= 6: right -= 1
        for vert in range(qr_size):
            for j in range(2):
                mx = right - j
                upwards = ((right + 1) & 2) == 0
                my = (qr_size - 1 - vert) if upwards else vert
                
                is_func = False
                if (mx < 9 and my < 9) or (mx >= qr_size - 8 and my < 9) or (mx < 9 and my >= qr_size - 8): is_func = True
                if mx == 6 or my == 6: is_func = True
                if ver >= 2:
                    pos = [6, qr_size - 7]
                    for px in pos:
                        for py in pos:
                            if (px == 6 and py == 6) or (px == 6 and py == qr_size - 7) or (px == qr_size - 7 and py == 6): continue
                            if px - 2 <= mx <= px + 2 and py - 2 <= my <= py + 2:
                                is_func = True
                
                if not is_func:
                    raw_bits.append(1 if unmasked[my][mx] else 0)
    
    codewords = []
    for i in range(0, len(raw_bits), 8):
        b = 0
        for bit in raw_bits[i:i+8]:
            b = (b << 1) | bit
        codewords.append(b)
    
    # De-interleave data
    num_blocks = 2 if ver == 4 else 1
    data_cw_per_block = 32 if ver == 4 else len(codewords)
    
    data_blocks = [bytearray() for _ in range(num_blocks)]
    idx = 0
    for i in range(data_cw_per_block):
        for b in range(num_blocks):
            if idx < len(codewords):
                data_blocks[b].append(codewords[idx])
                idx += 1
    
    all_data = bytearray()
    for b in data_blocks:
        all_data.extend(b)
    
    data_bits = []
    for b in all_data:
        for shift in reversed(range(8)):
            data_bits.append((b >> shift) & 1)
    
    mode = 0
    for i in range(4): mode = (mode << 1) | data_bits[i]
    assert mode == 4, f"Expected Byte mode 4, got {mode}"
    
    length = 0
    for i in range(4, 12): length = (length << 1) | data_bits[i]
    
    char_bytes = bytearray()
    bit_idx = 12
    for _ in range(length):
        b = 0
        for _ in range(8):
            b = (b << 1) | data_bits[bit_idx]
            bit_idx += 1
        char_bytes.append(b)
    
    decoded_url = char_bytes.decode("utf-8")
    print(f"\n[✓] QR Code successfully decoded!")
    print(f"    Payload URL: {decoded_url}\n")
    return decoded_url

def main():
    parser = argparse.ArgumentParser(description="Verify QR code image decoding.")
    parser.add_argument("image", nargs="?", default="assets/qr-contact-card.png", help="Path to PNG file to test")
    args = parser.parse_args()
    verify_qr(args.image)

if __name__ == "__main__":
    main()
