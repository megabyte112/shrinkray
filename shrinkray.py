# shrinkray, by megabyte112
# see LICENSE for license info
# https://github.com/megabyte112/shrinkray


### ----------[~~Settings~~]---------- ###

# Here you can find advanced settings for shrinkray.
# Lines prefixed with a hash (#) are comments and are ignored by code.

## -----[Video]----- ##

# maximum allowed size of longest edge (in pixels) before scaling is needed.
# default: 1280
max_res_size = 1280

# highest allowed audio bitrate (in kbps).
# ignored when audioonly is True
# set to None to disable.
# default: 256
max_audio_bitrate = 256

# container to contain video files.
# default: "mp4"
container = "mp4"

# video codec to use
# default: "libx264"
video_codec = "libx264"

## -----[Audio]----- ##

# don't include audio. 
# doesn't work when audioonly is True
# default: False
mute = False

# fraction of bandwith dedicated to audio.
# ignored when mute or audioonly is True
# must be less than 1.
# default: 1/4
audioratio = 1/4

# don't include video, and store file in audio container.
# default: False
audioonly = False

# container to store audio when audioonly is True.
# default: "mp3"
audiocontainer = "mp3"

# audio codec to use
# default: "libmp3lame"
audio_codec = "libmp3lame"

## ----[General]---- ##

# enable verbose mode.
# default: False
verbose = False

# string appended to filenames.
# default: "_shrinkray"
suffix = "_shrinkray"

# amount of 'wiggle room': higher means more chance of file being too big.
# always keep this less than 1, or else your files will be too large.
# default: 0.95
bitrate_multiplier = 0.95

### ---------------------------------- ###


# okay, let's do this.
import sys, os, subprocess, math, shutil, logging

# check dependencies
try:
    import ffpb
except ImportError:
    print("Hi, Welcome to shrinkray!")
    print("This may be your first time here, since you have missing dependencies.")
    print("shrinkray can automatically install dependencies for you using pip.")
    print("You may see warning messages during pip installs, these are generally safe.\n")
    input("Press enter to install the missing dependencies.")
    print("Installing...\n")
    import pip
    pip.main(["install","ffpb","--quiet","--exists-action","i"])
    import ffpb
    print()
    print("Installation complete!")
    input("You now need to close and reopen shrinkray.")
    sys.exit()

# check for ffmpeg
if shutil.which("ffmpeg") is None or shutil.which("yt-dlp") is None or shutil.which("ffprobe") is None:
    print("It seems like FFMPEG isn't installed, or isn't in your system path.")
    print("Download FFMPEG here: https://ffmpeg.org/download.html")
    print()
    print("Installing FFMPEG can be more complex than other apps,")
    print("but a quick web search and you should be good.")
    print()
    print("You also need to download yt-dlp and add it to FFMPEG's 'bin' folder.")
    print("Download yt-dlp here: https://github.com/yt-dlp/yt-dlp/releases")
    print()
    print("Make sure to add the folder to path!")
    input()
    sys.exit()

# don't edit
version = "1.2"

arg_length = len(sys.argv)

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
logging.info("args: " + str(sys.argv))
logging.info("mute: "+str(mute))
logging.info("audioonly: "+str(audioonly))
logging.info("audioratio: "+str(audioratio))
logging.info("bitrate_multiplier: "+str(bitrate_multiplier))

# determine host OS
if os.name == "nt": # windows
    logging.info("host is Windows")
    nullfile="NUL"
else:   # posix
    logging.info("host is non-Windows")
    nullfile="/dev/null"

if mute:
    print("WARNING: Video will be muted!")
if audioonly:
    print("WARNING: Output will be audio only!")

print("Welcome back to shrinkray, version "+version)

# text must be a number greater than 0
def CheckValidInput(text):
    return text.isnumeric() and int(text) > 0

