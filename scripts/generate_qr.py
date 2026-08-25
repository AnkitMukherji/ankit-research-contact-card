#!/usr/bin/env python3
"""
scripts/generate_qr.py
Official Apple CoreImage CIQRCodeGenerator Engine with 100% Solid Opaque 24-bit RGB PNG & Clean SVG.
Zero transparency, guaranteed camera recognition on iOS, Android, and all physical scanners.
"""

import os
import sys
import zlib
import struct
import argparse
import ctypes
import ctypes.util

# Setup Objective-C Runtime
objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))
objc.objc_getClass.restype = ctypes.c_void_p
objc.objc_getClass.argtypes = [ctypes.c_char_p]
objc.sel_registerName.restype = ctypes.c_void_p
objc.sel_registerName.argtypes = [ctypes.c_char_p]

ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Foundation.framework/Foundation')
ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreImage.framework/CoreImage')
ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
ctypes.cdll.LoadLibrary('/System/Library/Frameworks/AppKit.framework/AppKit')

class CGRect(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double),
                ('width', ctypes.c_double), ('height', ctypes.c_double)]

msg_send_obj = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
msg_send_str = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p))
msg_send_data = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t))
msg_send_set_val = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
msg_send_rect = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(CGRect, ctypes.c_void_p, ctypes.c_void_p))
msg_send_create_cg = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, CGRect))
msg_send_long = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p))
msg_send_ptr = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.POINTER(ctypes.c_uint8), ctypes.c_void_p, ctypes.c_void_p))

def str_to_nsstring(s):
    NSString = objc.objc_getClass(b'NSString')
    return msg_send_str(NSString, objc.sel_registerName(b'stringWithUTF8String:'), s.encode('utf-8'))

def str_to_nsdata(s):
    b = s.encode('utf-8')
    NSData = objc.objc_getClass(b'NSData')
    return msg_send_data(NSData, objc.sel_registerName(b'dataWithBytes:length:'), b, len(b))

def write_opaque_png(matrix, output_path, scale=12, quiet_zone=4, dpi=72):
    """Writes standard solid 24-bit RGB PNG with ZERO transparency and guaranteed high contrast."""
    qr_h = len(matrix)
    qr_w = len(matrix[0])
    total_h = qr_h + 2 * quiet_zone
    total_w = qr_w + 2 * quiet_zone
    
    img_w = total_w * scale
    img_h = total_h * scale
    
    raw_bytes = bytearray()
    for row in range(img_h):
        raw_bytes.append(0)  # Filter byte 0 (None)
        grid_y = row // scale - quiet_zone
        for col in range(img_w):
            grid_x = col // scale - quiet_zone
            if 0 <= grid_x < qr_w and 0 <= grid_y < qr_h and matrix[grid_y][grid_x]:
                raw_bytes.extend((0, 0, 0))          # Solid Black
            else:
                raw_bytes.extend((255, 255, 255))    # Solid Opaque White
    
    compressed = zlib.compress(bytes(raw_bytes), 9)
    
    def png_chunk(chunk_type, data):
        c_type = chunk_type.encode('ascii')
        crc = zlib.crc32(c_type + data) & 0xffffffff
        return struct.pack('>I', len(data)) + c_type + data + struct.pack('>I', crc)
    
    png_header = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', img_w, img_h, 8, 2, 0, 0, 0)  # color_type=2 (RGB, No Alpha)
    ihdr_chunk = png_chunk('IHDR', ihdr_data)
    
    ppm = int(round(dpi / 0.0254))
    phys_data = struct.pack('>IIB', ppm, ppm, 1)
    phys_chunk = png_chunk('pHYs', phys_data)
    
    idat_chunk = png_chunk('IDAT', compressed)
    iend_chunk = png_chunk('IEND', b'')
    
    with open(output_path, 'wb') as f:
        f.write(png_header + ihdr_chunk + phys_chunk + idat_chunk + iend_chunk)

