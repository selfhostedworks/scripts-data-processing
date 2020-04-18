# Image Processing Scripts
1. Download 

## Install
1. Run `sudo apt-get install libcanberra-gtk-module`
2. Run `sudo apt-get install python3-pip python3 imagemagick inkscape webp`
3. Run `pip install requirements.txt`

- you an also run `sh setup.sh` to automatically install the dependencies and python requirements

## Dependencies

- **imagemagick:** used for image conversions.
- **inkscape:** For converting SVG to PNG files.
- **webp:** For converting webp to PNG

## Use:

1. Run `sh download_and_process.sh your-filename.csv` to run the 
	- **download images** which downloads the images and converts to png
	- **image processing** script converts to grayscale and 175x175 px.
	- **html from csv** which creates a table of company names and logos, so you can spot check them if you have hundreds.

* Or run `python3 image_downloader.py the-list.csv` if you just want to download images
* Or run `python3 image_processor.py the-list.csv` if you just want to process and convert them.
* Or run `python3 html_crom_csv.py` to create the table

### File format
The `.csv` file must have the following headers for the python scripts to work:


| ID | Organization | HQ_Country | HQ_City/State | LinkedIn | New Logo URL | Website | Bio |
|----|--------------|------------|---------------|----------|--------------|---------|-----|
|    |              |            |               |          |              |         |     |


### Notes
- It will automatically make a backup of the image, or image directory first.
- log file contains data about the run
- Cache is there to avoid unnecessarily downloading

- Use `--help` for command line arguments.

