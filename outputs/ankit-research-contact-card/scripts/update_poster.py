#!/usr/bin/env python3
"""
scripts/update_poster.py
Quick-runner script to update your conference poster PDF and generate a high-res preview thumbnail.
Zero pip dependencies required (uses built-in macOS PDFKit & CoreGraphics).
"""

import os
import sys
import shutil
import argparse
import ctypes
import ctypes.util

# Load Apple frameworks
objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))
objc.objc_getClass.restype = ctypes.c_void_p
objc.objc_getClass.argtypes = [ctypes.c_char_p]
objc.sel_registerName.restype = ctypes.c_void_p
objc.sel_registerName.argtypes = [ctypes.c_char_p]

ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Foundation.framework/Foundation')
ctypes.cdll.LoadLibrary('/System/Library/Frameworks/AppKit.framework/AppKit')
ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
ctypes.cdll.LoadLibrary('/System/Library/Frameworks/PDFKit.framework/PDFKit')

class CGSize(ctypes.Structure):
    _fields_ = [('width', ctypes.c_double), ('height', ctypes.c_double)]

class CGPoint(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double)]

class CGRect(ctypes.Structure):
    _fields_ = [('origin', CGPoint), ('size', CGSize)]

msg_send_obj = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
msg_send_str = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p))
msg_send_set_val = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
msg_send_ulong = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p))
msg_send_page = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong))
msg_send_box = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(CGRect, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long))
msg_send_thumb = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, CGSize, ctypes.c_long))
msg_send_png = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p))
msg_send_ptr = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.POINTER(ctypes.c_uint8), ctypes.c_void_p, ctypes.c_void_p))

def str_to_nsstring(s: str):
    NSString = objc.objc_getClass(b'NSString')
    return msg_send_str(NSString, objc.sel_registerName(b'stringWithUTF8String:'), s.encode('utf-8'))

def render_poster_preview(pdf_file: str, output_png: str = "assets/poster-preview.png", max_width: float = 1600.0):
    if not os.path.exists(pdf_file):
        print(f"[!] Error: File '{pdf_file}' not found.")
        return False

    abs_path = os.path.abspath(pdf_file)
    print(f"[*] Processing poster PDF: {pdf_file}")

    NSURL = objc.objc_getClass(b'NSURL')
    url = msg_send_set_val(NSURL, objc.sel_registerName(b'fileURLWithPath:'), str_to_nsstring(abs_path), None)

    PDFDocument = objc.objc_getClass(b'PDFDocument')
    doc = msg_send_set_val(msg_send_obj(PDFDocument, objc.sel_registerName(b'alloc')), objc.sel_registerName(b'initWithURL:'), url, None)
    if not doc:
        print(f"[!] Error: Could not parse '{pdf_file}' as a valid PDF.")
        return False

    page_count = msg_send_ulong(doc, objc.sel_registerName(b'pageCount'))
    if page_count == 0:
        print(f"[!] Error: PDF has 0 pages.")
        return False

    page = msg_send_page(doc, objc.sel_registerName(b'pageAtIndex:'), 0)
    bounds = msg_send_box(page, objc.sel_registerName(b'boundsForBox:'), 0)

    w = bounds.size.width
    h = bounds.size.height
    aspect = h / w if w > 0 else 1.33
    target_w = max_width
    target_h = max_width * aspect

    thumb_size = CGSize(target_w, target_h)
    thumb = msg_send_thumb(page, objc.sel_registerName(b'thumbnailOfSize:forBox:'), thumb_size, 0)

    tiff = msg_send_obj(thumb, objc.sel_registerName(b'TIFFRepresentation'))
    NSBitmapImageRep = objc.objc_getClass(b'NSBitmapImageRep')
    rep = msg_send_set_val(NSBitmapImageRep, objc.sel_registerName(b'imageRepWithData:'), tiff, None)

    png_data = msg_send_png(rep, objc.sel_registerName(b'representationUsingType:properties:'), 4, None)
    length = msg_send_ulong(png_data, objc.sel_registerName(b'length'))
    ptr = msg_send_ptr(png_data, objc.sel_registerName(b'bytes'))

    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    with open(output_png, "wb") as f:
        f.write(bytes(ptr[:length]))

    # Sync to outputs folder if it exists
    out_copy = os.path.join("outputs", "ankit-research-contact-card", output_png)
    if os.path.exists(os.path.dirname(out_copy)):
        shutil.copy2(output_png, out_copy)
        # Also copy the PDF itself to outputs
        pdf_out_copy = os.path.join("outputs", "ankit-research-contact-card", os.path.basename(pdf_file))
        shutil.copy2(pdf_file, pdf_out_copy)

    print(f"[✓] Successfully converted '{pdf_file}' -> '{output_png}' ({int(target_w)}x{int(target_h)}px, {length:,} bytes)!")
    print("\nNext step: Run the following to publish your changes live:")
    print("  git add -A")
    print('  git commit -m "Update conference poster PDF and preview thumbnail"')
    print("  git push origin main")
    return True

def main():
    parser = argparse.ArgumentParser(description="Convert poster PDF to high-res preview PNG thumbnail.")
    parser.add_argument("pdf", nargs="?", default="Ankit_Mukherjee_Poster_GIC2026.pdf", help="Path to poster PDF file (default: Ankit_Mukherjee_Poster_GIC2026.pdf)")
    parser.add_argument("--out", default="assets/poster-preview.png", help="Output thumbnail path (default: assets/poster-preview.png)")
    args = parser.parse_args()

    render_poster_preview(args.pdf, args.out)

if __name__ == '__main__':
    main()
