#!/usr/bin/env python
# if running in py3, change the shebang, drop the next import for readability (it does no harm in py3)
from collections import defaultdict
import hashlib
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename: Path, first_chunk_only=False, hash=hashlib.sha1):
    hashobj = hash()
    with open(filename, "rb") as file_object:
        if first_chunk_only:
            hashobj.update(file_object.read(1024))
        else:
            # Reading in chunks to handle large files
            for chunk in iter(lambda: file_object.read(4096), b''):
                hashobj.update(chunk)
        return hashobj.hexdigest()


def check_for_duplicates(path: Path) -> int:
    """Checks files under the given directory path for duplicates and removes them."""
    hashes_by_size = defaultdict(list)  
    hashes_on_1k = defaultdict(list) 
    hashes_full = {}

    files = list(path.glob("*.*"))

    for file_path in files:
        file_size = file_path.stat().st_size
        hashes_by_size[file_size].append(file_path)

    # Find potential duplicates based on 1K hash.
    def hash_first_1k(file_path):
        small_hash = get_hash(file_path, first_chunk_only=True)
        if small_hash:
            file_size = file_path.stat().st_size
            hashes_on_1k[(small_hash, file_size)].append(file_path)

    with ThreadPoolExecutor() as executor:
        executor.map(hash_first_1k, [fp for flist in hashes_by_size.values() for fp in flist if len(flist) > 1])

     # Check full file hash for actual duplicates
    duplicates = []

    def check_full_hash(file_path):
        """ Check full hash (if applicable) and identify duplicates. """
        full_hash = get_hash(file_path)
        if full_hash:
            if full_hash in hashes_full:
                duplicates.append(file_path)
            else:
                hashes_full[full_hash] = file_path

    files_with_same_1k = [fp for flist in hashes_on_1k.values() for fp in flist if len(flist) > 1]
    with ThreadPoolExecutor() as executor:
        executor.map(check_full_hash, files_with_same_1k)

    # Delete duplicated files
    for file in duplicates:
        file.unlink()

    return len(duplicates)


def handle_photo_processing(photos, photos_path, duplicateflag):
    if duplicateflag:
        logging.info("Check for duplicates")
        duplicates_count = check_for_duplicates(photos_path)
        logging.info(f"Duplicates removed: {duplicates_count}")
        logging.info(f"Total downloaded: {len(photos) - duplicates_count} photo")
    else:
        logging.info(f"Total downloaded: {len(photos)} photo")