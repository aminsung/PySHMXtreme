#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2016 RoMeLa"
__date__ = "August 23, 2016"

__version__ = "0.0.1"
__status__ = "Final"

import mmap
import pdb
import collections

import numpy as np
import posix_ipc

ROBOT_NAME = "CPro"

class SHMSegment(object):
    def __init__(self, blocks, root_name=None):
        '''
        Create a new shared memory segment that will nicely keep all the different information organized
        in a block of memory.

        :params blocks: Blocks of memory to organize in the segment
        :params root_name: Root name of the memory segment
        '''
        self._attr = collections.defaultdict(lambda: collections.defaultdict(int))
        self._root_name = root_name

        self.initialized = False

        self._parse_blocks(blocks)

        # Only if shm.py is run, will the class create the shared memory segments and semaphores.
        if not self.initialized:
            self.create_blocks()
        else:
            self.link_blocks()

    def add_blocks(self, name, data):
        '''Given name and data, the block will be added to the segment
        Currently, it supports numpy.arrays and strings'''
        # If type of data is numpy array
        if type(data) is np.ndarray:
            # > Create data and size
            self._attr[name]['data'] = data
            self._attr[name]['size'] = data.size * data.itemsize
        elif type(data) is str:
            # > Else, create data and string size
            self._attr[name]['data'] = data.encode('utf8') # We assume it is a string and encode it UTF-8
            self._attr[name]['size'] = len(data)


    # Legacy code from CPro
    def _parse_blocks(self, blocks):
        """Parse the specified keys and values for ease of use throughout the class"""
        for k, v in blocks.iteritems():
            self._attr[k] = v
            self._attr[k]['length'] = self._attr[k]['shape'][0] * self._attr[k]['shape'][1] * 8  # Store length in bytes
            if not self._attr[k]['name']:
                self._attr[k]['name'] = k
            if not self._attr[k]['size']:
                # Default size of segment if not specified
                self._attr[k]['size'] = 2 ** 12  # Each numpy element takes up 8 bytes

    def create_blocks(self):
        """Convenient function for organizing the memory maps and semaphores into a dict"""
        for k in self._attr:
            path_name = "{}_{}_{}".format(ROBOT_NAME, self._root_name, self._attr[k]['name'])

            # Close all shared memory if they already exist
            try:
                posix_ipc.unlink_shared_memory(path_name + "_mem")
                posix_ipc.unlink_lockaphore(path_name + "_lock")
            except:
                pass

            # Another alternate ExisentialError catch approach
            # > Coming soon...

            # Create the shared memory, semaphore blocks and map to a dict
            mem = posix_ipc.SharedMemory(path_name + "_mem", posix_ipc.O_CREX, size=self._attr[k]['size'])
            self._attr[k]['map'] = mmap.mmap(mem.fd, mem.size)
            self._attr[k]['semaphore'] = posix_ipc.Semaphore(path_name + "_lock", posix_ipc.O_CREX)
            self._attr[k]['semaphore'].release()

            # Close the open FD
            mem.close_fd()
            self.initialized = True

    def link_blocks(self):
        """If shared memory already exists, organize memory maps and semaphores and do not newly create."""
        for k in self._attr:
            path_name = ROBOT_NAME + "_" + self._root_name + "_" + self._attr[k]['name']

            # Create the shared memory, semaphore blocks and map to a dict
            mem = posix_ipc.SharedMemory(path_name + "_mem")
            self._attr[k]['map'] = mmap.mmap(mem.fd, mem.size)
            self._attr[k]['semaphore'] = posix_ipc.Semaphore(path_name + "_lock")
            self._attr[k]['semaphore'].release()

            # Close the open FD
            mem.close_fd()


    def set(self, key, val):
        with self._attr[key]['semaphore']:
            self._write_to_mem(self._attr[key]['name'], self._attr[key]['map'], val)

    def _write_to_mem(self, key, mapfile, data):
        mapfile.seek(0)
        data = data.tostring()
        data += '\n'
        self._attr[key]['memlines'] = data.count('\n')
        mapfile.write(data)

    def get(self, key):
        with self._attr[key]['semaphore']:
            arr = self._read_from_mem(self._attr[key]['name'], self._attr[key]['map'], self._attr[key]['shape'])
            return arr

    def _read_from_mem(self, key, mapfile, shape):
        """Read whatever is currently in the given mapfile"""
        mapfile.seek(0)
        data = mapfile.readline()
        for idx in range(self._attr[key]['memlines']-1):
            data += mapfile.readline()
        return np.fromstring(data[:-1]).reshape(shape)
        # return np.fromstring(data).reshape(shape)

    def _generate_accessors_setters(self):
        '''Experimental... and dangerous... and not recommended...'''
        for k in self._attr:
            key = k
            accessor = ("self.get_%s = lambda: self.get('%s')" % (self._attr[k]['name'], self._attr[k]['name']))
            exec accessor