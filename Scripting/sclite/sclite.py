import re
import subprocess
import sys
import os

# sclite alignment
GT_FILENAME = sys.argv[1]
folder = sys.argv[2]
#flags = sys.argv[3:]
sclite_path = '/Users/i530455/Downloads/sctk-2.4.10/bin/sclite'

def get_wer(GT_FILENAME,fpath):
    try:
        args = [sclite_path, '-r', GT_FILENAME, '-h', fpath, '-i', 'rm', '-p']  # sclite needs to be in $PATH
        #print("args: ",args)
        align_str = subprocess.check_output(args).decode("utf-8")
        align_str = re.sub(r'".+"', '', align_str)
        align_str = re.sub(r'<.+>', '', align_str)
        align_str = "".join(align_str.split())
        #print("out: ",align_str)
    except Exception as e:
        print("BenchmarkEngine: align_transcripts: error occurred running 'sclite': %s", e)
        raise Exception(e)

    # calculate WER from alignment string
    numer = align_str.count('I') + align_str.count('S') + align_str.count('D')
    denom = align_str.count('C') + align_str.count('S') + align_str.count('D')
    if denom == 0:
        wer = 0.0
    else:
        wer = numer / denom * 100.0

    #print("[ {} ] wer: {}".format(fpath,wer))
    return wer


if GT_FILENAME == "--diff-gt":
    print("diff gt mode")
    if not os.path.isfile(folder):
        print(os.listdir(folder))
        for foldername in os.listdir(folder):
            path = os.path.join(folder,foldername)
            print(path)
            if os.path.isfile(path):
                continue
            print(foldername,": ",get_wer(os.path.join(path,"gt.txt"),os.path.join(path,"h.txt")))
    else:
        print(filename,": ",get_wer(GT_FILENAME,folder))
else if GT_FILENAME == "--tesseract":
    print("tesseract ocr")
    if not os.path.isfile(folder):
        print(os.listdir(folder))
        for foldername in os.listdir(folder):
            path = os.path.join(folder,foldername)
            print(path)
            if os.path.isfile(path):
                continue

            print(foldername,": ",get_wer(os.path.join(path,"gt.txt"),os.path.join(path,"h.txt")))
    else:
        print(filename,": ",get_wer(GT_FILENAME,folder))
else:
    if not os.path.isfile(folder):
        for filename in os.listdir(folder):
            path = os.path.join(folder,filename)
            if not os.path.isfile(path):
                continue
            print(filename,": ",get_wer(GT_FILENAME,path))
    else:
        print(folder,": ",get_wer(GT_FILENAME,folder))
