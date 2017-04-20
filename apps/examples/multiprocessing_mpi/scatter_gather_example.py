#! /usr/bin/python

from mpi4py import MPI
import numpy

comm = MPI.COMM_WORLD

def python_bcast():
    if comm.rank == 0:
        outpath = "hello"
        print "I am rank %d and outpath is : %s" %(comm.rank, outpath) 
    else:
        outpath = None
        print "I am rank %d and outpath is : %s" %(comm.rank, outpath) 
    comm.barrier()
    outpath = comm.bcast(outpath, root=0)
    comm.barrier()
    if comm.rank == 0:
        print "======= bcast done ========"
    comm.barrier()
    print "I am rank %d and outpath is : %s" %(comm.rank, outpath) 

def numpy_scatter_gather():
    send_buffer=[]
    root=0
    factor = comm.size
    if comm.rank==0:
        m=numpy.array(range(factor*comm.size),dtype=float)
        m.shape=(comm.size,comm.size)
        print 'm array made in rank 0'
        print(m)
        send_buffer=m

    receive_buff = numpy.empty(factor, dtype=float)
    comm.Scatter([send_buffer, MPI.FLOAT], receive_buff, root=root)
    print "I am rank %d and I got this array (buffer): %s" %(comm.rank, receive_buff)
    #receive_buff = receive_buff*receive_buff
    final_array = numpy.empty(factor*comm.size, dtype=float)
    comm.Gather([receive_buff, MPI.FLOAT], final_array, root=root)
    if comm.rank==0:
        print "I am rank 0 and the gathered array is", final_array


def python_objects_scatter_gather():
    send_buffer=None
    root=0
    factor = 1
    if comm.rank==0:
        m=range(factor*comm.size)
        print 'm list made in rank 0'
        print(m)
        send_buffer=m
    scattered_list = comm.scatter(send_buffer, root=root)
    print "I am rank %d and I got this array (buffer): %s" %(comm.rank, scattered_list)
    gathered_list = comm.gather(scattered_list, root=root)
    if comm.rank==0:
        print "I am rank 0 and the gathered list is", gathered_list

def python_objects_gather():
    from itertools import chain
    root=0
    if comm.rank==0:
        m = [1, 2, 3]
    if comm.rank==1:
        m = [4]
    if comm.rank==2:
        m = [5, 6, 7, 8]
    comm.barrier()
    gathered_list = comm.gather(m, root=root)
    if comm.rank==0:
        print "I am rank 0 and the gathered list is", gathered_list
        print "I am rank 0 and the gathered list is", list(chain(*gathered_list))

#python_objects_scatter_gather()
#python_objects_gather()
python_bcast()

