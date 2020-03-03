import glob
import os
import hashlib

def remove_duplicates(folder):
    
    img_files = glob.glob( folder + "/*.jpg")

    image_dict = dict()

    for filename in img_files:
        with open(filename, 'rb') as image_file:
            image_hash = hashlib.md5(image_file.read()).hexdigest()

        if image_hash in image_dict:
            print("File {0} is a duplicate of {1}".format(filename, image_dict[image_hash]))
        else:
            image_dict[image_hash] = filename
        
    print("done {0} images".format(len(img_files)))1


if __name__ == '__main__':
    folder = ''
    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("Incorrect arguments. Please run python remove-duplicates.py <file-path>")
        sys.exit(1)

    remove_duplicates(folder)
