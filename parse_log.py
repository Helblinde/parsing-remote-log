import re
import logging
from paramiko import SSHClient, AutoAddPolicy
from create_logs import create_logs
from auth_data import auth_data

LINES_RANGE = 100
SERVER_LOGS_DIR = '/tmp'


def find_server_log(sftp_client, file_pattern):
    """Auxiliary function for parse_log:
    Accepts sftp client instance and file pattern;
    Returns found file name that matches pattern
    or 'False' if not found
    """
    # go to '/tmp' directory with our test server logs
    sftp_client.chdir(SERVER_LOGS_DIR)

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
    return found_file_name


def find_line_number(sftp_client, found_file_name, str_id):
    """Auxiliary function for parse_log:
    Accepts sftp client instance, found file name and str_id;
    looks for the specified str_id in any line of the file;
    Returns line number of found str_id or False otherwise
    """
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
    return line_number


def copy_remote_to_local(sftp_client, found_file_name, line_number):
    """Auxiliary function for parse_log:
    Accepts sftp client instance, found file name and line number
    that contains needed str_id. Copies specified line and +100 and
    -100 lines of that line from remote file on the server to the
    "results.txt" file on the local machine where script is called.
    If line_number is within 100 lines of the beginning or the end
    of the file, lines will be copied from the beginning or till
    the end correspondingly, so less than 201 line will be in result
    """
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
        # calling 'find_server_log' function to find proper file
        found_file_name = find_server_log(sftp_client, file_pattern)
        # return False and immediately exit if nothing found
        if not found_file_name:
            return False

        # calling 'find_line_number' function to find line number containing str_id
        line_number = find_line_number(sftp_client, found_file_name, str_id)
        # return False and immediately exit if nothing found
        if not line_number:
            return False

        # calling 'copy_remote_to_local' procedure to copy found file
        # from remote server to local dir from which script is called
        copy_remote_to_local(sftp_client, found_file_name, line_number)

    finally:
        # close sftp and ssh sessions'
        sftp_client.close()
        ssh.close()

    return True


if __name__ == '__main__':
    result = parse_log('127.0.0.1', 'access_###3.###', 'EditDoesNotIncreaseTheRevision')
    print(result)