# ask for target file size
def GetTargetSize():
    target_size = ""
    while not CheckValidInput(target_size):
        target_size = input("\nTarget file size in MB\n> ")
        if not CheckValidInput(target_size):
            logging.warning("rejected input: "+str(target_size))
            print("\nMake sure your input a whole number greater than 0")
    return target_size

# yt-dlp will get this
dlcontain = "mp4"

# download video if no arguments are given
bad_chars = [':','*','?','|','<','>']
if arg_length < 2:
    logging.info("prepare download...")
    url=input("\nPaste a video link here.\nIt can be YouTube, Reddit, and most other video sites.\n> ")
    logging.info(f"input: \"{url}\"")
    target_size = GetTargetSize()
    print("\nFetching video...")
    titlecmd = "yt-dlp -e --no-playlist "+url
    logging.info("fetching title with the following command")
    logging.info(titlecmd)
    p = subprocess.getstatusoutput(titlecmd)
    if p[0] != 0:
        logging.info("title grab failed with return code "+str(p[0]))
        print("There was an issue with your video URL.\nClose this window and run shrinkray again.")
        print("Be sure to check whether your URL is correct!")
        input()
        sys.exit()
    title = p[1]
    filein = "download/"+str(title)+"."+dlcontain
    logging.info("title: "+str(title))
    url=url.replace("\"","\\\"")
    dltype = "-f "+dlcontain
    if verbose:
        dlcommand = f"yt-dlp \"{url}\" -v {dltype} --no-playlist -o \"{filein}\""
    else:
        dlcommand = f"yt-dlp \"{url}\" --quiet --progress {dltype} --no-playlist -o \"{filein}\""
    print("Downloading video...")
    logging.info("downloading video with the following command")
    logging.info(dlcommand)
    os.system(dlcommand)
    for char in bad_chars:
        filein = filein.replace(char,'#')
else:
    filein=sys.argv[1]
    logging.info("target file "+filein)
    target_size = GetTargetSize()

if audioonly:
    container = audiocontainer

# convert to correct format
splitfilein = filein.split(".")
fileincontain = splitfilein[len(splitfilein)-1]
filenocontain = filein[0:len(filein)-len(fileincontain)-1]
if fileincontain != container:
    logging.info("converting file to "+container+" with the following command")
    print("\nConverting...")
    convertcommand = f"ffpb -y -i \"{filein}\" \"{filenocontain}.{container}\""
    logging.info(convertcommand)
    os.system(convertcommand)
    filein = filenocontain+"."+container


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

targetSizeKB = int(target_size) * 1000 * bitrate_multiplier
logging.info("target size: "+str(targetSizeKB)+"KB")

# calculate size: no need to shrink if file is already small enough
size=os.path.getsize(filein)/1024   # in kiB
logging.info(f"size of input file: {size}kiB")
if size < targetSizeKB:
    logging.info("file is already small enough")
    newsize=size
    print("\nThe file is already small enough!")
    shutil.copy(filein, fileout)
    print("It has been copied to the output folder.")
    logging.info("complete!")
    input("You can now close this window.")
    sys.exit()

# bitrate (in Mbps) = Size / Length
# divide target size by length in seconds
lencmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{filein}\""
logging.info("fetching length with the following command")
logging.info(lencmd)
length = math.ceil(float(subprocess.getoutput(lencmd)))
logging.info(f"video length: {length}s")
totalbitrate=math.floor(targetSizeKB*8/length)
logging.info(f"total bitrate: {totalbitrate}kbps")

# get resolution
doScale = False
if not audioonly:
    rescmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 \"{filein}\""
    logging.info("fetching resolution with the following command")
    logging.info(rescmd)
    fullresolution = subprocess.getoutput(rescmd)
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
    if width > max_res_size or height > max_res_size:
        doScale = True
        logging.info("scaling will be needed")

# split into audio and video
if audioonly:
    videobitrate = 0
    audiobitrate = totalbitrate
elif mute:
    audiobitrate = 0
    videobitrate = totalbitrate
