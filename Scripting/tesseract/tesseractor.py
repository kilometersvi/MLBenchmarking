# import the necessary packages
from PIL import Image
import pytesseract
import itertools
import cv2
import os
import platform
import pdf2image
import io
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

import sys
import argparse

class tesseractor:
    log = False
    dau = True
    rag = False
    tmp_dir = ""

    def __init__(self,delete_after_use=True,reveal_after_gen=False,do_logs=False):
        self.dau = delete_after_use
        self.rag = reveal_after_gen
        self.log = do_logs
        if platform.system() == 'Linux' and os.path.exists('/tmp/'):
            self.tmp_dir = '/tmp/'+str(os.getpid())
        elif platform.system() == 'Windows':
            self.tmp_dir = os.getcwd()+'\\'+str(os.getpid()) #lot more to be done for windows support
        else:
            self.tmp_dir = os.getcwd()+'/'+str(os.getpid())
        os.mkdir(self.tmp_dir)

    def in_directory(self,file, directory):
        directory = os.path.join(os.path.realpath(directory), '')
        file = os.path.realpath(file)
        return os.path.commonprefix([file,directory]) == directory

    def pdf_to_img(self,pdf):
        images = pdf2image.convert_from_path(pdf)
        return images

    def generate_processed(self,img_raw, preprocesses=['gray','thresh']):
        image = None
        if type(img_raw) is str:
            image = cv2.imread(img_raw)
        else:
            image = img_raw
        if "gray" in preprocesses:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # check to see if we should apply thresholding to preprocess the
            # image (needs gray)
            if "thresh" in preprocesses:
                image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # make a check to see if median blurring should be done to remove
        # noise
        elif "blur" in preprocesses:
        	image = cv2.medianBlur(image, 3)
        # write the grayscale image to disk as a temporary file so we can
        # apply OCR to it
        filename = os.path.join(self.tmp_dir,"{}.png".format(os.path.basename(img_raw).split('.')[0]))
        cv2.imwrite(filename, image)
        return filename

    def read(self,img):
        # load the image as a PIL/Pillow image, apply OCR, and then delete
        # the temporary file
        text = pytesseract.image_to_string(Image.open(img))
        if self.log or self.rag:
            print(text)
        if self.rag:
            cv2.imshow("Image", img)
            cv2.waitKey(0)
        if self.dau and self.in_directory(img,self.tmp_dir):
            print('deleting tempimg')
            os.remove(img)
        return text

    def get_all(self,img_raw):
        args_possible = ['gray','thresh','blur']
        argset = []
        results = {}
        for r in range(0,len(args_possible)+1):
            nCr = itertools.combinations(args_possible,r)
            argset.extend(nCr)
        for arg in argset:
            pimg = self.generate_processed(img_raw,list(arg))
            results[arg] = self.read(pimg)
            if self.log:
                print(list(arg),"\n",results[arg])
        return results

    def __del__(self):
        for filename in os.listdir(self.tmp_dir):
            if os.path.basename(img).split('.')[-1]=='png':
                os.remove(filename)
        os.rmdir(self.tmp_dir)

'''
t = tesseractor()
print(t.read(t.generate_processed('/home/milesmilos/Pictures/tcp3.png')))
'''

#usage: tesseractor.py <folder or file> [args]
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--src", type=str,required=True, help="path to input pdf/image/dir to be OCR'd")
ap.add_argument('-d','--dest', type=str, default='console', help='outfile dest. "console" = only print results.')
ap.add_argument('-p','--preprocess', nargs='+', help='preprocessing methods to perform.\noptions:\n\tgray\n\tthresh\n\tblur', default=['gray','thresh'])
ap.add_argument("-v", "--verbose", type=bool, default=False)
args = vars(ap.parse_args())

t = tesseractor(do_logs=args['verbose'])

if not os.path.exists(args['dest']) and args['dest'] != 'console':
    raise RuntimeError('destination does not exist.')
elif not os.path.isfile(args['src']):
    parent_path = os.path.join(args['dest'],'ocr_'+os.path.basename(args['src']))
    try:
        os.mkdir(parent_path)
    except FileExistsError:
        pass
    if args['verbose']:
        print(os.listdir(args['src']))
    for filename in os.listdir(args['src']):
        if args['verbose']:
            print('processing ',filename)
        path = os.path.join(args['src'],filename)
        result = ''
        if not os.path.isfile(path) or os.path.basename(path)[0]=='.':
            continue
        elif os.path.splitext(path)[-1] == 'pdf':
            images = t.pdf_to_img(path)
            for image in images:
                result = result + t.read(t.generate_processed(image,args['preprocess']))
        else:
            result = t.read(t.generate_processed(path,args['preprocess']))
        if args['verbose'] and args['dest'] is not 'console':
            print(result)
        if args['dest'] is 'console':
            print("{}\n{}".format(path,result))
        else:
            f = open(os.path.join(parent_path,'h_'+os.path.basename(path).split('.')[0]+'.txt'),'w')
            f.write(result)
            f.close()
else:
    path = args['src']
    if args['verbose']:
        print('processing ',os.path.basename(path))
    result = ''
    if os.path.splitext(path)[-1] == 'pdf':
        images = t.pdf_to_img(path)
        for image in images:
            result = result + t.read(t.generate_processed(image,args['preprocess']))
    else:
        result = t.read(t.generate_processed(path,args['preprocess']))
    if args['verbose'] and args['dest'] is not 'console':
        print(result)
    if args['dest'] is 'console':
        print("{}\n{}".format(path,result))
    else:
        f = open(args['dest'],'w')
        f.write(result)
        f.close()
