import os, argparse
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
from datetime import date
import hashlib

#acceptable file types
FTYPES = {"jpg", "JPG", "JPEG", "THM", "PNG", "png"}

TAG_NAME = "DateTimeOriginal"

#function takes the name of an image and returns date it was taken yyyy:mm:dd
#if file fails to open "Invalid File" is returned
def get_date(path):

    image = Image.open(path)
    
    # extract EXIF data
    exifdata = image.getexif()

    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        if tag == TAG_NAME:
            data = exifdata.get(tag_id)
            return data[0:10].replace(":", "_")

    #did not have date created field in exif data so we will use modified date
    timestamp = os.path.getmtime(path)
    dt_object = date.fromtimestamp(timestamp)
    m_date = dt_object.isoformat()
    m_date = m_date.replace("-", "_")
    return m_date

#function deletes all files in image folder ignoring directories
def clear_files(fpath):
    f_list = os.listdir(fpath)
    for name in f_list:
        if os.path.isdir(fpath + '/' + name):
            continue
        else:
             os.remove(fpath + '/' + name)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("src_folder", help="Source folder to read raw media files from")
    parser.add_argument("dest_folder", help="Destination folder to store media files in once sorted")
    parser.add_argument("-d", '--delete', help="If set old media files will be deleted after they have been sorted", action = "store_true", required=False)

    args = parser.parse_args()

    src_image_folder_path = args.src_folder
    dest_image_folder_path = args.dest_folder
    file_list = os.listdir(src_image_folder_path)

    for fn in file_list:

        src_file_path = src_image_folder_path + '/' + fn

        if os.path.isfile(src_file_path):

            #grabbing the extension of the file
            ext = fn.split('.',1)[1]
            #seeing if current file is an acceptable type
            if ext not in FTYPES:   
                continue

            #getting the date from the file    
            date_result = get_date(src_file_path)
            
            if date_result == "Invalid File":
                print("Invalid File: ", fn)
                continue

            print(fn, " ", date_result)

            dest = dest_image_folder_path + '/' + date_result

            #if date directory already exists we want to copy new file to it
            #if not we want to create it
            if os.path.exists(dest):

                #checking if file already exists
                if os.path.exists(dest + '/' + fn):

                    #generating md5 hashes
                    old_file = open(dest + '/' + fn, 'rb')
                    new_file = open(src_file_path, 'rb')
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
                        os.rename(src_file_path, src_image_folder_path + '/' + new_name)
                        shutil.copy2(src_image_folder_path + '/' + new_name, dest)
                else:

                    #no file conflict, we just copy
                    shutil.copy2(src_file_path, dest)
            else:

                #directory didnt exist, create directory and copy file to it
                os.mkdir(dest)
                shutil.copy2(src_file_path, dest)
        else:
            continue
    
    if args.delete:
        clear_files(src_image_folder_path)

if __name__ == "__main__":
    main()