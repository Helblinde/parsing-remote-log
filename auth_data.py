import logging


def auth_data(ip):
    """Returns login and password for
    the specified server ip address

    Usage example:

    >>> login, password = auth_data('127.0.0.1')
    >>> print(login, password)
    User1 password1
    """

    try:
        # here we assume having some code that connects
        # to the database or grabs login and password from
        # local encrypted file for example or whatever
        # instead of locally set values for testing purposes;
        # replace these values with your laptop credentials
        # for testing on your local machine
        login, password = 'your_login', 'your_password'
    except Exception:
        # handling all possible exceptions that can happen
        # during login/password retrieval; in real project
        # we should better catch some specific exceptions that
        # can happen instead of broad 'Exception' class
        logging.exception('Error while retrieving login and password!')
        login = password = None
    finally:
        # here we should have some code that closes
        # DB connection or opened local file etc.
        pass

    return [login, password]

if __name__ == '__main__':
    login, password = auth_data('127.0.0.1')
    print(login, password)
