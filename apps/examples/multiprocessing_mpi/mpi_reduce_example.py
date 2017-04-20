#! /usr/bin/python

from mpi4py import MPI
import numpy

comm = MPI.COMM_WORLD

def numpy_mpi_reduce():
    send_buffer=[]
    root=0
    npix = 10
    for i in range(5):
        if comm.rank == i:
            map_ = numpy.ones(npix, dtype=numpy.double)*i
            print 'i am rank %d and my map_ is' %comm.rank, map_
    total_map = numpy.zeros(npix, dtype=numpy.double)
    comm.barrier()
    comm.Reduce([map_, MPI.DOUBLE], total_map, op=MPI.SUM, root=root)
    if comm.rank==0:
        print 'after Reduce, the total map is', total_map

def python_mpi_reduce():
    send_buffer=[]
    root=0
    for i in range(5):
        if comm.rank == i:
            t = float(i)
            print 'i am rank %d and my t is' %comm.rank, t
    total_t = 0.0
    comm.barrier()
    total_t = comm.reduce(t, root=root)
    if comm.rank==0:
        print 'after reduce, the total t is', total_t

#numpy_mpi_reduce()
python_mpi_reduce()

