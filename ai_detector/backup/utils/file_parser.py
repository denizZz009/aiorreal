"""Dosya parsing ve metadata okuma"""

import struct
from typing import Dict, Optional
from pathlib import Path


def read_png_chunks(file_path: str) -> Dict[str, bytes]:
    """PNG chunk'larını oku"""
    chunks = {}
    
    with open(file_path, 'rb') as f:
        # PNG signature kontrolü
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            return chunks
        
        while True:
            try:
                # Chunk length
                length_bytes = f.read(4)
                if len(length_bytes) < 4:
                    break
                length = struct.unpack('>I', length_bytes)[0]
                
                # Chunk type
                chunk_type = f.read(4).decode('ascii', errors='ignore')
                
                # Chunk data
                data = f.read(length)
                
                # CRC (skip)
                f.read(4)
                
                chunks[chunk_type] = data
                
                # IEND chunk'ı son chunk
                if chunk_type == 'IEND':
                    break
                    
            except Exception:
                break
    
    return chunks


def extract_png_text_chunks(chunks: Dict[str, bytes]) -> Dict[str, str]:
    """PNG text chunk'larından metadata çıkar"""
    text_data = {}
    
    # tEXt chunks
    if 'tEXt' in chunks:
        try:
            data = chunks['tEXt']
            null_pos = data.find(b'\x00')
            if null_pos > 0:
                keyword = data[:null_pos].decode('latin-1')
                text = data[null_pos+1:].decode('latin-1', errors='ignore')
                text_data[keyword] = text
        except Exception:
            pass
    
    # iTXt chunks (international text)
    if 'iTXt' in chunks:
        try:
            data = chunks['iTXt']
            null_pos = data.find(b'\x00')
            if null_pos > 0:
                keyword = data[:null_pos].decode('latin-1')
                # Simplified parsing
                text_data[keyword] = data[null_pos:].decode('utf-8', errors='ignore')
        except Exception:
            pass
    
    return text_data


def read_jpeg_segments(file_path: str) -> Dict[str, bytes]:
    """JPEG APP segment'lerini oku"""
    segments = {}
    
    with open(file_path, 'rb') as f:
        # JPEG signature
        if f.read(2) != b'\xff\xd8':
            return segments
        
        while True:
            try:
                marker = f.read(2)
                if len(marker) < 2:
                    break
                
                if marker[0] != 0xff:
                    break
                
                marker_type = marker[1]
                
                # SOS marker (Start of Scan) - data başlıyor
                if marker_type == 0xda:
                    break
                
                # Length
                length_bytes = f.read(2)
                if len(length_bytes) < 2:
                    break
                length = struct.unpack('>H', length_bytes)[0]
                
                # Data (length includes the 2 bytes of length itself)
                data = f.read(length - 2)
                
                # APP0-APP15 markers
                if 0xe0 <= marker_type <= 0xef:
                    app_name = f"APP{marker_type - 0xe0}"
                    segments[app_name] = data
                
            except Exception:
                break
    
    return segments


def parse_mp4_atoms(file_path: str, max_read: int = 10 * 1024 * 1024) -> Dict[str, bytes]:
    """MP4 atom'larını parse et (basitleştirilmiş)"""
    atoms = {}
    
    with open(file_path, 'rb') as f:
        data = f.read(max_read)
    
    # Basit atom arama
    pos = 0
    while pos < len(data) - 8:
        try:
            size = struct.unpack('>I', data[pos:pos+4])[0]
            atom_type = data[pos+4:pos+8].decode('ascii', errors='ignore')
            
            if size < 8 or size > len(data) - pos:
                pos += 1
                continue
            
            atom_data = data[pos+8:pos+size]
            atoms[atom_type] = atom_data
            
            pos += size
        except Exception:
            pos += 1
    
    return atoms
