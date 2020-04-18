#!/bin/bash
# this will download and perform the image processing to your original requirements
# the scripts were written and intended to run individually, this is just a wrapper
# for convenience

if [ -z $1 ];

then 
echo ''
echo .csv file with appropriate layout required.;
echo "ID |  Organization |  HQ_Country |  HQ_City/State | LinkedIn | New Logo URL | Website | Bio"

exit;
fi;

./image_downloader.py $1;

./image_processor.py logos-otm --resize --greyscale --background-color white
