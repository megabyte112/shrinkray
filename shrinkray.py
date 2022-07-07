# shrinkray, by megabyte112
# see LICENSE for license info
# https://github.com/megabyte112/shrinkray

import sys, os, subprocess, math, shutil, logging

version = "1.1"

suffix = "_shrinkray"
container = "mp4"
arg_length = len(sys.argv)

# maximum allowed resolution before scaling
max_res_size = 1280

# check folders
if not os.path.isdir("logs"):
    os.mkdir("logs")
if not os.path.isdir("output"):
    os.mkdir("output")
if not os.path.isdir("download"):
    os.mkdir("download")

# setup logger
if os.path.exists("logs/shrinkray.log"):
    os.remove("logs/shrinkray.log")
logformat='%(asctime)s: %(message)s'
logging.basicConfig(filename="logs/shrinkray.log", filemode="w", level=logging.INFO, format=logformat)

logging.info(f"shrinkray {version} is running")
logging.info("tell megabyte112 about any issues!!")

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
    nullfile="NUL"
else:   # posix
    logging.info("host is non-Windows")
    expath="bin/"
    nullfile="/dev/null"

# use the "bin" folder if it exists
# if not, assume everything is in PATH already
if not os.path.isdir("bin"):
    expath=""
    logging.info("using PATH")
else:
    logging.info("using bin folder")

print("shrinkray, version "+version)
print()

# download video if no arguments are given
bad_chars = [':','*','?','|','<','>']
if arg_length < 2:
    logging.info("prepare download...")
    if os.path.exists("input.mp4"):
        os.remove("input.mp4")
        logging.info("removed old input.mp4")
    fullurl=input("Paste a video link here.\nIt can be YouTube, Reddit, and most other video sites.\n> ")
    logging.info(f"input: \"{fullurl}\"")
    url=fullurl.split("&")[0]
    if url != fullurl:
        logging.info(f"shortened input to: \"{url}\"")
    logging.info("attempting download")
    print(f"\nDownloading video...")
    title = subprocess.getoutput(expath+"yt-dlp -e --no-playlist "+url)
    logging.info("title: "+title)
    filein = "download/"+title+"."+container
    if verbose:
        dlcommand = f"{expath}yt-dlp \"{url}\" -f mp4 --no-playlist -o \"{filein}\""
    else:
        dlcommand = f"{expath}yt-dlp \"{url}\" -q -f mp4 --no-playlist -o \"{filein}\""
    logging.info("running yt-dlp with the following command")
    logging.info(dlcommand)
    os.system(dlcommand)
    for char in bad_chars:
        filein = filein.replace(char,'#')
    print()
else:
    filein=sys.argv[1]
    logging.info("target file "+filein)

# figure out valid file name
fullname = filein.split("/")
fullname = fullname[len(fullname)-1].split("\\")
name = fullname[len(fullname)-1].split(".")
if len(name) == 1:
    fileout = "output/"+name+suffix+"."+container
else:
    newname=""
    for item in name:
        if item != container:
            newname += item
    fileout = "output/"+newname+suffix+"."+container

# text must be a number greater than 0
def CheckValidInput(text):
    return text.isnumeric() and int(text) > 0

# ask for target file size
target_size = ""
while not CheckValidInput(target_size):
    target_size = input("Target file size in MB\n> ")
    if not CheckValidInput(target_size):
        logging.warning("rejected input: "+str(target_size))
        print("\nMake sure your input a whole number greater than 0")

# 95% of target size seems to provide enough "wiggle room" for most videos
targetSizeKB = int(target_size) * 950
logging.info("target size: "+str(targetSizeKB)+"KB")

# calculate size: no need to shrink if video is already small enough
size=os.path.getsize(filein)/1000
logging.info(f"size of input file: {size}kB")
if size < targetSizeKB:
    shutil.copy(filein, fileout)
    logging.info("video is already small enough, copying to "+fileout)
    newsize=size
    print("\nThe video is already small enough!")
    logging.info("complete!")
    input("You can now close this window.")
    sys.exit()

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
width = int(splitres[0])
height = int(splitres[1])
if width > height:
    orientation = 'l'
    logging.info("video is landscape")
