#! /usr/bin/env python

from mpi4py import MPI
from itertools import chain
import os
from leap.lib.leap_app import leap_app
from leap.lib.io_management import dirfile_loading

class ExampleMPIApp(leap_app.App):

    def run(self):
        # On different nodes, the path to the settings file won't be found, hence the following lines
        if not hasattr(self, "settings"):
            from leap.apps.simulated_timestreams.bolo import custom_settings
            self.settings = custom_settings.settings
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        num_process = comm.Get_size()
        # Creating output directory only for rank0
        if rank == 0:
            self.create_output()
            segments = dirfile_loading.load(self.settings.dirfile_loading)
            for segment in segments:
                for board in segment.unloaded_board_datasets:
                    self.create_board_directory(segment.name, board.name)
        else:
            self.out_path = None
        comm.barrier()
        self.out_path = comm.bcast(self.out_path, root=0) 
        comm.barrier()
        # Doing application for every segment board
        segments = dirfile_loading.load(self.settings.dirfile_loading)
        counter = 0
        hit_pixels = []
        for segment in segments:
            for board in segment.unloaded_board_datasets:
                if counter % num_process == rank:
                    print "I am rank %d doing segment-board %s %s" %(rank, segment.name, board.name)
                    output_array = self.do_my_app(rank)
                counter += 1
        # The following is to reunite all arrays from every processor into one array
        comm.barrier()
        total_output_array = comm.gather(output_array, root=0)
        comm.barrier()
        if rank == 0:
            total_output_array = list(chain(*total_output_array))
            print 'total output array'
            print total_output_array
            # Note that self.end() is only called once
            self.end()

    def do_my_app(self, rank):
        return [rank]*rank
        
    def create_board_directory(self, segment_name, board_name):
        os.makedirs(os.path.join(self.out_path, "bolo/bolo_simul_etime_v3-0", segment_name, 
                    board_name))
        os.makedirs(os.path.join(self.out_path, "bolo/bolo_simul_template_removed_v3-0", 
                    segment_name, board_name))
        os.makedirs(os.path.join(self.out_path, "bolo/bolo_simul_bolo_v3-0", 
                    segment_name, board_name))


if __name__ == "__main__":
    sim_timestreams = ExampleMPIApp()
    sim_timestreams.run()
