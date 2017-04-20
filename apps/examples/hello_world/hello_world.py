#! /usr/bin/env python
from leap.lib.leap_app import leap_app


class HelloWorldApp(leap_app.App):

    def run(self):
        print self.settings.message

if __name__ == "__main__":
    app = HelloWorldApp()
    app.run()
    app.end()
