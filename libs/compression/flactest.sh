#!/bin/bash

$(python3 makewav.py)

for file in *.npy

do 

og_file_size=$(stat -c%s "$file")

flac=$(flac "$file" --compression-level-8 --endian="little" --sign="signed" --channels="1" --bps="16" --sample-rate="100" -f)

done

for file in *.flac

do 

#get meta-data from files just in case
meta=$(metaflac --show-bps --show-channels --show-total-samples "$file")

#get file size
file_size=$(stat -c%s "$file")

perc=$(bc <<< "scale =2; ($og_file_size - $file_size)/$og_file_size * 100 ")
echo "$perc %"

done


