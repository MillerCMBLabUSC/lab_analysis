#!/bin/bash


$(python3 makewav.py $1)


#get original binary file size and make flac files

find *.npy \
	| \
	(
	while read file
	do 
	og_file_size=$(stat -c%s "$file")
	flac=$(flac "$file" --compression-level-8 --endian="little" --sign="signed" --channels="1" --bps="16" --sample-rate="100" -f &> /dev/null)

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
for file in *.npy
	do
	rm $file
done

#clear the text file

#> arrayfile.txt
