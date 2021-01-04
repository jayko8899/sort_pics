#print("Hello world")
import os, time
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
from datetime import date
import hashlib

#function takes the name of an image and returns date it was taken yyyy:mm:dd
#if file fails to open "Invalid File" is returned
def get_date( file_name ):

    image = Image.open(image_folder_path + '/' + file_name)
    
    # extract EXIF data
    exifdata = image.getexif()

    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        if tag == tag_name:
            data = exifdata.get(tag_id)
            return data[0:10].replace(":", "_")

    #did not have date created field in exif data so we will use modified date
    timestamp = os.path.getmtime(image_folder_path + '/' + file_name)
    dt_object = date.fromtimestamp(timestamp)
    m_date = dt_object.isoformat()
    m_date = m_date.replace("-", "_")
    return m_date

#function deletes all files in image folder ignoring directories
def clear_files():
    f_list = os.listdir(image_folder_path)
    for name in f_list:
        if os.path.isdir(image_folder_path + '/' + name):
            continue
        else:
             os.remove(image_folder_path + '/' + name)

#acceptable file types
ftypes = {"jpg", "JPG", "JPEG", "THM", "PNG", "png"}
#tag name to be extracted
tag_name = "DateTimeOriginal"
#src folder
image_folder_path = "/home/jja/JJA/temp/Photos_Sort"
file_list = os.listdir(image_folder_path)

for fn in file_list:


    if os.path.isfile(image_folder_path + '/' + fn):

        #grabbing the extension of the file
        ext = fn.split('.',1)[1]
        #seeing if current file is an acceptable type
        if ext not in ftypes:   
            continue

        #getting the date from the file    
        date_result = get_date(fn)
        
        if date_result == "Invalid File":
            print("Invalid File: ", fn)
            continue

        print(fn, " ", date_result)

        dest = image_folder_path + '/' + date_result

        #if date directory already exists we want to copy new file to it
        #if not we want to create it
        if os.path.exists(dest):

            #checking if file already exists
            if os.path.exists(dest + '/' + fn):

                #generating md5 hashes
                old_file = open(dest + '/' + fn, 'rb')
                new_file = open(image_folder_path + '/' + fn, 'rb')
                old_file_read = old_file.read()
                new_file_read = new_file.read()
                
                old_md5_hash = hashlib.md5()
                new_md5_hash = hashlib.md5()

                old_md5_hash.update(old_file_read)
                new_md5_hash.update(new_file_read)

                old_check = old_md5_hash.hexdigest()
                new_check = new_md5_hash.hexdigest()

                #checking if files are the same
                if old_check == new_check:
                    pass
                else:

                    #prompt user for new file name then rename new file and copy to dest folder
                    rename_prompt = f"Name conflict of unequal files: {fn} \nPlease enter new file name:\n"
                    new_name = input(rename_prompt)
                    os.rename(image_folder_path + '/' + fn, image_folder_path + '/' + new_name)
                    shutil.copy2(image_folder_path + '/' + new_name, dest)
            else:

                #no file conflict, we just copy
                shutil.copy2(image_folder_path + '/' + fn, dest)
        else:

            #directory didnt exist, create directory and copy file to it
            os.mkdir(dest)
            shutil.copy2(image_folder_path + '/' + fn, dest)
    else:
        continue

clear_files()