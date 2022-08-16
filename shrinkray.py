# shrinkray, by megabyte112
# see LICENSE for license info
# https://github.com/megabyte112/shrinkray


### ----------[~~Settings~~]---------- ###

# Here you can find advanced settings for shrinkray.
# Lines prefixed with a hash (#) are comments and are ignored by code.
# All booleans (True/False) must have the first letter capitalized.

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

# ask user whether audioonly shall be used each launch.
# this is useless when audioonly is already True.
# user is always asked this if using a local file.
# default: False
ask_audio = False

# ask user for target file size each launch.
# default: False
ask_size = False

# default target file size in MB.
# default: 8
default_size = 8

# shrinking speed, a number between 1 and 10, higher is faster.
# lower speeds lead to more accurate file sizes.
# default: 8
speed = 8

## -----[Video]----- ##

# maximum allowed size of longest edge (in pixels) before scaling is needed.
# default: 1280
max_res_size = 1280

# highest allowed audio bitrate (in kbps).
# ignored when audioonly is True.
# set to None to disable.
# default: 256
max_audio_bitrate = 256

# framerate limit.
# default: 30
target_fps = 30

# container to contain video files.
# default: "mp4"
container = "mp4"

# video codec to use.
# default: "libx264"
video_codec = "libx264"

## -----[Audio]----- ##

# don't include audio. 
# doesn't work when audioonly is True.
# default: False
mute = False

# fraction of bandwith dedicated to audio.
# ignored when mute or audioonly is True.
# must be less than 1.
# default: 1/4
audioratio = 1/4

# don't include video, and store file in audio container.
# default: False
audioonly = False

# container to store audio when audioonly is True.
# default: "mp3"
audiocontainer = "mp3"

# audio codec to use.
# default: "libmp3lame"
audio_codec = "libmp3lame"

## ------[Fun]------ ##

# ultra high compression for those moldy shitposts.
# locks video bitrate to 20kbps, and audio bitrate to 10kbps.
# resolution is also smaller and FPS is capped at 10.
# default: False
meme_mode = False

### -------[~~End of Settings~~]------- ###

# Everything below this point is actual code.
# Only edit if you know exactly what you're doing.



# okay, let's do this.
import sys, os, subprocess, math, shutil, logging

# check dependencies
try:
    import ffpb, yt_dlp
except ImportError:
    print("Installing deps...\n")
    import pip
    pip.main(["install","ffpb","yt-dlp","--exists-action","i"])
    import ffpb
    print()
    print("Dependency Installation complete!")
    input("You now need to close and reopen shrinkray.")
    sys.exit()

# check for ffmpeg
if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
    print("It seems like FFMPEG isn't installed, or isn't in your system path.")
    print("Refer to shrinkray's guide for more info.")
    print("https://github.com/megabyte112/shrinkray/wiki/shrinkray-wiki")
    print()
    input("When you're done, reopen shrinkray, and you're all set.")
    sys.exit()

# don't edit
version = "1.3"

speeds = ["placebo", "veryslow", "slower", "slow", "medium", "fast", "faster", "veryfast", "superfast", "ultrafast"]
preset = " -preset "+speeds[speed-1]

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

if verbose:
    logging.getLogger().addHandler(logging.StreamHandler())

logging.info(f"shrinkray {version} is running")
logging.info("tell megabyte112 about any issues!!")
logging.info("args: " + str(sys.argv))
logging.info("mute: "+str(mute))
logging.info("audioonly: "+str(audioonly))
logging.info("audioratio: "+str(audioratio))
logging.info("bitrate_multiplier: "+str(bitrate_multiplier))
logging.info("meme mode: "+str(meme_mode))

# determine host OS
if os.name == "nt": # windows
    logging.info("host is Windows")
    nullfile="NUL"
else:   # posix
    logging.info("host is non-Windows")
    nullfile="/dev/null"

# we're running!!
print(f"Welcome back to shrinkray, version {version}")

if meme_mode:
    ask_size = False
    ask_audio = False
    print("\nhaha shitpost shrinkray go brrrrrrrrr")
    print("(meme mode is active)")
elif audioonly:
    print("\nWARNING: Output will be audio only!")
elif mute:
    print("\nWARNING: Video will be muted!")

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

def GetAudioChoice():
    return input("\nGet audio only? [Y/N]\n> ").lower() == "y"

# download video if no arguments are given
bad_chars = [':','*','?','|','<','>']
if arg_length < 2:
    logging.info("prepare download...")
    url=input("\nPaste a video link here.\nIt can be YouTube, Reddit, and most other video sites.\n> ")
    logging.info(f"input: \"{url}\"")
    if ask_size:
        target_size = GetTargetSize()
    else:
        target_size = default_size
    if ask_audio:
        audioonly = GetAudioChoice()
        logging.info("audioonly: "+str(audioonly))
    print("\nFetching video...")
    titlecmd = "yt-dlp -e --no-playlist "+url
    logging.info("fetching title with the following command")
    logging.info(titlecmd)
    p = subprocess.getstatusoutput(titlecmd)
    if p[0] != 0:
        logging.info("title grab failed with return code "+str(p[0]))
        print("There was an issue with your video URL.\nPress [Enter] or close this window and run shrinkray again.")
        logging.shutdown()
        input("Be sure to check whether your URL is correct!")
        sys.exit()
    title = p[1].replace("\"","'")
    getfilenamecmd = f"yt-dlp \"{url}\" --get-filename --no-playlist -o \"download/{title}.%(ext)s\""
    logging.info("fetching filename with the following command")
    logging.info(getfilenamecmd)
    filein = subprocess.getoutput(getfilenamecmd)
    logging.info("filename: "+filein)
    logging.info("title: "+str(title))
    url=url.replace("\"","\\\"")
    if verbose:
        dlcommand = f"yt-dlp \"{url}\" -v --no-playlist -o \"{filein}\""
    else:
        dlcommand = f"yt-dlp \"{url}\" --quiet --progress  --no-playlist -o \"{filein}\""
    print("Downloading video...")
    logging.info("downloading video with the following command")
    logging.info(dlcommand)
    os.system(dlcommand)
    for char in bad_chars:
        if os.name == "nt":
            filein = filein.replace(char,'#')
        else:
            filein = filein.replace(char,'?')
