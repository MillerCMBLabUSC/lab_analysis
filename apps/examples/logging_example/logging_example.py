#! /usr/bin/env python
from leap.lib.leap_app import leap_app
from leap.lib.tools import leap_multiprocessing
import multiprocessing
import logging
#import warnings


class LoggingExample(leap_app.App):
    '''
    An example App using the python logging library.

    INSTRUCTIONS:
    The idea of LEAP logging is that it should default to what you
    want so all you should do in your new App is use the following
    levels instead of print statements:
        self.logger.debug - for low level debug statements
        self.logger.info - for typical print statements
        self.logger.warning - for warnings
        self.logger.error - For errors, you might call of these and
            raise an Exception
        self.logger.critical - For really critical problems. You
            might also do these before raising an Exception

    If you want debug statements to appear in the console you need
    to set its level via a call like:
        self.console_logger.setLevel(logging.DEBUG)

    Once your app is stable you'll probably want to switch to only
    seeing INFO (and higher) messages
        self.console_logger.setLevel(logging.INFO)

    Finally, if you create_output all log statements will be saved
    to file as well as written to the screen. The file logger's
    level can be adjusted with
        self.file_logger.setLevel(logging.DEBUG)
    but I don't recommend touching it.
    '''
    def run(self):
        pool = leap_multiprocessing.Pool()
        for job_num in range(5):
            pool.add_job(self.run_log_process, args=[])
        for job_num, job in enumerate(pool.jobs):
            result = job.get()
        pool.end()

    def run_log_process(self):
        '''
        The following outputs each message to stdout. Note
        the differences in formats between types. These
        are defined in leap.lib.leap_app.leap_app_console_formatter
        '''
        "------------- Log Process ------------------------"
        self.logger.debug('This is a debug message')
        self.logger.info('This is an info message')
        self.logger.warning('This is a warning')
        self.logger.error('This is an error')
        self.logger.critical('This is a critical message')
        #self.warning_statement_in_a_library("This is a zeroth warning from a library")
        print "\n\n"

        '''
        Create_output() creates a log file called log.txt
        in the typical output directory. The logging level of this
        file is set to the lowest (DEBUG) and the format includes
        the timestamp.
        The folllowing five lines will get saved to that file as
        well as wrtting to screen
        '''
        self.create_output()
        self.logger.debug('This is a second debug message')
        self.logger.info('This is a second info message')
        self.logger.warning('This is a second warning')
        self.logger.error('This is a second error')
        self.logger.critical('This is a second critical message')
        #self.warning_statement_in_a_library("This is a warning from a library")
        print "\n\n"

        '''
        It is possible to set the levels of each of the handlers
        individually. For convenience they are stored in:
            self.console_logger
            self.file_logger
        '''
        self.console_logger.setLevel(logging.WARNING)
        self.file_logger.setLevel(logging.ERROR)
        self.logger.info('This will not show up')
        self.logger.warning('This message will appear only on the screen')
        self.logger.error('This message will appear on the screen and in the log')
        #self.warning_statement_in_a_library("This is a second warning from a library")
        print "\n\n"

        '''
        It is possible to override both handlers with the loggers level, though
        I don't really recommend it.
        '''
        self.logger.setLevel(logging.CRITICAL)
        self.logger.debug('This is a third debug message')
        self.logger.info('This is a third info message')
        self.logger.warning('This is a third warning')
        self.logger.error('This is a third error')
        self.logger.critical('This is a third critical message (the only one that should appear)')
        #self.warning_statement_in_a_library("This is a third warning from a library")

        self.create_output()  # A second call to create_output shouldn't cause problems
        self.logger.critical('A final message')

    #def warning_statement_in_a_library(self, message):
    #    """
    #    This simulated a function/method in a library that doesn't have access to the
    #    logger. It can emit warnings through the use of warnings.warn, 
    #    which will be captured by the logger
    #    """
    #    warnings.warn(message)

if __name__ == "__main__":
    app = LoggingExample()
    app.run()
    #app.run_log_process()
    app.end()
