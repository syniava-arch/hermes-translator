#!/usr/bin/env python3
"""Extract text from RTF file."""
import sys
try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    print("striprtf not available, using basic extraction")
    rtf_to_text = None

path = "/home/stan/.hermes/attachments/Без названия 2.rtf"

if rtf_to_text:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        rtf = f.read()
    text = rtf_to_text(rtf)
    print(text)
else:
    # Basic: strip RTF control sequences
    import re
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        rtf = f.read()
    # Remove control words
    text = re.sub(r'\\[a-zA-Z]+\d*\s?', '', rtf)
    # Remove braces
    text = text.replace('{', '').replace('}', '')
    # Remove Unicode escapes
    text = re.sub(r'\\u\d+\?', '', text)
    print(text)
