import os
import pep8
import time
import shutil
import datetime
import leap
import inspect
import imp
import cProfile
import multiprocessing
import logging
import sys
import pylab as pl
import pprint
from lab.lib.units import times
#from leap.lib.tools import letter_cases, generic
#from leap.lib.tools.leap_termcolor import colored
from lab.lib.lab_app import enable_method_pickling
from lab.lib.lab_app.app_console_formatter import AppConsoleFormatter
#import lab.lib.tools.svn_tools as svn


class App(object):
    '''
    Base App object for all LEAP apps. Performs the following operations
    - Defines output directory as self.out_path
    - Will create output directory with self.create_output
    - Checks code for PEP8 compliance.
    - Tracks running time.
    - Defines a logger with standard default operation
    '''
    def __init__(self, settings=None, out_path=None, check_pep8=True):
        self.__start_time = time.time()
        self.__run_time_string = datetime.datetime.fromtimestamp(
            int(self.__start_time)).strftime("%Y-%m-%d--%H-%M-%S")
        self.__camel_case_name = self.__class__.__name__
        self.__name = letter_cases.from_camel_to_lower(self.__camel_case_name)
        if self.__name.endswith("_app"):
            self.__name = self.__name[:-4]
        self.leap_path = os.path.realpath(leap.__path__[0])
        self.resources_path = os.path.join(self.leap_path, 'resources')
        self.ldb_data_path = os.path.join(self.leap_path, 'ldb_data')
        self.long_term_output_path = os.path.join(self.leap_path, 'long_term_output')
        self.app_dir = os.path.dirname(os.path.realpath(inspect.getfile(self.__class__)))
        self.logger, self.console_logger = self._create_console_logger_and_handler(self.app_dir, self.leap_path)
        if out_path is not None:
            self.out_path = out_path
        else:
            self.out_path = self.__define_out_path()
        self.out_admin_path = os.path.join(self.out_path, "admin")
        if settings is not None:
            self.settings = settings
        else:
            old_settings_path = os.path.join(self.app_dir, 'settings.py')
            self.custom_settings_path = os.path.join(self.app_dir, 'custom_settings.py')
            self.default_settings_path = os.path.join(self.app_dir, 'default_settings.py')
            if os.path.exists(old_settings_path) and not os.path.exists(self.default_settings_path):
                error_message = ''.join(["\nPlease update your App's folder to conform the LEAP convention\n",
                                         "You need to create/commit default_settings.py to the repo\n",
                                         "default_settings.py must contain the minimum settings required\n",
                                         "Create an svn ignored file called custom_settings.py\n",
                                         "You can override or add addtional settings in custom_settings.py"])
                raise(IOError(error_message))
            if os.path.exists(self.default_settings_path) and not os.path.exists(self.custom_settings_path):
                error_message = ''.join(["\nPlease update your App's folder to conform the LEAP convention\n",
                                         "Create an svn ignored file called custom_settings.py\n",
                                         "In this file put at least this line:\n"
                                         "from default_settings import settings\n",
                                         "Then you can override or add to this settings object"])
                raise(IOError(error_message))
            self._load_settings()
        self.logger.info(colored("==== running %s (%s) ====" % (self.__name, self.__run_time_string), "cyan"))
        if check_pep8:
            self.check_pep8()

    def __getstate__(self):
        '''
        This method defines how an App is pickled. It was written to remove
        the logger, as it can not be pickled and breaks multiprocessing.
        '''
        d = dict(self.__dict__)
        d['console_logger_level'] = d['console_logger'].__dict__['level']
        del(d['console_logger'])
        d['logger_level'] = d['logger'].__dict__['level']
        del(d['logger'])
        if 'file_logger' in d:
            d['file_logger_level'] = d['file_logger'].__dict__['level']
            d['file_logger_base_file_name'] = d['file_logger'].__dict__['baseFilename']
            del(d['file_logger'])
        return d

    def __setstate__(self, d):
        '''
        This method defines how an App is unpickled. It reinstates the loggers
        that were removed by __getstate__.
        '''
        self.__dict__ = d
        logger, console = self._create_console_logger_and_handler(d['app_dir'], d['leap_path'])
        logger.setLevel(d['logger_level'])
        console.setLevel(d['console_logger_level'])
        self.__dict__['logger'] = logger
        self.__dict__['console_logger'] = console
        if 'file_logger_level' and 'file_logger_base_file_name' in d:
            log_dir = os.path.dirname(d['file_logger_base_file_name'])
            proc_name = multiprocessing.current_process().name
            log_path = os.path.join(log_dir, proc_name) + ".txt"
            file_logger = self._create_file_logger(log_path, d['file_logger_level'])
            self.__dict__['file_logger'] = file_logger
            if not file_logger in self.logger.handlers:
                self.logger.addHandler(file_logger)

    def _load_settings(self):
        if os.path.isfile(self.custom_settings_path):
            settings_module = imp.load_source('settings', self.custom_settings_path)
            if hasattr(settings_module, "settings"):
                self.settings = settings_module.settings


    def _create_console_logger_and_handler(self, app_dir, leap_dir):
        '''
        Creates a console hander with the format defined in
        LeapAppConsoleFormatter. Creates a logger with this handler
        and returns both
        '''
        #logger name is made up of alg, process name and time to ensure uniqueness
        alg_path = os.path.relpath(app_dir, leap_dir)
        alg_path = os.path.normpath(alg_path)  # converts to standard unix path
        proc_name = multiprocessing.current_process().name
        name = "%s.%s.%s" % (alg_path.replace('/', '.'), proc_name, str(time.time()).replace('.', ''))
        logger = logging.getLogger(name)
        console = logging.StreamHandler(sys.stdout)
        formatter = LeapAppConsoleFormatter()  # use custom formatter for console
        console.setFormatter(formatter)
        try:
            console.set_name('console')
        except AttributeError:
            pass
        if not console in logger.handlers:
            logger.addHandler(console)
        logger.setLevel(logging.DEBUG)  # Control levels via handlers
        return logger, console

    def _create_file_logger(self, log_path, level=logging.DEBUG):
        file_logger = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s | %(message)s')
        file_logger.setFormatter(formatter)
        file_logger.setLevel(level)
        try:
            file_logger.set_name('file')
        except AttributeError:
            pass
        return file_logger

    def __define_out_path(self):
        '''
            Constructs the path for output by combining the start_time with
            the name of the child class.
        '''
        return os.path.join(self.leap_path, "output",
                            self.__run_time_string + "_" + self.__name)

    def check_pep8(self, quiet=True):
        guide = pep8.StyleGuide(quiet=quiet, max_line_length=120)
        report = guide.check_files(".")
        if report.get_count() > 0:
            self.logger.info(colored("==== (files do not meet style guidelines) ====", "cyan"))

    def create_output(self, write_svn_diff=True):
        if not os.path.isdir(self.out_path):
            os.mkdir(self.out_path)
            self.logger.info(colored("==== created output for %s (%s) ====" % (self.__name, self.__run_time_string),
                                     "cyan"))
        if not os.path.isdir(self.out_admin_path):
            os.mkdir(self.out_admin_path)
        if hasattr(self, "custom_settings_path"):
            if os.path.exists(self.custom_settings_path):
                if not os.path.isfile(os.path.join(self.out_admin_path, "custom_settings.py")):
                    shutil.copy(self.custom_settings_path, os.path.join(self.out_admin_path, "custom_settings.py"))
        if hasattr(self, "default_settings_path"):
            if os.path.exists(self.default_settings_path):
                if not os.path.isfile(os.path.join(self.out_admin_path, "default_settings.py")):
                    shutil.copy(self.default_settings_path, os.path.join(self.out_admin_path, "default_settings.py"))
        if hasattr(self, "settings"):
            from leap.lib.io_management import loading_parameters
            if not os.path.isfile(os.path.join(self.out_admin_path, 'settings_used.txt')):
                with open(os.path.join(self.out_admin_path, 'settings_used.txt'), 'w') as fh:
                    pprinter = pprint.PrettyPrinter(width=120, stream=fh)
                    pprinter.pprint(vars(self.settings))
                    for key in vars(self.settings):
                        if type(getattr(self.settings, key)) == loading_parameters.Params:
                            if hasattr(getattr(self.settings, key), "data_path"):
                                data_path = getattr(self.settings, key).data_path
                                associated_path = os.path.join(str(os.path.realpath(leap.__path__[0])), "ldb_data", str(data_path))
                                for base in os.listdir(associated_path):
                                    if base in ["acs", "bolo", "ss"]:
                                        fh.write("== data path for %s base ==\n" %base)
                                        base_path = os.path.join(associated_path, base)
                                        for subbase in os.listdir(base_path):
                                            fh.write("%s:\n %s\n" %(subbase, os.path.realpath(os.path.join(base_path, subbase))))
                                        

        #Create log file and the handler for logging
        proc_name = multiprocessing.current_process().name
        log_path = os.path.join(self.out_admin_path, proc_name) + '.txt'
        if not hasattr(self, "file_logger"):
            self.file_logger = self._create_file_logger(log_path)
        if not self.file_logger in self.logger.handlers:
            self.logger.addHandler(self.file_logger)

        #svn state
        if write_svn_diff:
            svn_tool = svn.SvnTools(leap_path=self.leap_path, out_path=self.out_admin_path,
                                    log=self.logger)
            svn_tool.write_svn_to_file()

    def save_and_show(self, name, save=False, show=True, fig_num=None, clf=True, close=False, figsize=None, path=None):
        if save:
            if not hasattr(self, "out_path") or not os.path.isdir(self.out_path):
                self.create_output()
            if fig_num is not None:
                fig = pl.figure(fig_num)
            else:
                fig = pl.gcf()
            if figsize is None:
                figsize = (22, 14)
            fig.set_size_inches(figsize)
            if path is None:
                pl.savefig(os.path.join(self.out_path, name))
            else:
                pl.savefig(os.path.join(path, name))
        if show:
            pl.show()
        if clf:
            pl.clf()
        if close and not show:
            pl.close()

    def run_test(self):
        self.run()

    def profile(self):
        cProfile.runctx('self.run()', globals(), locals(), sort="cumulative")

    def end(self):
        time_str = times.time_string(time.time()-self.__start_time)
        self.logger.info(colored("==== finished %s (after %s) ====" % (self.__name, time_str), "cyan"))
        logging.shutdown()


def get_resources_path():
    return os.path.join(os.path.realpath(leap.__path__[0]), "resources")


if __name__ == "__main__":
    print "--- Doing simple test of App Class ---"
    app = App()
