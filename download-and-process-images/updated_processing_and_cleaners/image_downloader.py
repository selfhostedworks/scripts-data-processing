import csv
import os
import requests
import sys
import time
# import requests_cache
from concurrent.futures import ProcessPoolExecutor as PoolExecutor
from image_processor import change_image_type, resize_image, add_padding, convert_to_greyscale
from types import SimpleNamespace


#progress bar
def progressBar(total, progress):
    """
    Displays or updates a console progress bar.

    """
    barLength, status = 50, ""
    progress = float(progress) / float(total)
    if progress >= 1.:
        progress, status = 1, "\r\n"
    block = int(round(barLength * progress))
    text = "\r[{}] {:.2f}% {}".format(
        "#" * block + "-" * (barLength - block), round(progress * 100, 2),
        status)
    sys.stdout.write(text)
    sys.stdout.flush()



# Get filename and load it
def getFileFromUser():
    print('Please input required data...')
    print('File name for processing: (test.csv, example.csv)')
    while True:
        filename = input()

        filecontents = []
        try:
            with open(filename, encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                index = 0
                for row in csv_reader:
                    filecontents.append(row)
                return filecontents
        except:
            print(f"{filename} does not exists!")
            print('Try again or input 0 to exit!')
            pass

# Try to get image extension
# If not available, image will not be downloaded as it cannot be used further
def getImageExtension(r):
    content = r.headers['Content-Type'].lower()
    if 'image' in content:
        if 'svg' in content:
            return '.svg'
        else:
            return '.' + content.split('/')[1]  
    return None

def downloadLogos(file, logo_name_index,logo_url_index):
    processedCSV = []

    #create original folder if it doesn't exists
    if not os.path.isdir('originals'):
        os.mkdir('originals')
    # with PoolExecutor(max_workers=12) as executor:
    #     for _ in executor.map(downloadImage, [(x, logo_name_index, logo_url_index) for x in file]):
    #         pass
    counter = 1
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0"
    }
    # download each image from URL
    for row in file:
        counter += 1
        progressBar(len(file), counter)

        logo_name = row[logo_name_index]
        logo_url = row[logo_url_index]
        error_list = []
        if logo_url:
            try:
                r = requests.get(logo_url, timeout=10, headers=headers)
                img_ext = getImageExtension(r)
                if img_ext:
                    file_path = 'originals/' + get_image_name(logo_name, sub='_') + img_ext
                    with open('originals/' + get_image_name(logo_name, sub='_') + img_ext, 'wb') as f:
                        f.write(r.content)
                    if img_ext != '.png':
                        file_path = change_image_type(file_path, '.png')
                    row.append(file_path)

                    #add downloaded file_path to our CSV
                    processedCSV.append(row)
                else:
                    error_list.append(row)
            except:
                error_list.append(row)
        else:
            error_list.append(row)
    #mark files we were unable to download
    if (len(error_list) > 0):
        with open('unableToDownload.csv', 'a', encoding='utf-8') as eror_file:
            writer = csv.writer(eror_file)
            writer.writerows(error_list)
    return processedCSV



# Clean image name
def get_image_name(name, sub='-', ext=''):
    chars = " &._()|,'\"\\/:"
    for c in chars:
        name = name.replace(c, sub)
        name = name.replace(f'{sub}{sub}', sub).strip(sub)
    name = name.replace(f'{sub}{sub}', sub).strip(sub)
    return f'{name}{ext}'.lower()

# Get info about images and use that to process them
def getProcessingInfoFromUser():
    global image_height, image_width, image_height_w_pad, image_width_w_pad, padding, padding_color, images_type

    print('Image width without padding:')
    image_width = int(input())
    print('Image height without padding:')
    image_height = int(input())
    
    print('Do you need padding? ( 1 - Yes, 0 - No)')
    padding = int(input())
    
    if (padding == 1):
        print('Image width including padding:')
        image_width_w_pad = int(input())
        print('Image height including padding:')
        image_height_w_pad = int(input())
        print('What color do you need for padding? (white, black, transparent)')
        padding_color = input()
    
    print('What type of images you need? (1 - Color, 2 - Black & White, 3 - Both)')
    images_type = int(input())
    tmp = os.system('clear')
    
    print('='*30)
    print('Images will be resized to', image_width, 'x', image_height)
    if (padding == 1):
        print('Padding if required will be added in', padding_color, 'color to match size of ', image_width_w_pad, 'x',image_height_w_pad)
    print('='*30)
    print('Is this ok? ( 1 - Yes, 2 - No, try again with parameters, 0 - Abort process)')
    answer = int(input())
    if (answer == 0):
        exit()
    elif (answer == 1):
        global ask_user
        ask_user = False

def generateColorImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color):
    return_list = []
    if not os.path.isdir('color'):
        os.mkdir('color')
    counter = 1
    return_list = []
    for row in processedCSV:
        counter += 1
        progressBar(len(processedCSV), counter)
        new_name = row[-1].replace('originals/', 'color/color_').replace('.png','')
        if (padding == 1):
            new_name = f"{new_name}-{image_width_w_pad}x{image_height_w_pad}.png"
            padding_argument = f"-background {padding_color} -gravity center -extent {image_width_w_pad}x{image_height_w_pad}"
            resize_image(row[-1], new_name, image_width, image_height, padding_argument)
        else:
            new_name = f"{new_name}-{image_width}x{image_height}.png"
            resize_image(row[-1], new_name, image_width, image_height, 0)
        item = SimpleNamespace()
        item.logo_name = row[-1]
        item.type = 'color'
        item.output_file_name = new_name
        return_list.append(item)
    tmp = os.system('clear')
    print('Done with color images resizing...')
    return return_list

def generatebwImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color):
    if not os.path.isdir('bw'):
        os.mkdir('bw')
    counter = 1
    return_list = []
    for row in processedCSV:
        counter += 1
        progressBar(len(processedCSV), counter)
        new_name = row[-1].replace('originals/', 'bw/bw_').replace('.png','')
        if (padding == 1):
            new_name = f"{new_name}_{image_width_w_pad}x{image_height_w_pad}.png"
            padding_argument = f"-background {padding_color} -gravity center -extent {image_width_w_pad}x{image_height_w_pad}"
            resize_image(row[-1], new_name, image_width, image_height, padding_argument)
        else:
            new_name = f"{new_name}_{image_width}x{image_height}.png"
            resize_image(row[-1], new_name, image_width, image_height, 0)
        item = SimpleNamespace()
        item.logo_name = row[-1]
        item.type = 'black and white'
        item.output_file_name = new_name
        return_list.append(item)
    tmp = os.system('clear')
    # convert copied to gray
    print('Making them gray now.')
    counter = 0
    for row in processedCSV:
        
        counter += 1
        progressBar(len(processedCSV), counter)
        new_name = row[-1].replace('originals/', 'bw/bw_').replace('.png','')
        new_name = f"{new_name}_{image_width}x{image_height}.png"
        convert_to_greyscale(new_name)
    tmp = os.system('clear')
    print('Done with bw images resizing...')
    return return_list

def dump_html_file(outputCSV, prefix):
    html_head = """<html><head><style>table {border-collapse: collapse;}tr{height: 175px;}th,td{border: 1px solid;padding: 3px 5px;}img {width: 175px;height: auto;}
                    </style></head><body><table><thead><tr><th>###</th><th>Logo Name</th><th>File Type</th><th>Output File Name</th><th>URL</th><th>Logo Image</th></tr></thead><tbody>"""
    html_end = """ </tbody></table></body></html>"""
    id_counter = 0
    html_content = ''
    for row in outputCSV:
        id_counter += 1
        html_content += f""" <tr><td>{id_counter}</td><td>{row.logo_name}</td><td>{row.type}</td><td>{row.output_file_name}</td><td>{prefix}{row.output_file_name}</td><td><img src='{row.output_file_name}' /></td>
                            </tr> """
    html = f"{html_head}{html_content}{html_end}"
    with open('table-logo.html', 'w') as f:
        f.write(html)


def dump_processed_csv_file(processedCSV, outputCSV):
    #write initial headers for file
    with open('processed_output.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['logo_name','file_type','output_file_name','output_file_URL'])
    # get processed in shape
    for row in outputCSV:
        row.logo_name = row.logo_name.replace('originals/', '')
    
    # get originals in shape
    for row in processedCSV:
        item = SimpleNamespace()
        item.logo_name = row[-1]
        item.logo_name = item.logo_name.replace('originals/','')
        item.type = 'original'
        item.output_file_name = row[-1]
        outputCSV.append(item)
    outputCSV.sort(key=lambda x: x.logo_name)
    print('Do you want to append some prefix for output files? ( 1 - Yes, 0 - No)') 
    answer = int(input())
    if (answer == 1):
        print('Please type in prefix:')
        prefix = input()
    else:
        prefix = ''
    print('Generating new CSV file and html file for you to review...')
    
    for row in outputCSV:
        csv_row = [row.logo_name, row.type, row.output_file_name, f"{prefix}{row.output_file_name}"]
        with open('processed_output.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(csv_row)
    dump_html_file(outputCSV, prefix)
    print('Done...')
    print('Exiting. Bye!')



###################################################################################################################
###################################################################################################################
###################################################################################################################

if( __name__ == "__main__" ):
    try:
        #Get filename for processing from user input
        file = getFileFromUser()

        # if headers are present remove headers from file
        print('Does file contains headers? ( 1 - Yes, 0 - No)')
        has_headers = int(input())
        if (has_headers == 1):
            headers = file.pop(0)
            print(headers)
        else:
            headers = file[0]
        
        # Get basic info from user about file structure for downloading
        tmp = os.system('clear')
        print('Here is first line of file:')
        for i in range(len(headers)):
            print( str(i) + ' - ' + headers[i]) 
        print('What column contains logo name?')
        logo_name_index = int(input())
        print('What column contains logo url?')
        logo_url_index = int(input())
        tmp = os.system('clear')
        print('Thank you. Getting images now and converting them as necessary to correct file format, please wait a bit ...')
        
        # Get all the images from file
        processedCSV = downloadLogos(file, logo_name_index,logo_url_index)
        print('Finished with downloading and converting to .png format. Let us process this now.')

        #default values for image processing
        image_height = 0
        image_width = 0
        image_height_w_pad = 0
        image_width_w_pad = 0
        padding_color = 'transparent'
        padding = 0
        images_type = 1

        # Get user input
        ask_user = True
        while ask_user:
            getProcessingInfoFromUser()
        print('Starting process of resizing...')
        outputCSV = []
        if (images_type == 1):
            print('Resizing and generating color images...')
            outputCSV = generateColorImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color)
        elif (images_type == 2):
            print('Resizing and generating black and white images...')
            outputCSV = generatebwImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color)
        elif (images_type == 3):
            print('Resizing and generating both color and b&w images...')
            outputCSV = generateColorImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color)
            bw_output = generatebwImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color)
            outputCSV.extend(bw_output)
        print('Done, moving on...')
        time.sleep(1)
        tmp = os.system('clear')
        # Dump new CSV File
        dump_processed_csv_file(processedCSV, outputCSV)
    except (KeyboardInterrupt):
        print('Exit by user. Bye!')
        exit()