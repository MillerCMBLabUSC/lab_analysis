#! /usr/bin/env python

import os
from leap.lib.leap_app import leap_app
from leap.lib.tools import generic
from leap.lib.tools import tabling


class TablesExample(leap_app.App):

    def write(self):
        things = []
        for i in range(3):
            things.append(generic.Class(x=i, y=i+1))
        keys = ["x", "y"]
        tabling.write(things, os.path.join(self.out_path, "table.txt"), keys)

    def read(self):
        things = tabling.read(os.path.join(self.out_path, "table.txt"))
        print things

    def run(self):
        self.create_output()
        self.write()
        self.read()

    def run_test(self):
        print "skipping most of the example"
        self.end()


if __name__ == "__main__":
    app = TablesExample()
    app.run()
    #app.run_test()
    app.end()
