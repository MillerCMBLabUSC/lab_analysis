#!/usr/bin/env python2

import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import pylab
import pygetdata
import pickle
import sys


def load_channel(dirfile_or_dirfile_path, channel_name, first_frame=0, num_frames=None):

    need_to_close = False
    if type(dirfile_or_dirfile_path) == pygetdata.dirfile:
        dirfile = dirfile_or_dirfile_path
    else:
        dirfile = pygetdata.dirfile(dirfile_or_dirfile_path)
        need_to_close = True
    if num_frames is None:
        num_frames = dirfile.nframes
    data = dirfile.getdata(channel_name, dirfile.native_type(channel_name),
                           first_frame=first_frame, num_frames=num_frames)
    #data = dirfile.getdata(channel_name, first_frame=first_frame, num_frames=num_frames)
    if need_to_close:
        dirfile.close()
    return data

def channel_to_txt(dataset_path, channel_names, board_num=None):
    count = 0
    if type(channel_names) is str:
        channel_names = [channel_names]
    for i, channel_name in enumerate(channel_names):
#	if i == 0:
#	    axes = pylab.subplot(len(channel_names)*100 + 11 + i)
#	else:
#	    pylab.subplot(len(channel_names)*100 + 11 + i, sharex = axes)
        start_frame = 0
        for segment_name in sorted(os.listdir(dataset_path)):
            if board_num is not None:
                segment_path = os.path.join(dataset_path, "board%i_calib" % board_num)
            else:
                segment_path = os.path.join(dataset_path, segment_name)
            if os.path.exists(segment_path):
                for subsegment_name in sorted(os.listdir(segment_path)):
                    dirfile_path = os.path.join(segment_path, subsegment_name)
                    channel = load_channel(dirfile_path, channel_name)
#		    indices = pylab.arange(len(channel)) + start_frame
#		    pylab.plot(indices, channel)
		    thefile = open('board58_calib_%s.txt' %count, 'w')
		    for item in channel:
		        thefile.write("%s\n" %item)
		    thefile.close()
		    #np.array(channel).dump(open('%s_calib.npy' %count, 'wb'))
                    #with open('%s_ss.pkl' %count, 'wb') as f:
                    #    pickle.dump(channel,f)
                    start_frame += len(channel)
                    count = count + 1



def save_to_txt():

    dataset_path="/home/williamscommajason/williamscommajason"
    #dataset_path = "/home/williaje/so/lab_analysis/libs/compression"
    #channel_names = os.listdir("/home/williaje/so/lab_analysis/libs/compression/board58/subsegment0/subsegment0")
    #channel_names = os.listdir("/home/williamscommajason/williamscommajason/board59_calib/subsegment0/subsegment0")
    channel_names = os.listdir("/home/williamscommajason/williamscommajason/board58_calib/subsegment0")[-20:]
    #channel_names = ["board58_mb_temp1","board58_mb_temp2","board58_mb_temp3","board58_source_ts","board58_mezz1_temp","board58_mezz2_temp"]
    print(channel_names)
    cn = [x.split('.')[0] for x in channel_names]
    cn.remove('format')
    #cn = cn[0]
    #print(cn)
    #cn.remove('board58_hwp_angle')
    channel_to_txt(dataset_path, cn, 58)
    #pylab.show()

if __name__ == "__main__":
  save_to_txt()