else:
    filein=sys.argv[1]
    logging.info("target file "+filein)
    if ask_size:
        target_size = GetTargetSize()
    else:
        target_size = default_size
    if not meme_mode:
        audioonly = GetAudioChoice()

if audioonly:
    container = audiocontainer
    preset = ""

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
if size < targetSizeKB and not meme_mode:
    if mute:
        print("\nRemoving Audio...")
        os.system(f"ffpb -y -i \"{filein}\" -an \"{fileout}\"")
    else:
        shutil.copy(filein, fileout)
    logging.info("file is already small enough")
    newsize=size
    print("\nThe file is already small enough!")
    print("It has been copied to the output folder.")
    logging.info("complete!")
    logging.shutdown()
    input("You can now press [Enter] or close this window to exit.")
    sys.exit()

# bitrate (in Mbps) = Size / Length
# divide target size by length in seconds
lencmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{filein}\""
logging.info("fetching length with the following command")
logging.info(lencmd)
length = math.ceil(float(subprocess.getoutput(lencmd)))
logging.info(f"video length: {length}s")
totalbitrate=math.floor(targetSizeKB*8/length)

# get fps
if not audioonly:
    if meme_mode:
        target_fps = 10
    fpscmd = f"ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate \"{filein}\""
    logging.info("fetching framerate with the following command")
    logging.info(fpscmd)
    fullfps = subprocess.getoutput(fpscmd).split("/")
    fps = float(int(fullfps[0])/int(fullfps[1]))
    logging.info(f"video is {fps}fps")
    lowerfps = fps > target_fps

# get resolution
doScale = False
if not audioonly:
    if meme_mode:
        max_res_size = 640
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

# ahh yes, crusty shitposts
if meme_mode:
    audiobitrate = 10
    videobitrate = 20
    totalbitrate = audiobitrate + videobitrate

logging.info(f"audio bitrate: {audiobitrate}kbps")
logging.info(f"video bitrate: {videobitrate}kbps")
logging.info(f"total bitrate: {totalbitrate}kbps")

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
        if lowerfps:
            fpsargs = ",fps="+str(target_fps)
        else:
            fpsargs = ""
        if orientation == 'p':
            scale = max_res_size / height
            newres = str(round((width*scale)/2)*2)+":"+str(max_res_size)
        else:
            scale = max_res_size / width
            newres = str(max_res_size)+":"+str(round((height*scale)/2)*2)
        videoargs = f"-vf scale={newres}{fpsargs} -c:v {video_codec} -b:v {videobitrate}k"
        if audioonly:
            videoargs = ""
        if verbose:
            ffmpeg_commands = [f"ffpb -y -i \"{filein}\" {videoargs} {preset} -passlogfile logs/fflog -pass 1 -f null {nullfile}",
            f"ffpb -y -i \"{filein}\" {videoargs} {preset} -passlogfile logs/fflog {audioargs} -pass 2 \"{fileout}\""]
        else:
            ffmpeg_commands = [f"ffpb -y -hide_banner -i \"{filein}\" {videoargs} {preset} -passlogfile logs/fflog -pass 1 -f null {nullfile}",
            f"ffpb -y -hide_banner -i \"{filein}\" {videoargs} {preset} -passlogfile logs/fflog {audioargs} -pass 2 \"{fileout}\""]
    else:
        if lowerfps:
            fpsargs = "-vf fps="+str(target_fps)
        else:
            fpsargs = ""
        videoargs = f"{fpsargs} -c:v {video_codec} -b:v {videobitrate}k"
        if verbose:
            ffmpeg_commands = [f"ffpb -y -i \"{filein}\" {videoargs} {preset} -passlogfile logs/fflog -pass 1 -f null {nullfile}",
            f"ffpb -y -i \"{filein}\" {videoargs} {preset} -passlogfile logs/fflog {audioargs} -pass 2 \"{fileout}\""]
        else:
            ffmpeg_commands = [f"ffpb -y -hide_banner -i \"{filein}\" {videoargs} {preset} -passlogfile logs/fflog -pass 1 -f null {nullfile}",
            f"ffpb -y -hide_banner -i \"{filein}\" {videoargs} {preset} -passlogfile logs/fflog {audioargs} -pass 2 \"{fileout}\""]

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
    print("It looks like shrinkray couldn't shrink your file as much as you requested.")
    print("If you need it to be smaller, try lowering the target size and running shrinkray again.")
    print("The file was still saved.")
logging.info("complete!")
logging.shutdown()
input("You can now press [Enter] or close this window to exit.")
sys.exit()
