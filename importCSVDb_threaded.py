#!/usr/bin/python
__author__ = 'bobo'

import Queue
import threading
import time
import os
import csv
import re
import datetime
import database

threads = []
threadID = 1
threadNumber = 5
queueLock = threading.Lock()
workQueue = Queue.Queue(0)
exitFlag = 0

mysqlconfig = {
      'user': 'preturi',
      'password': 'preturi',
      #'host': 'localhost',
      'host': '192.168.122.120',
      'database': 'preturi',
    }


class MyThread (threading.Thread):
    def __init__(self, threadid, threadname, queue):
        threading.Thread.__init__(self)
        self.threadid = threadid
        self.name = threadname
        self.queue = queue

    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.queue)
        print "Exiting " + self.name


def process_data(threadname, queue):
    connection = database.connect_db(mysqlconfig)
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = queue.get()
            queueLock.release()
            csv_start_timestamp = datetime.datetime.now()
            print "%s processing %s" % (threadname, data)
            lines, products, prices = process_csv(data, connection)
            queueLock.acquire()
            print "%s: %s processed in %s" % (threadname, data, str(datetime.datetime.now() - csv_start_timestamp))
            print "%s: %s lines processed" % (threadname, str(lines))
            print "%s: %s products added" % (threadname, str(products))
            print "%s: %s prices added" % (threadname, str(prices))
            queueLock.release()
        else:
            queueLock.release()
        time.sleep(1)
    database.disconnect_db(connection)


def traverse_folder(path):
    for entry in os.listdir(path):
        if os.path.isdir(path + "/" + entry):
            traverse_folder(path + "/" + entry)
        else:
            if entry != "index":
                workQueue.put(path + "/" + entry)


def process_csv(file_name, connection):
    nr_processed_lines = 0
    nr_added_products = 0
    nr_added_prices = 0

    match = re.match("^.+/([a-zA-Z0-9]+)-([0-9]{2})-([0-9]{2})-([0-9]{2}).+", file_name)

    shop_id = database.get_shop_id(match.group(1), connection)

    date = datetime.datetime.strptime(match.group(4) + match.group(3) + match.group(2), "%y%m%d")
    scrape_date = date.strftime("%Y-%m-%d")

    with open(file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            try:
                product = (row[0], row[1], row[3], row[4])
            except:
                print "Error on row: %s" % row
            (added_product, added_price) = database.insert_product(product, shop_id, scrape_date, connection)
            nr_processed_lines += 1
            nr_added_products += added_product
            nr_added_prices += added_price

    result = (nr_processed_lines, nr_added_products, nr_added_prices)

    return result

#workaround for strptime to solve thread safe behaviour
boggus_date = datetime.datetime.strptime(datetime.datetime.today().strftime("%y%m%d"), "%y%m%d")

# Create new threads
for tNumber in range(0, threadNumber):
    thread = MyThread(threadID, "Thread-" + str(tNumber), workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

# Fill the queue
queueLock.acquire()
traverse_folder("csv")
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
    itemsRemaining = workQueue.qsize()
    print "Main Thread - %s - Items remaining: %s" % (str(time.ctime(time.time())), itemsRemaining)
    time.sleep(600)

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for thread in threads:
    thread.join()
print "Exiting Main Thread"