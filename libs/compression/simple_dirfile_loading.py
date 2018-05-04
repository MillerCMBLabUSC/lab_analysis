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


def plot_channels_for_flight(dataset_path, channel_names, board_num=None):
    if type(channel_names) is str:
        channel_names = [channel_names]
    for i, channel_name in enumerate(channel_names):
        if i == 0:
            axes = pylab.subplot(len(channel_names)*100 + 11 + i)
        else:
            pylab.subplot(len(channel_names)*100 + 11 + i, sharex=axes)
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
                    indices = pylab.arange(len(channel)) + start_frame
                    pylab.plot(indices, channel)
                    start_frame += len(channel)
	    #else:
	    #    print('channel')


def _plot_example():
    dataset_path = "/home/williaje/Desktop/boards"
    #dataset_path = "/data/ebex/ld2012/flight/secondary_dirfile_products/sub_base/sub_ss_v4-0"
    #dataset_path = "../../apps/base_creation/output/temp/2014-02-13--22-23-16_writing_dirfiles/sub_ss_vX-Y"
    channel_names = ["board67_wire1_ch02_template_removal_flag_all","board67_wire1_ch04_template_removal_flag_all","board67_wire1_ch04_template_removal_flag_all","board67_wire1_ch02_template_subtracted","board67_wire1_ch03_template_subtracted","board67_wire1_ch04_template_subtracted","board67_wire1_ch06_template_subtracted","board67_wire1_ch08_template_subtracted","board67_wire1_ch12_template_subtracted"]
    #channel_names = ["board70_mb_temp1", "BOARD70_SOURCE_MAJ", "BOARD70_RAW_EBEX_TIME"]
    plot_channels_for_flight(dataset_path, channel_names, 67)
    pylab.show()

if __name__ == "__main__":
    _plot_example()
