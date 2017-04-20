#! /usr/bin/env python
import scipy.stats
from leap.lib.leap_app import leap_app
from leap.lib.timing import progress_indicator


class IndicatorExampleApp(leap_app.App):

    def job(self, thing):
        x = scipy.stats.norm.rvs(size=10000)

    def class_example(self, things):
        indicator = progress_indicator.Indicator()
        for i, thing in enumerate(things):
            indicator.display(i, total=len(things))
            #indicator.display(i)  # if you don't know the total
            #indicator.display(i, total=num_jobs, verb="processing")
            self.job(thing)
        indicator.end()

    def generator_example(self, things):
        for thing in progress_indicator.wrapper(things):
            self.job(thing)

    def run(self):
        things = range(3000)
        self.class_example(things)
        self.generator_example(things)

if __name__ == "__main__":
    app = IndicatorExampleApp()
    app.run()
    app.end()
