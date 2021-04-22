import sys


def write_to_memory(mapfile, data):
    mapfile.seek(0)
    mapfile.write(data)


def read_from_memory(mapfile):
    mapfile.seek(0)
    data = mapfile.read(2764800)
    return data
    