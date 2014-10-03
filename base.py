#!/usr/bin/env python

import requests
import time

DELAY = 10


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