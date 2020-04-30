import csv
import os
import requests
# import requests_cache
from concurrent.futures import ProcessPoolExecutor as PoolExecutor
from image_processor import change_image_type, resize_image, add_padding, convert_to_greyscale
from types import SimpleNamespace
#progress bar

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()



# Get filename and load it
def getFileFromUser():
    print('Please input required data...')
    print('File name for processing: (test.csv, example.csv)')

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
        exit()

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
    if not os.path.isdir('ORIGINALS'):
        os.mkdir('ORIGINALS')
    # with PoolExecutor(max_workers=12) as executor:
    #     for _ in executor.map(downloadImage, [(x, logo_name_index, logo_url_index) for x in file]):
    #         pass
    counter = 1

    for row in file:
        counter += 1
        printProgressBar(counter, len(file), prefix = 'Progress:', suffix = 'Complete', length = 50, printEnd = "\r")

        logo_name = row[logo_name_index]
        logo_url = row[logo_url_index]
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0"
        }
        error_list = []
        if logo_url:
            try:
                r = requests.get(logo_url, timeout=10, headers=headers)
                img_ext = getImageExtension(r)
                if img_ext:
                    file_path = 'ORIGINALS/' + get_image_name(logo_name, sub='_') + img_ext
                    with open('ORIGINALS/' + get_image_name(logo_name, sub='_') + img_ext, 'wb') as f:
                        f.write(r.content)
                    if img_ext != '.png':
                        file_path = change_image_type(file_path, '.png')
                    row.append(file_path)
                    processedCSV.append(row)
                else:
                    error_list.append(row)
            except:
                error_list.append(row)
        else:
            error_list.append(row)
        with open('unableToDownload.csv', 'a', encoding='utf-8') as eror_file:
            writer = csv.writer(eror_file)
            writer.writerow(error_list)
    return processedCSV

# Clean image name
def get_image_name(name, sub='-', ext=''):
    chars = " &._()|,'\"\\/:"
    for c in chars:
        name = name.replace(c, sub)
        name = name.replace(f'{sub}{sub}', sub).strip(sub)
    name = name.replace(f'{sub}{sub}', sub).strip(sub)
    return f'{name}{ext}'.lower()


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
    print('------------------------------------------------------------------------------------')
    print('Images will be resized to', image_width, ' x ', image_height)
    if (padding == 1):
        print('Padding if required will be added in ', padding_color, 'color.')
    print('------------------------------------------------------------------------------------')
    print('Is this ok? ( 1 - Yes, 2 - No, try again with parameters, 0 - Abort process)')
    answer = int(input())
    if (answer == 0):
        exit()
    elif (answer == 1):
        global ask_user
        ask_user = False

def generateColorImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color):
    return_list = []
    if not os.path.isdir('COLOR'):
        os.mkdir('COLOR')
    counter = 1
    return_list = []
    for row in processedCSV:
        counter += 1
        # printProgressBar(counter, len(processedCSV), prefix = 'Progress:', suffix = 'Complete', length = 50, printEnd = "\r")
        new_name = row[-1].replace('ORIGINALS/', 'COLOR/color_').replace('.png','')
        new_name = f"{new_name}_{image_width}x{image_height}.png"
        if (padding == 1):
            padding_argument = f"-background {padding_color} -gravity center -extent {image_width_w_pad}x{image_height_w_pad}"
            resize_image(row[-1], new_name, image_width, image_height, padding_argument)
        else:
            resize_image(row[-1], new_name, image_width, image_height, 0)
        item = SimpleNamespace()
        item.logo_name = row[-1]
        item.type = 'color'
        item.output_file_name = new_name
        return_list.append(item)
    tmp = os.system('clear')
    print('Done with color images resizing...')
    return return_list

def generateBWImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color):
    if not os.path.isdir('BW'):
        os.mkdir('BW')
    counter = 1
    return_list = []
    for row in processedCSV:
        counter += 1
        printProgressBar(counter, len(processedCSV), prefix = 'Progress:', suffix = 'Complete', length = 50, printEnd = "\r")
        new_name = row[-1].replace('ORIGINALS/', 'BW/bw_').replace('.png','')
        new_name = f"{new_name}_{image_width}x{image_height}.png"
        if (padding == 1):
            padding_argument = f"-background {padding_color} -gravity center -extent {image_width_w_pad}x{image_height_w_pad}"
            resize_image(row[-1], new_name, image_width, image_height, padding_argument)
        else:
            resize_image(row[-1], new_name, image_width, image_height, 0)
        item = SimpleNamespace()
        item.logo_name = row[-1]
        item.type = 'black and white'
        item.output_file_name = new_name
        return_list.append(item)
    tmp = os.system('clear')
    # convert copied to gray
    for row in processedCSV:
        counter += 1
        printProgressBar(counter, len(processedCSV), prefix = 'Progress:', suffix = 'Complete', length = 50, printEnd = "\r")
        new_name = row[-1].replace('ORIGINALS/', 'BW/bw_').replace('.png','')
        new_name = f"{new_name}_{image_width}x{image_height}.png"
        convert_to_greyscale(new_name)
    tmp = os.system('clear')
    print('Done with bw images resizing...')
    return return_list

def dump_processed_csv_file(processedCSV, outputCSV):
    for row in processedCSV:
        item = SimpleNamespace()
        item.logo_name = row[-1]
        item.type = 'original'
        item.output_file_name = row[-1]
        outputCSV.append(item)
    print('Do you want to append some prefix for output files? ( 1 - Yes, 0 - No)') 
    answer = int(input())
    if (answer == 1):
        print('Please type in prefix:')
        prefix = input()
    else:
        prefix = ''
    for row in outputCSV:
        csv_row = [row.logo_name.replace('/ORIGINALS',''), row.type, row.output_file_name, f"{prefix}{row.output_file_name}"]
        with open('processed_output.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(csv_row)
    print('Done...')
    # dump_html_file(outputCSV)
if( __name__ == "__main__" ):
    # requests_cache.install_cache()
    processedCSV = []
    os.system('pwd')
    file = getFileFromUser()
    headers = file.pop(0)
    print(headers)
    for i in range(len(headers)):
        print( str(i) + ' - ' + headers[i]) 
    print('What column contains logo name?')
    logo_name_index = int(input())
    print('What column contains logo url?')
    logo_url_index = int(input())
    print('Thank you. Getting images now, please wait a bit ...')
    processedCSV = downloadLogos(file, logo_name_index,logo_url_index)
    print('Finished with downloading and converting to .png format. Let us process this now.')

    #default values
    image_height = 0
    image_width = 0
    image_height_w_pad = 0
    image_width_w_pad = 0
    padding_color = 'transparent'
    padding = 0
    images_type = 1


    ask_user = True
    while ask_user:
        getProcessingInfoFromUser()
    print('Starting process of resizing...')
    outputCSV = []
    if (images_type == 1):
        outputCSV = generateColorImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color)
    elif (images_type == 2):
        outputCSV = generateBWImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color)
    elif (images_type == 3):
        outputCSV = generateColorImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color)
        bw_output = generateBWImages(processedCSV, image_width, image_height, padding, image_height_w_pad, image_width_w_pad, padding_color)
        outputCSV.extend(bw_output)
    dump_processed_csv_file(processedCSV, outputCSV)