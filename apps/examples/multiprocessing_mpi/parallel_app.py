#! /usr/bin/env python

from mpi4py import MPI
import os
import time
from leap.lib.leap_app import leap_app
from leap.lib.io_management import dirfile_loading


class ParallelApp(leap_app.App):

    def write_bolo(self, segment, bolo):
        bolo.load()
        time.sleep(20)  # simulate processing on a bolo
        segment_path = os.path.join(self.out_path, "segments", segment.name)
        out_file_path = os.path.join(segment_path, "%s.txt" % bolo.name)
        with open(out_file_path, "w") as out_file:
            out_file.write("hello I am bolo %s" % bolo.name)

    def write_bolos(self, rank, size):
        segments = dirfile_loading.load(self.settings.loading_params)
        counter = 0
        for segment in segments:
            for bolo in segment.unloaded_bolo_datasets:
                if counter % size == rank:
                    self.write_bolo(segment, bolo)
                counter += 1

    def create_directories(self):
        self.create_output()
        segments = dirfile_loading.load(self.settings.loading_params)
        os.mkdir(os.path.join(self.out_path, "segments"))
        for segment in segments:
            segment_path = os.path.join(self.out_path, "segments", segment.name)
            os.mkdir(segment_path)

    def run(self):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
        if rank == 0:
            self.create_directories()
        comm.barrier()
        self.write_bolos(rank, size)


if __name__ == "__main__":
    app = ParallelApp()
    app.run()
    app.end()
