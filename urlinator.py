#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
from lib.urlverifier import urlverifier

class Urlinator:
    def __init__(self,targets = None, threads = 10, outputfile = None):
        self.logger = logging.getLogger("URLINATOR")
        self.logger.info("Starting scan.")
        self.targets = targets
        self.threads = threads
        self.outputFile = outputfile

        self.urls = self.start_scan()

        if self.outputFile is not None:
            self.write_out()
        else:
            for url in self.urls:
                self.logger.info(url)

    def start_scan(self):
        urlverif = urlverifier(self.targets, self.threads)
        return urlverif.verify()

    def write_out(self):
        for url in self.urls:
            self.outputFile.writelines(f'{url}\n')
        
        self.logger.info(f"Written results to \"{self.outputFile.name}\".")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(add_help =  True, description = "URLinator tries to identify if the target IP and PORT combination supports HTTP and/or HTTPS.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', metavar="<input file>", type=argparse.FileType('r'), help='Input file containing IP:PORT targets on separate lines', required=False)
    group.add_argument('-t', metavar="<IP:PORT>", type=str, help='Single target to test', required=False)
    parser.add_argument('-T', metavar="<threads>", type=int, default=10, help='Number of threads (default 10)', required=False)
    parser.add_argument('-O', metavar="<output file>", type=argparse.FileType('w'), help='Results file', required=False)
    parser.add_argument('-debug', action='store_true', help='Turn DEBUG output ON')
    options = parser.parse_args()

    logger = logging.getLogger("MAIN")

    if (options.debug):
        logging.basicConfig(format='%(name)-11s | %(asctime)s - %(levelname)-5s - %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(name)-11s | %(asctime)s - %(levelname)-5s - %(message)s', level=logging.INFO)

    logger.info("URLinator")
    targets = []
    if options.i:
        with options.i as infile:
            for line in infile:
                target = line.strip()
                logger.debug(f"Target: {target}")
                targets.append(target)
    elif options.t:
        logger.debug(f"Target: {options.t}")
        targets.append(options.t)
        options.T = 1

    if len(targets) < options.T:
        options.T = len(targets)
        logger.debug("Less targets than threads, so reducing threads to: "+str(options.T))
    else:
        logger.debug("Threads: "+str(options.T))
    
    urlinator = Urlinator(targets=targets, threads=options.T, outputfile=options.O)
