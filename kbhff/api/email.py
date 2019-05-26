import easyimap, email
from kbhff.api.exceptions import *
import time
import imaplib
import sys

class GmailConnection:
    def __init__(self):
        self.connection = None
        self.mail_credentials = get_mail_credentials()
        self.connect()

    def __del__(self):
        if self.connection is not None:
            self.connection.quit()
    
    def connect(self):
        if self.connection is not None:
            self.connection.quit()
        address = self.mail_credentials["login"]
        password = self.mail_credentials["password"]
        self.connection = easyimap.connect('imap.gmail.com', address, password)

    def listup(self, number_of_mails = 25, retries_left = 100):
        try:
            return self.connection.listup(number_of_mails)
        except imaplib.IMAP4.abort:
            sys.stderr.write("Gmail connection had to reconnect after IMAP4.abort")
            if retries_left < 1:
                raise GmailConnectionError
            time.sleep(1)
            self.connect()
            return self.listup(number_of_mails, retries_left-1)

def get_mail_credentials():
    try:
        # check if module exists:
        from kbhff.api.mail_credentials import mail_credentials
    except ModuleNotFoundError:
        # check if environment variables exist:
        from os import environ
        mail_credentials = {}
        # Throws error, if environment variable does not exist
        mail_credentials["login"] = environ["MAIL_CREDENTIALS_EMAIL"]
        mail_credentials["password"] = environ["MAIL_CREDENTIALS_PASSWORD"]
    return mail_credentials


def get_latest_mail_to(to_address, email_connection = None, expect_title = None, retry_count = 10):
    """ Receive latest email sent to to_address.

    Optional parameters:
        expect_title --- if set, emails with titles that aren't an exact match will be ignored
        retry --- retry this many times with a 10 second of delay between each
        email_connection --- if an easyimap imapper with an existing connection is passed, this will be used to look up emails. Otherwise, a default connection as passed by get_gmail_connection is established and used.
    """

    connection_is_temporary = (email_connection is None)
    if connection_is_temporary:
        email_connection = GmailConnection()

    def mail_match(mail):
        return mail.to == to_address and (expect_title == mail.title or expect_title is None)

    matches = list(filter(mail_match, email_connection.listup(25))) 
    for i in range(0,retry_count):
        if len(matches) > 0:
            break
        time.sleep(10)
        matches = list(filter(mail_match, email_connection.listup(25))) 

    if len(matches) > 0:
        return matches[0]
    else:
        raise NoEmailReceivedError(f"Found no matching Email to {to_address}.")

def get_activation_code_from_email(email_body):
    """ Parses body of the email sending an activation code and returns the code as string. """
    import re
    # some random assumptions on what codes look like have been made...
    # only lowercase letters or numbers
    # between 5 and 10 characters
    code_pattern_later = re.compile('ind i feltet:[ \r\n]{1,4}([a-z0-9]{5,10})[ \r\n]{1,4}Din konto vil blive')
    code_matches_later = code_pattern_later.findall(email_body)
    
    code_pattern_during_signup = re.compile('aktivere din konto:[ \r\n]{1,4}([a-z0-9]{5,10})[ \r\n]{1,4}Alternativt kan du klikke')
    code_matches_during_signup = code_pattern_during_signup.findall(email_body)
    
    code_matches = code_matches_later + code_matches_during_signup

    if len(code_matches) != 1:
        raise UnexpectedLayoutError(f"Could not find a unique activation code in the following mail body:\n {email_body}")
    return code_matches[0]
