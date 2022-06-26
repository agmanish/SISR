from urllib.request import urlopen
from zipfile import ZipFile
import os
import random
import glob
import argparse
import shutil
import random

import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('split-folders')

import splitfolders

def create_dataset(oppath="/content/generated_dataset",
                   dataurl ='https://zenodo.org/record/4291940/files/data.zip',
                   samplesize=1000,
                   ttv_ratio ="8:1:1",
                   filetype=".jpg"):

  #download file from dataurl and extract the zip file
  filename=dataurl.rsplit('/', 1)[-1]
  dirname=filename.replace(".zip","")
  datapath = os.getcwd()
  zipresp = urlopen(dataurl)
  tempzip = open(os.path.join(datapath,filename), "wb")
  tempzip.write(zipresp.read())
  tempzip.close()
  zf = ZipFile(os.path.join(datapath,filename))
  zf.extractall(path = datapath)
  zf.close()
  os.remove(os.path.join(datapath,filename))

  #create lists of all files of specified filetype (filetype) 
  filepaths=[]
  for root, dirs, files in os.walk(os.path.join(datapath,dirname)):
	  for file in files:
		  if(file.endswith(filetype)):
			  filepaths.append(os.path.join(root,file))

  random.shuffle(filepaths)

  #Generate the train/val/test split
  ratios=ttv_ratio.split(":")
  train_ratio=int(ratios[0])/(int(ratios[0])+int(ratios[1])+int(ratios[2]))
  val_ratio=int(ratios[1])/(int(ratios[0])+int(ratios[1])+int(ratios[2]))
  test_ratio=int(ratios[2])/(int(ratios[0])+int(ratios[1])+int(ratios[2]))

  #Generate SR directory and copy all files
  if not os.path.exists(os.path.join(datapath,"temp","SR")):
    os.makedirs(os.path.join(datapath,"temp","SR"))

  for i in range(0,samplesize):
    src_path = filepaths[i]
    src_file = filepaths[i].rsplit('/', 1)[-1]
    dst_path =os.path.join(datapath,"temp","SR",src_file)
    try:
      shutil.copyfile(src_path, dst_path)
    except shutil.SameFileError:
      pass

  output_dir=os.path.join(oppath)
  temp_dir=os.path.join(datapath,"temp")
  splitfolders.ratio(temp_dir, output=output_dir,
    seed=1337, ratio=(train_ratio, val_ratio, test_ratio), group_prefix=None, move=False)
  
  ttv=["test","train","val"]
  for dir in ttv:
    src_dir=os.path.join(oppath,dir,"SR")
    srfiles=os.listdir(src_dir)
    dest_dir=os.path.join(oppath,dir)
    for srfile in srfiles:
      if(srfile.endswith(filetype)):
        os.rename(os.path.join(src_dir,srfile),os.path.join(dest_dir,srfile))
    shutil.rmtree(src_dir)

  shutil.rmtree(os.path.join(datapath,"__MACOSX"))
  shutil.rmtree(os.path.join(datapath,dirname))
  shutil.rmtree(os.path.join(datapath,"temp"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--download-url', type=str, default="https://zenodo.org/record/4291940/files/data.zip")
    parser.add_argument('--output-path', type=str, default="/content/generated_dataset")
    parser.add_argument('--sample-size', type=int, default=1000)
    parser.add_argument('--train-val-test-ratio', type=str, default="8:1:1")
    parser.add_argument('--image-type', type=str, default=".jpg")
    args = parser.parse_args()

    DOWNLOAD_URL=args.download_url
    OUTPUT_PATH=args.output_path
    SAMPLE_SIZE=args.sample_size
    TVT_RATIO=args.train_val_test_ratio
    IMAGE_TYPE=args.image_type
    
    create_dataset(oppath=OUTPUT_PATH, dataurl=DOWNLOAD_URL, samplesize= SAMPLE_SIZE, ttv_ratio=TVT_RATIO, filetype=IMAGE_TYPE)