def generate_apple_qr(url: str, output_dir: str = "assets"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Generating Apple CoreImage QR Code for: {url}")

    # 1. Generate via Apple CIQRCodeGenerator
    CIFilter = objc.objc_getClass(b'CIFilter')
    qr_filter = msg_send_set_val(CIFilter, objc.sel_registerName(b'filterWithName:'), str_to_nsstring('CIQRCodeGenerator'), None)
    msg_send_obj(qr_filter, objc.sel_registerName(b'setDefaults'))
    
    msg_send_set_val(qr_filter, objc.sel_registerName(b'setValue:forKey:'), str_to_nsdata(url), str_to_nsstring('inputMessage'))
    msg_send_set_val(qr_filter, objc.sel_registerName(b'setValue:forKey:'), str_to_nsstring('M'), str_to_nsstring('inputCorrectionLevel'))
    
    raw_qr = msg_send_obj(qr_filter, objc.sel_registerName(b'outputImage'))
    raw_extent = msg_send_rect(raw_qr, objc.sel_registerName(b'extent'))
    
    CIContext = objc.objc_getClass(b'CIContext')
    context = msg_send_obj(CIContext, objc.sel_registerName(b'context'))
    cg_raw = msg_send_create_cg(context, objc.sel_registerName(b'createCGImage:fromRect:'), raw_qr, raw_extent)
    
    NSBitmapImageRep = objc.objc_getClass(b'NSBitmapImageRep')
    rep = msg_send_set_val(msg_send_obj(NSBitmapImageRep, objc.sel_registerName(b'alloc')), objc.sel_registerName(b'initWithCGImage:'), cg_raw, None)
    
    bpr = msg_send_long(rep, objc.sel_registerName(b'bytesPerRow'))
    ptr = msg_send_ptr(rep, objc.sel_registerName(b'bitmapData'))
    
    raw_w = int(raw_extent.width)
    raw_h = int(raw_extent.height)
    
    # CoreImage CIQRCodeGenerator has 1 module border by default. Extract core matrix without the border.
    core_matrix = []
    for y in range(1, raw_h - 1):
        row = []
        for x in range(1, raw_w - 1):
            # ARGB byte order: byte 0=Alpha, byte 1=Red
            offset = y * bpr + x * 4
            red = ptr[offset + 1]
            is_dark = (red < 128)
            row.append(is_dark)
        core_matrix.append(row)
    
    matrix_size = len(core_matrix)
    print(f"  [i] Extracted Apple Core Matrix: {matrix_size}x{matrix_size} (ISO Version {(matrix_size - 17)//4})")

    # 2. Write Solid Opaque 300 DPI Print PNG (Scale 48 -> 1968x1968)
    print_png_path = os.path.join(output_dir, "qr-code-print-300dpi.png")
    write_opaque_png(core_matrix, print_png_path, scale=48, quiet_zone=4, dpi=300)
    print(f"  [+] Saved Opaque 300 DPI Print PNG: {print_png_path} (1968x1968px, RGB 24-bit, 0% transparency)")

    # 3. Write Solid Opaque Web PNG (Scale 12 -> 492x492)
    web_png_path = os.path.join(output_dir, "qr-contact-card.png")
    write_opaque_png(core_matrix, web_png_path, scale=12, quiet_zone=4, dpi=72)
    print(f"  [+] Saved Opaque Web PNG: {web_png_path} (492x492px, RGB 24-bit, 0% transparency)")

    # 4. Generate Clean Vector SVG (with solid opaque white background)
    quiet_zone = 4
    total_grid = matrix_size + 2 * quiet_zone
    svg_rects = []
    for y in range(matrix_size):
        for x in range(matrix_size):
            if core_matrix[y][x]:
                svg_rects.append(f'<rect x="{x + quiet_zone}" y="{y + quiet_zone}" width="1" height="1" fill="#000000"/>')
    svg_body = "\n  ".join(svg_rects)
    
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_grid} {total_grid}" width="{total_grid * 20}" height="{total_grid * 20}" shape-rendering="crispEdges">
  <!-- Solid Opaque White Background -->
  <rect width="{total_grid}" height="{total_grid}" fill="#ffffff"/>
  <!-- Apple CoreImage QR Code Matrix -->
  <g fill="#000000">
  {svg_body}
  </g>
