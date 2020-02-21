import re
import subprocess
import sys
import os
import io
import asrtoolkit

# sclite alignment
GT_PATH = sys.argv[1]
folder = sys.argv[2]
#flags = sys.argv[3:]
sclite_path = '/Users/i530455/Downloads/sctk-2.4.10/bin/sclite'
tmp_path = os.getcwd()+'/tmp/'

def getFile(fpath):
    print(fpath)
    if(not os.path.isdir(tmp_path)):
        os.mkdir(tmp_path)
    bad_chars = ['(',')','\\n','#','`',"'",'"','|','@']
    txt = ''
    with io.open(fpath, 'rt') as file:
        for line in file:
            for invalid in bad_chars:
                line = line.replace(invalid, " ")
            txt += line+" "
            #txt = "".join([i for i in txt if not bad_chars.contains(i)])
        if txt[-1] != '\n':
            txt += '\n'
    tmpfile_path = os.path.join(tmp_path,os.path.basename(fpath))
    with io.open(tmpfile_path,'wt') as file2:
        file2.write(txt)
        #print(file2.read())
    return tmpfile_path

def getWER(gtpath,fpath):
    args = ["wer", '--char-level', fpath, gtpath]  # sclite needs to be in $PATH
    #print("args: ",args)
    align_str = subprocess.check_output(args).decode("utf-8")
    #print(align_str)
    return align_str[5:]
    '''
    try:
        gt = getFile(gtpath)
        h = getFile(fpath)
        args = [sclite_path, '-r', gt, '-h', h, '-i', 'rm', '-p']  # sclite needs to be in $PATH
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
        wer = float(numer) / float(denom) * 100.0

    #print("[ {} ] wer: {}".format(fpath,wer))
    cleanup()
    '''
    #return wer

def cleanup():
    if(os.path.isdir(tmp_path)):
        for filename in os.listdir(tmp_path):
            os.remove(filename)

if GT_PATH == "--diff-gt":
    print("diff gt mode")
    if not os.path.isfile(folder):
        #print(os.listdir(folder))
        documents = sorted(os.listdir(folder))
        print(documents)
        for foldername in documents:
            path = os.path.join(folder,foldername)
            #print(path)
            if os.path.isfile(path):
                continue
            print(foldername,": ",getWER(os.path.join(path,"gt.txt"),os.path.join(path,"h.txt")))
    else:
        print('invalid input') #filename,": ",get_wer(GT_PATH,folder))
else:
    if not os.path.isfile(folder):
        for filename in os.listdir(folder):
            path = os.path.join(folder,filename)
            if not os.path.isfile(path):
                continue
            print(filename,": ",getWER(GT_PATH,path))
    else:
        print(folder,": ",getWER(GT_PATH,folder))