else:
    orientation = 'p'
    logging.info("video is portrait")
doScale = False
if width > max_res_size or height > max_res_size:
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
        scale = max_res_size / height
        newres = str(round(width*scale))+":"+str(max_res_size)
    else:
        scale = max_res_size / width
        newres = str(max_res_size)+":"+str(round(height*scale))
    if verbose:
        ffmpeg_commands = [f"{expath}ffmpeg -y -i \"{filein}\"  -vf scale={newres},fps=30 -c:v libx264 -b:v {videobitrate}k -passlogfile logs/fflog -pass 1 -f null {nullfile}",
        f"{expath}ffmpeg -y -i \"{filein}\" -vf scale={newres},fps=30 -c:v libx264 -b:v {videobitrate}k -passlogfile logs/fflog -c:a aac -b:a {audiobitrate}k -pass 2 \"{fileout}\""]
    else:
        ffmpeg_commands = [f"{expath}ffmpeg -y -hide_banner -loglevel error -nostats -i \"{filein}\" -vf scale={newres},fps=30 -c:v libx264 -b:v {videobitrate}k -passlogfile logs/fflog -pass 1 -f null {nullfile}",
        f"{expath}ffmpeg -y -hide_banner -loglevel error -nostats -i \"{filein}\" -vf scale={newres},fps=30 -c:v libx264 -b:v {videobitrate}k -passlogfile logs/fflog -c:a aac -b:a {audiobitrate}k -pass 2 \"{fileout}\""]
else:
    if verbose:
        ffmpeg_commands = [f"{expath}ffmpeg -y -i \"{filein}\" -vf fps=30 -c:v libx264 -b:v {videobitrate}k -passlogfile logs/fflog -pass 1 -f null {nullfile}",
        f"{expath}ffmpeg -y -i \"{filein}\" -vf fps=30 -c:v libx264 -b:v {videobitrate}k -passlogfile logs/fflog -c:a aac -b:a {audiobitrate}k -pass 2 \"{fileout}\""]
    else:
        ffmpeg_commands = [f"{expath}ffmpeg -y -hide_banner -loglevel error -nostats -i \"{filein}\" -vf fps=30 -c:v libx264 -b:v {videobitrate}k -passlogfile logs/fflog -pass 1 -f null {nullfile}",
        f"{expath}ffmpeg -y -hide_banner -loglevel error -nostats -i \"{filein}\" -vf fps=30 -c:v libx264 -b:v {videobitrate}k -passlogfile logs/fflog -c:a aac -b:a {audiobitrate}k -pass 2 \"{fileout}\""]

print("\nShrinking Video using two-pass, this can take a while.")
logging.info("calling ffmpeg for two-pass, will now log commands")
logging.info(ffmpeg_commands[0])
print("Running pass 1...")
os.system(ffmpeg_commands[0])
logging.info(ffmpeg_commands[1])
print("Running pass 2...")
os.system(ffmpeg_commands[1])
logging.info("called both commands")

# get the new file size
newsize=os.path.getsize(fileout)/1000
logging.info(f"size of output file: {newsize}")

# done!
print("\nShrinking complete!\nCheck the output folder for your video.")
displaysize=round((size/8192)*8000)
newdisplaysize=round((newsize/8192)*8000)
expected = (targetSizeKB/1000)*1024
print(f"\nCompressed {displaysize}kB into {newdisplaysize}kB\n")
if newdisplaysize > expected:
    logging.info("file is larger than expected!")
    print("It looks like shrinkray couldn't shrink your video as much as expected.")
    print("If you need it to be smaller, try running shrinkray again and lowering the target size.")
logging.info("complete!")
input("You can now close this window.")
sys.exit()
