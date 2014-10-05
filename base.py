#!/usr/bin/env python

import requests
import time

from boto.s3.connection import S3Connection
from boto.s3.key import Key


AWS_ACCESS_KEY_ID = "AKIAIYIAPEOQ2T6AF7MQ"
AWS_SECRET_ACCESS_KEY = "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"
DELAY = 10
BUCKET = 'preturi'


def get_page_content(url):
    error_file = open("error.log", 'a')
    try:
        page = requests.get(url, timeout=40)
        if not page.ok:
            time.sleep(DELAY)
            page = requests.get(url, timeout=40)
            if not page.ok:
                raise NameError("Page was not loaded")
        return page
    except requests.Timeout:
        print "!!! caca !!!- {0}".format(url)
        error_file.write("{0} - Timeout exception - {1}\n".
                         format(time.strftime("%d-%m-%y %H-%M"), url))
        pass
    except NameError as e:
        error_file.write("{0} - Page was not loaded exception - {1} - {2}\n".
                         format(time.strftime("%d-%m-%y %H-%M"),
                                e.message, url))
        pass
    except Exception as e:
        error_file.write("{0} - Some error - {1} - {2}\n".format(
            time.strftime("%d-%m-%y %H-%M"), e.message, url))
    error_file.close()
    return None


def send_to_s3(file_to_send):
    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    b = conn.get_bucket(BUCKET)
    k = Key(b)
    f = open(file_to_send, 'rb')
    k.key = file_to_send
    k.set_contents_from_filename(f)
    k.send_file()
    f.close()
