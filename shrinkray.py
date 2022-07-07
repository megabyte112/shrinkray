# shrinkray, by megabyte112
# version 1.1
# see LICENSE for license info

import sys, os, subprocess, math, shutil, logging

version = "1.1"
arg_length = len(sys.argv)

# run this after completion
def complete():
    global filein, size, newsize
    # remove input file, it's not needed
    if os.path.exists("input.mp4"):
        os.remove("input.mp4")
        logging.info("removed old input.mp4")
    logging.info("complete!")
    print("\n")
    print("Shrinking complete!\n")
    if newsize != size:
        displaysize=round((size/8192)*8000)
        newdisplaysize=round((newsize/8192)*8000)
        print(f"Compressed {displaysize}kB into {newdisplaysize}kB\n")
    else:
        print("The file was already small enough!\n")
    input("You can now close this window.")
    exit()

# setup logger
if os.path.exists("shrinkray.log"):
    os.remove("shrinkray.log")
logformat='%(asctime)s: %(message)s'
logging.basicConfig(filename="shrinkray.log", filemode="w", level=logging.INFO, format=logformat)

logging.info("shrinkray is running, version "+version)

# verbose mode
verbose = False
if sys.argv[arg_length - 1] == "verbose":
    verbose = True
    arg_length -= 1
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("verbose mode enabled")

# determine host OS
if os.name == "nt": # windows
    logging.info("host is Windows")
    expath="bin\\"
else:   # posix
    logging.info("host is non-Windows")
    expath="bin/"

# use the "bin" folder if it exists
# if not, assume everything is in PATH already
if not os.path.isdir("bin"):
    expath=""
    logging.info("using PATH")
else:
    logging.info("using bin folder")

# remove older output
if os.path.exists("output.mp4"):
    os.remove("output.mp4")
    logging.info("removed old output.mp4")

# download video if no arguments are given
if arg_length < 2:
    logging.info("prepare download...")
    if os.path.exists("input.mp4"):
        os.remove("input.mp4")
        logging.info("removed old input.mp4")
    fullurl=input("Paste a video link here.\nIt can be YouTube, Reddit, and most other video sites.\n> ")
    logging.info(f"input: \"{fullurl}\"")
    url=fullurl.split("?")[0]               # TODO: Allow FULL youtube URLs 
    if url != fullurl:
        logging.info(f"shortened input to: \"{url}\"")
    logging.info("attempting download")
    print(f"\nDownloading video {url}...")
    os.system(f"{expath}yt-dlp \"{url}\" -q -f mp4 -o input.mp4")
    filein="input.mp4"
else:
    filein=sys.argv[1]
    logging.info(f"target file {filein}")
print("\n")



if filein == "input.mp4":
    outputname = "output_shrinkray.mp4"
else:
    outputname = filein + "_shrinkray"

# text must be a number greater than 0
def CheckValidInput(text):
    return text.isnumeric() and text > 0

# ask for target file size
target_size = ""
while not CheckValidInput(target_size):
    target_size = input("Target file size in MB\n> ")
    if not CheckValidInput(target_size):
        logging.warning("rejected input: "+str(target_size))
        print("\nMake sure your input a whole number greater than 0")
targetSizeKB = target_size * 1000
logging.info("target size of",targetSizeKB+"KB")

# calculate size: no need to shrink if video is already small enough
size=os.path.getsize(filein)/1000
logging.info(f"size of input file: {size}kB")
if size < targetSizeKB:
    shutil.copy(filein, "output.mp4")
    logging.info("video is already small enough, copying to output.mp4")
    if os.path.exists("input.mp4"):
        os.remove("input.mp4")
        logging.info("removed old input.mp4")
    newsize=size
    complete()

# bitrate (in Mbps) = Size / Length
# assume 64Mb, and divide by length in seconds
length = math.floor(float(subprocess.getoutput(f"{expath}ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{filein}\"")))
logging.info(f"video length: {length}s")
totalbitrate=math.floor(targetSizeKB*8/length)
logging.info(f"total bitrate: {totalbitrate}kbps")

# get resolution
fullresolution = subprocess.getoutput(f"{expath}ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 \"{filein}\"")
logging.info("video is "+fullresolution)
splitres = fullresolution.split("x")
width = splitres[0]
height = splitres[1]
if width > height:
    orientation = 'l'
    logging.info("video is landscape")
else:
    orientation = 'p'
    logging.info("video is portrait")
doScale = False
if width > 1280 or height > 1280:
    doScale = True
    logging.info("scaling will be needed")

# split into audio and video
audiobitrate=totalbitrate/4
if audiobitrate > 128:
    audiobitrate = 128
logging.info(f"audio bitrate: {audiobitrate}kbps")
videobitrate=totalbitrate-audiobitrate
logging.info(f"video bitrate: {videobitrate}kbps")

if doScale:
    if orientation == 'p':
        scale = 1280 / height
        newres = str(round(width*scale))+":1280"
    else:
        scale = 1280 / width
        newres = "1280:"+str(round(height*scale))
    if verbose:
        ffmpeg_command = f"{expath}ffmpeg -i \"{filein}\" -vf scale={newres} -filter:v fps=30 -vcodec libx264 -b:v {videobitrate}k -b:a {audiobitrate}k output.mp4"
    else:
        ffmpeg_command = f"{expath}ffmpeg -hide_banner -loglevel error -nostats -i \"{filein}\" -vf scale={newres} -filter:v fps=30 -vcodec libx264 -b:v {videobitrate}k -b:a {audiobitrate}k output.mp4"
else:
    if verbose:
        ffmpeg_command = f"{expath}ffmpeg -i \"{filein}\" -filter:v fps=30 -vcodec libx264 -b:v {videobitrate}k -b:a {audiobitrate}k output.mp4"
    else:
        ffmpeg_command = f"{expath}ffmpeg -hide_banner -loglevel error -nostats -i \"{filein}\" -filter:v fps=30 -vcodec libx264 -b:v {videobitrate}k -b:a {audiobitrate}k output.mp4"
print("\nShrinking Video, this usually takes a while...")
logging.info("calling ffmpeg")
os.system()

# get the new file size
newsize=os.path.getsize("output.mp4")/1000
logging.info(f"size of output file: {newsize}")

# done!
complete()