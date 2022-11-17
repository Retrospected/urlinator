import logging
import threading
import queue
import urllib3
import urllib3.exceptions

queueLock = threading.Lock()
workQueue = queue.Queue()
resultsQueue = queue.Queue()

class urlverifier:

    def __init__(self, targets, threads):
        self.logger = logging.getLogger('URLVERIFIER')
        self.logger.info('Initiated URLVerifier with '+str(threads)+' thread(s).')

        self.targets = targets
        self.threads = threads

    def verify (self):
        threads = []

        for ThreadID in range(int(self.threads)):
            thread = urlWorker(ThreadID)
            thread.start()
            threads.append(thread)

        queueLock.acquire()

        for target in self.targets:
            workQueue.put(str(target))

        queueLock.release()

        self.logger.info("Verifying " + str(workQueue.qsize()) + " service(s) using " + str(self.threads) + " thread(s).")

        while not workQueue.empty():
            pass

        self.logger.info("The queue is empty, waiting for the remaining thread(s) to finish.")

        for thread in threads:
            thread.keepRunning = False

        for t in threads:
            t.join()

        self.logger.info("Scan completed.")
        urls=[]
        while not resultsQueue.empty():
            url = resultsQueue.get()
            urls.append(":".join(url.split(":")[0:2]))

        self.logger.info("Found "+str(len(urls))+ " valid URL(s).")
        return urls

class urlWorker (threading.Thread):

    def __init__(self, threadid):
        threading.Thread.__init__(self)
        self.threadid = str(threadid)
        self.logger = logging.getLogger('WORKER-'+self.threadid)
        self.logger.debug("Initialized urlWorker "+self.threadid)

    def check_url(self, url):
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logging.getLogger("urllib3").setLevel(logging.ERROR)
            http = urllib3.PoolManager(cert_reqs='CERT_NONE')
            # starting from urllib3 v2 use this:
            # http = urllib3.PoolManager(cert_reqs='CERT_NONE', ssl_minimum_version=ssl.TLSVersion.SSLv3)

            user_agent={'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
            result = http.request('GET', url, retries=urllib3.Retry(total=3, redirect=2, raise_on_redirect=False), headers=user_agent, timeout=urllib3.Timeout(connect=5, read=10))
            if result.status and not result.status == 400:
                return True
            else:
                return False
        except urllib3.exceptions.SSLError as e:
            # no SSL support
            return False
        except urllib3.exceptions.ProtocolError as e:
            # protocol error
            return False
        except urllib3.exceptions.ResponseError as e:
            # this can be too many redirects or anything HTTP protocol related, but we can assume the conclusion of (un)encrypted traffic can be made
            return True
        except urllib3.exceptions.TimeoutError as e:
            # port is closed
            return False
        except urllib3.exceptions.MaxRetryError as e:
            # max retries failed
            return False
        except Exception as e:
            self.logger.error(e)
            return False

    def run(self):
        self.keepRunning = True
        while self.keepRunning:
            queueLock.acquire()
            if not workQueue.empty():
                ipport = workQueue.get()
                queueLock.release()
                found = False
                self.logger.debug("urlWorker "+self.threadid+" checking out: "+ipport)

                if self.check_url("https://"+ipport):
                    queueLock.acquire()
                    resultsQueue.put("https://"+ipport)
                    found = True
                    queueLock.release()
                if self.check_url("http://"+ipport):
                    queueLock.acquire()
                    resultsQueue.put("http://"+ipport)
                    found = True
                    queueLock.release()

                if not found:
                    self.logger.info("Could not find a working protocol for: "+ipport)

            else:
                queueLock.release()