else:
    audiobitrate=totalbitrate * audioratio
    if max_audio_bitrate is not None and audiobitrate > max_audio_bitrate:
        audiobitrate = max_audio_bitrate
    videobitrate=totalbitrate-audiobitrate
logging.info(f"audio bitrate: {audiobitrate}kbps")
logging.info(f"video bitrate: {videobitrate}kbps")

audioargs = f"-c:a {audio_codec} -b:a {audiobitrate}k"
if mute:
    audioargs = "-an"

if audioonly:
    if verbose:
        ffmpegcmd = f"ffpb -y -i \"{filein}\" {audioargs} \"{fileout}\""
    else:
        ffmpegcmd = f"ffpb -y -hide_banner -i \"{filein}\" {audioargs} \"{fileout}\""
    print("\nShrinking, this can take a while...\n")
    logging.info("audio shrinking using the following command")
    logging.info(ffmpegcmd)
    os.system(ffmpegcmd)
    logging.info("called command")

else:
    if doScale:
        if orientation == 'p':
            scale = max_res_size / height
            newres = str(round(width*scale))+":"+str(max_res_size)
        else:
            scale = max_res_size / width
            newres = str(max_res_size)+":"+str(round(height*scale))
        videoargs = f"-vf scale={newres},fps=30 -c:v {video_codec} -b:v {videobitrate}k"
        if audioonly:
            videoargs = ""
        if verbose:
            ffmpeg_commands = [f"ffpb -y -i \"{filein}\" {videoargs} -passlogfile logs/fflog -pass 1 -f null {nullfile}",
            f"ffpb -y -i \"{filein}\" {videoargs} -passlogfile logs/fflog {audioargs} -pass 2 \"{fileout}\""]
        else:
            ffmpeg_commands = [f"ffpb -y -hide_banner -i \"{filein}\" {videoargs} -passlogfile logs/fflog -pass 1 -f null {nullfile}",
            f"ffpb -y -hide_banner -i \"{filein}\" {videoargs} -passlogfile logs/fflog {audioargs} -pass 2 \"{fileout}\""]
    else:
        videoargs = f"-vf fps=30 -c:v {video_codec} -b:v {videobitrate}k"
        if verbose:
            ffmpeg_commands = [f"ffpb -y -i \"{filein}\" {videoargs} -passlogfile logs/fflog -pass 1 -f null {nullfile}",
            f"ffpb -y -i \"{filein}\" {videoargs} -passlogfile logs/fflog {audioargs} -pass 2 \"{fileout}\""]
        else:
            ffmpeg_commands = [f"ffpb -y -hide_banner -i \"{filein}\" {videoargs} -passlogfile logs/fflog -pass 1 -f null {nullfile}",
            f"ffpb -y -hide_banner -i \"{filein}\" {videoargs} -passlogfile logs/fflog {audioargs} -pass 2 \"{fileout}\""]

    print("\nShrinking using two-pass, this can take a while.\n")
    logging.info("calling ffmpeg for two-pass, will now log commands")
    logging.info(ffmpeg_commands[0])
    print("Running pass 1...")
    os.system(ffmpeg_commands[0])
    logging.info(ffmpeg_commands[1])
    print("Running pass 2...")
    os.system(ffmpeg_commands[1])
    logging.info("called both commands")


# done!
print("\nShrinking complete!\nCheck the output folder for your file.")
newsize=os.path.getsize(fileout)/1000
displaysize=round((size/8192)*8000)
newdisplaysize=round((newsize/8192)*8000)
logging.info(f"size of output file: {newdisplaysize}")
expected = (targetSizeKB/1000)*1024
print(f"\nCompressed {displaysize}kB into {newdisplaysize}kB\n")
if newdisplaysize > expected:
    logging.info("file is larger than expected!")
    print("It looks like shrinkray couldn't shrink your file as much as expected.")
    print("If you need it to be smaller, try running shrinkray again and lowering the target size.")
logging.info("complete!")
input("You can now close this window.")
sys.exit()
