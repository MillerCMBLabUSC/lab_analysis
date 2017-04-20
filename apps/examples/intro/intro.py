#! /usr/bin/env python

"""
This demonstrates a basic LEAP app that writes a string to a file.
Read the code, run the code (./run.py), then check leap/output for the output.
This app demonstrates:

    * An App is a class that inherits from leap_app.App.
      Being a child of leap_app.App automatically gives the app some useful features:

        * self.settings automatically points to the settings object from settings.py

        * self.create_output() automatically creates a directory in leap/output
          with the app name and timestamp (e.g. 2013-05-09--13-26-19_introduction)

            * settings.py is automatically copied to the output directory for future
              reference

            * leap/output is meant for scratch work, you usually keep it empty.
              You run your app hundreds of times while developing, then every once
              in a while clear out the directory when it gets annoying

            * leap/long_term_output is where you copy the outputs you want to keep long term

            * none of the contents of leap/output or leap/long_term_output are checked
              into the repository

            * self.out_path automatically points to the output directory that is created
              by self.create_output()

        * When you instantiate the app it will warn you if you violate PEP8 style guidelines
          (try adding a space to the end of some line of code and running it again)

        * self.profile() will call self.run() but with the profiler enabled
          (try commenting app.run() and uncommenting app.profile())

    * The app is a class that can be imported and instantiated by other apps, but if you
      want to run the app directly you specify a __main__ block of code that instantiates
      the app and runs it
"""

import os
from leap.lib.leap_app import leap_app


class IntroductionApp(leap_app.App):

    def run(self):
        self.create_output()
        outfilename = os.path.join(self.out_path, "test.txt")
        outfile = open(outfilename, "w")
        print "writing \"%s\" to file" % self.settings.x
        outfile.write(self.settings.x)
        outfile.close()


if __name__ == "__main__":
    app = IntroductionApp()
    app.run()
    #app.profile()
    app.end()