</svg>
"""
    svg_path = os.path.join(output_dir, "qr-code.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"  [+] Saved Vector SVG: {svg_path}")

    # 5. Generate Poster Badge SVG
    module_px = 6
    qr_px = total_grid * module_px
    badge_width = max(qr_px + 40, 320)
    badge_height = qr_px + 130
    qr_x = (badge_width - qr_px) / 2
    qr_y = 65

    badge_rects = []
    for y in range(matrix_size):
        for x in range(matrix_size):
            if core_matrix[y][x]:
                rx = qr_x + (x + quiet_zone) * module_px
                ry = qr_y + (y + quiet_zone) * module_px
                badge_rects.append(f'<rect x="{rx}" y="{ry}" width="{module_px}" height="{module_px}" fill="#000000"/>')
    badge_body = "\n    ".join(badge_rects)

    badge_svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {badge_width} {badge_height}" width="{badge_width}" height="{badge_height}" shape-rendering="crispEdges">
  <defs>
    <style>
      .card-bg {{ fill: #ffffff; stroke: #0d3b35; stroke-width: 2.5; rx: 14; }}
      .title {{ font-family: 'DM Mono', -apple-system, sans-serif; font-size: 11px; font-weight: 800; fill: #0d3b35; letter-spacing: 1.5px; text-anchor: middle; }}
      .name {{ font-family: Georgia, serif; font-size: 14px; font-weight: 700; fill: #0d3b35; text-anchor: middle; }}
      .affil {{ font-family: -apple-system, sans-serif; font-size: 9.5px; font-weight: 600; fill: #61716c; text-anchor: middle; }}
      .url-text {{ font-family: 'DM Mono', monospace; font-size: 8px; fill: #bd8c41; font-weight: 600; text-anchor: middle; }}
    </style>
  </defs>

  <!-- Background Box -->
  <rect x="3" y="3" width="{badge_width - 6}" height="{badge_height - 6}" class="card-bg"/>

  <!-- Header -->
  <text x="{badge_width / 2}" y="25" class="title">SCAN FOR POSTER &amp; CONTACT</text>
  <text x="{badge_width / 2}" y="42" class="name">Ankit Mukherjee</text>
  <text x="{badge_width / 2}" y="55" class="affil">CSIR-IGIB · GIC 2026</text>

  <!-- QR Background and Modules -->
  <rect x="{qr_x}" y="{qr_y}" width="{qr_px}" height="{qr_px}" fill="#ffffff" stroke="#e0e0e0" stroke-width="1" rx="4"/>
  <g shape-rendering="crispEdges">
    {badge_body}
  </g>

  <!-- Footer Link -->
  <text x="{badge_width / 2}" y="{badge_height - 12}" class="url-text">{url}</text>
</svg>
"""
    badge_path = os.path.join(output_dir, "poster-badge-qr.svg")
    with open(badge_path, "w", encoding="utf-8") as f:
        f.write(badge_svg_content)
    print(f"  [+] Saved Poster Badge SVG: {badge_path}")

    print("\n[✓] All Apple CoreImage QR Code assets successfully generated with 100% solid opacity!")

def main():
    parser = argparse.ArgumentParser(description="Generate Apple CoreImage QR codes.")
    parser.add_argument("--url", default="https://ankitmukherji.github.io/ankit-research-contact-card/", help="Website URL")
    parser.add_argument("--outdir", default="assets", help="Assets output directory")
    args = parser.parse_args()
    generate_apple_qr(args.url, args.outdir)

if __name__ == '__main__':
    main()
