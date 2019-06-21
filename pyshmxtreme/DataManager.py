#!usr/bin/env python
__author__ = "Joshua Hooks"
__email__ = "hooksjrose@gmail.com"
__copyright__ = "Copyright 2019 RoMeLa"
__date__ = "June 13, 2019"

__version__ = "0.0.1"
__status__ = "Prototype"

import numpy as np
import Util.MemoryManager as MM
import time
import pdb


class Logger(object):
    """
    Logs all data in desired blocks of shared memory. The data is stored in a pre-allocated numpy array and uses a circular
    buffer structure.
    """

    def __init__(self, smb, size=60000, filename='data_log.csv'):
        self._sm_blocks = smb  # list of shared memory blocks that should be logged
        self._log_index = 0          # index for the position in the data structure
        self._log_size = size
        self._data_size = self._get_size()
        self._header = self._create_headers()
        self._log = np.zeros((self._log_size, self._data_size))
        self._filename = filename

        # Set these if you want to add a delay to the logger
        self._log_delay = 0  # Number of control loops between recorded data points, set to 0 for continuous logging
        self._log_delay_count = 0

    def log_current_data(self):

        logging_data = np.zeros((1, self._data_size))
        logging_data[0] = time.time()
        log_index = 1

        for block in self._sm_blocks:
            sm_dict = block.get()  # get the shared memory dictionary
            for data in sm_dict.itervalues():
                cd_size = data.size  # current data block size
                logging_data[0, log_index:(log_index+cd_size)] = data.reshape((1, cd_size))
                log_index += cd_size

        # add data to the log
        self._log[self._log_index, :] = logging_data
        self._log_index += 1
        if self._log_index >= self._log_size:  # check if the index needs to be set back to 0
            self._log_index = 0

    def write2csv(self):
        np.savetxt(self._filename, self._log, fmt='%.10f', delimiter=',', header=self._header)

    def _get_size(self):
        """
        Loops through all shared memory blocks desired for logging and determines the total size
        :return:
        """

        logging_data = np.array([time.time()])

        for block in self._sm_blocks:
            sm_dict = block.get()  # get the shared memory dictionary
            for data in sm_dict.itervalues():
                logging_data = np.concatenate((logging_data, data), axis=None)

        return logging_data.size

    def _create_headers(self):

        header = "time_stamp"

        for block in self._sm_blocks:
            group = "(" + block.get_seg_name() + ")"
            sm_dict = block.get()  # get the shared memory dictionary
            for key in sm_dict.iterkeys():
                cd_size = sm_dict[key].size
                if cd_size == 1:
                    header += "," + group + str(key)
                else:
                    for i in range(1,cd_size+1):
                        header += "," + group + str(key) + ":" + str(i)

        return header

if __name__ == "__main__":

    MM.init()
    MM.connect()

    sm_blocks = [MM.LIMB_STATE, MM.JOINT_STATE]

    test = MM.JOINT_STATE.get()

    log = logger(sm_blocks)
    log.log_current_data()
    time.sleep(0.1)
    log.log_current_data()
    time.sleep(0.1)
    log.log_current_data()
    time.sleep(0.1)
    log.log_current_data()
    time.sleep(0.1)

    log.write2csv()
