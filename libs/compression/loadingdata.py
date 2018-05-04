#!/usr/bin/env python2

import os
import pylab
import pygetdata

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
    if need_to_close:
        dirfile.close()
    return data

def channel_to_txt(dataset_path, channel_names, board_num=None):

    if type(channel_names) is str:
        channel_names = [channel_names]
    for i, channel_name in enumerate(channel_names):
        start_frame = 0
        for segment_name in sorted(os.listdir(dataset_path)):
            if board_num is not None:
                segment_path = os.path.join(dataset_path, "board%i" % board_num)
            else:
                segment_path = os.path.join(dataset_path, segment_name)
            if os.path.exists(segment_path):
                for subsegment_name in sorted(os.listdir(segment_path)):
                    dirfile_path = os.path.join(segment_path, subsegment_name)
                    channel = load_channel(dirfile_path, channel_name)
		    print(channel)
		    thefile = open('%s.txt' %subsegment_name, 'w')
		    for item in channel:
		        thefile.write("%s\n" %item)
		    thefile.close()
                    start_frame += len(channel)



def save_to_txt():

    dataset_path = "/home/williaje/so/lab_analysis/libs/compression"
    channel_names = os.listdir("/home/williaje/so/lab_analysis/libs/compression/board58/subsegment0")
    cn = [x.split('.')[0] for x in channel_names]
    cn.remove('format')
    cn.remove('board58_hwp_angle')
    channel_to_txt(dataset_path, cn, 58)

if __name__ == "__main__":
  save_to_txt()
