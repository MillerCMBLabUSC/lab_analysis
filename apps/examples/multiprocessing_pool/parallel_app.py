#! /usr/bin/env python

"""
leap_multiprocessing.Pool runs your program multiple times in parallel:
  * once as the main process that waits for the N workers to finish
  * an additional N times as each of the N worker processes

Normally you have more jobs than workers.  The Pool automatically hands out
jobs to the worker processes.

Issues and details to be aware of:

    1) Do not include lambdas in classes that need to be passed to a multiprocessed
        job because they cannot be pickled.

    2) If your worker function calls a shared library with ctypes, that C code
        also needs to register a SIGINT handler that exits the C code.  This is
        because if the interrupt happens while inside the C library, the python
        function that called it no longer has the GIL and can't kill itself.

    3) You may have trouble interrupting your program if you try to kill it while it
        is adding jobs.  If this is the case you can wrap the loop that adds jobs
        in a try/except KeyboardInterrupt.
"""

import time
from leap.lib.leap_app import leap_app
from leap.lib.tools import leap_multiprocessing


class ParallelApp(leap_app.App):

    def job(self, job_num):
        print "doing job", job_num
        time.sleep(2)
        return "hello%i" % job_num

    def run(self):
        self.create_output()
        #pool = leap_multiprocessing.Pool()
        ###  Try these:
        #pool = leap_multiprocessing.Pool(run_parallel=False)
        pool = leap_multiprocessing.Pool(4, run_parallel=True)
        for job_num in range(6):
            pool.add_job(self.job, args=[job_num])
        for job_num, job in enumerate(pool.jobs):
            result = job.get()
            print "got result for job %i: %s" % (job_num, result)
        pool.end()


if __name__ == "__main__":
    app = ParallelApp()
    app.run()
    app.end()
