import re
import logging
from paramiko import SSHClient, AutoAddPolicy
from create_logs import create_logs
from auth_data import auth_data

LINES_RANGE = 100


def parse_log(ip, mask, str_id):
    """Accepts server ip address, masked file name
    and specific id (or string), that should be found
    inside the file. After finding the proper line,
    prints 100 preceding and 100 subsequent lines
    of the found line.
    Returns False in case of any unexpected errors
    or creates 'results.txt' and returns True otherwise
    """

    # calling existing auth_data() function to
    # get login and password for the ssh connection
    login, password = auth_data(ip)

    # calling create_logs() function for making
    # six sample logs inside '/tmp' directory
    # for testing purposes
    create_logs()

    # replacing all '#' with '.' symbols
    # since '.' is default wild-card symbol for regex
    # but at first add backslash before the '.' symbol
    # which is the delimiter between file name and file type
    fixed_mask = mask.replace('.', '\.')
    regex_pattern = fixed_mask.replace('#', '.')

    # compile regex pattern for using further
    file_pattern = re.compile(regex_pattern)

    # start SSH session, return False in case of any exceptions
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ip, username=login, password=password)
    except Exception:
        logging.exception('Error! Can not establish ssh session')
        return False

    # start the SFTP session across an open SSH Transport
    # for performing remote file operations, return False
    # in case of any exceptions
    try:
        sftp_client = ssh.open_sftp()
    except Exception:
        logging.exception('Error! Can not establish SFTP session')
        return False

    # finding proper server log in the specified directory
    # using provided mask, find str_id inside that file and
    # copy -100 and +100 lines from that line with str_id
    # including found line itself
    try:
        # go to '/tmp' directory with our test server logs
        sftp_client.chdir('/tmp')

        # finding proper server log with regex
        for item in sftp_client.listdir('.'):
            if re.match(file_pattern, item):
                found_file_name = item
                break
        else:
            # print error message and immediately return False
            # in case there's no corresponding file among server logs
            print("Error! Chosen mask doesn't match with any file!")
            return False

        # seeking for the line number containing specified id
        line_number = 0
        with sftp_client.file(found_file_name, 'r') as file:
            for line in file:
                line_number += 1
                if str_id in line:
                    break
            else:
                # print error message and immediately return False
                # in case there's no corresponding id string in log
                print('Error! str_id is not found inside log')
                return False

        # copy 201 lines totally from server log on the server
        # to results.txt file in this script's directory
        with sftp_client.file(found_file_name, 'r') as file_out, \
                open('results.txt', 'w') as file_in:
            if line_number >= LINES_RANGE + 1:
                # skip the beginning of the file in case found line number
                # is greater than 101 (or LINES_RANGE + 1)
                # and then start copying
                for i in range(1, line_number - LINES_RANGE):
                    file_out.readline()
                for i in range(line_number - LINES_RANGE, line_number + LINES_RANGE + 1):
                    file_in.write(file_out.readline())
            else:
                # otherwise simply start copying from the very beginning of the file
                for i in range(1, line_number + LINES_RANGE + 1):
                    file_in.write(file_out.readline())
    finally:
        # close sftp and ssh sessions'
        sftp_client.close()
        ssh.close()

    return True


if __name__ == '__main__':
    result = parse_log('127.0.0.1', 'access_###3.###', 'EditDoesNotIncreaseTheRevision')
    print(result)
