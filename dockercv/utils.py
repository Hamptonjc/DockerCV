import sys


def write_to_memory(mapfile, data):
    mapfile.seek(0)
    return mapfile.write(data)


def read_from_memory(mapfile, n_bytes):
    mapfile.seek(0)
    data = mapfile.read(n_bytes)
    return data
    