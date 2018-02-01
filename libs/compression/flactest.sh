#!/bin/bash


$(python3 makewav.py $1)


#get original binary file size and make flac files

find *.bin \
	| \
	(
	while read file
	do
	og_file_size=$(stat -c%s "$file")
	flac=$(flac "$file" --compression-level-8 --endian="little" --sign="signed" --channels="1" --bps="24" --sample-rate="100" -f &> /dev/null)

	#find the newly created .flac file, and then calculate the difference

	find *.flac \
		| \
		(
		while read otherfile
		do
		#get meta data from files just in case
		meta=$(metaflac --show-bps --show-channels --show-total-samples "$otherfile")

		#get file size
		file_size=$(stat -c%s "$otherfile")

		#calculate the compression ratio and place the value in a text file
		perc=$(bc <<< "scale=5; ($og_file_size - $file_size)/$og_file_size * 100")
		echo "$perc" >> arrayfile.txt
		rm $otherfile
		done
		)
	done
	)

#remove the initial binary file
for file in *.bin
	do
	rm $file
done

#make a histogram

function histo {

python3 - <<END
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

filename = np.loadtxt('arrayfile.txt', unpack = 'False')
length = len(filename)

plt.hist(filename, bins = 'auto' , histtype = 'bar')
plt.xlabel('compression ratio (%)')
plt.ylabel('blah')
plt.title('Histogram of %a compression ratios'%length)
plt.legend()
plt.show()
END
}

histo

#clear the text file

> arrayfile.txt
