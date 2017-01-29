import logging
from shutil import copy2

SOURCE_ACCESS_LOG = 'sample_logs/access_log.txt'
SOURCE_ERROR_LOG = 'sample_logs/error_log.txt'


def create_logs():
    """This is auxiliary function for testing purposes
    It creates three similar Apache access logs and
    error logs with different names in '/tmp' directory
    using sample logs from 'sample_logs' directory
    and shutil.copy2 function
    """

    try:
        for i in range(1, 4):
            copy2(SOURCE_ACCESS_LOG, '/tmp/access_log%d.txt' % i)
            copy2(SOURCE_ERROR_LOG, '/tmp/error_log%d.txt' % i)
    except OSError:
        logging.exception('Error, destination location is not writable!')
    else:
        print('All test logs were successfully created!')


if __name__ == '__main__':
    create_logs()
