# shrinkray, by megabyte112
# see LICENSE for license info


import sys, os, subprocess, math, shutil, logging

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
logformat='[%(asctime)s] %(levelname)s: %(message)s'
logging.basicConfig(filename="shrinkray.log", filemode="w", level=logging.INFO, format=logformat)

logging.info("initialising...")

# use the "bin" folder if it exists
# if not, assume everything is in PATH already
if os.path.isdir("bin"):
    if os.name == "nt": # windows
        logging.info("host is Windows")
        expath="bin\\"
    else:   # posix
        logging.info("host is non-Windows")
        expath="/bin"
    logging.info("using bin folder")
else:
    expath=""
    logging.info("using PATH")

# remove older output
if os.path.exists("output.mp4"):
    os.remove("output.mp4")
    logging.info("removed old output.mp4")

# download video if no arguments are given
if len(sys.argv) < 2:
    logging.info("prepare download...")
    if os.path.exists("input.mp4"):
        os.remove("input.mp4")
        logging.info("removed old input.mp4")
    print("Paste a video link here.\nIt can be YouTube, Reddit, and most other video sites.\n")
    fullurl=input("> ")
    logging.info(f"input: \"{fullurl}\"")
    url=fullurl.split("?")[0]
    if url != fullurl:
        logging.info(f"shortened input to: \"{url}\"")
    logging.info("downloading video...")
    print(f"\nDownloading video {url}...")
    os.system(f"{expath}yt-dlp \"{url}\" -q -f mp4 -o input.mp4")
    print("Finished downloading!")
    logging.info("download complete")
    filein="input.mp4"
else:
    filein=sys.argv[1]
    logging.info(f"using file {filein}")
    print("Target:", filein)

# calculate size: no need to shrink if video is already small enough
size=os.path.getsize(filein)/1000
logging.info(f"size of input file: {size}kB")
if size < 8000:
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
totalbitrate=math.floor(64000/length)
logging.info(f"total bitrate: {totalbitrate}kbps")

# split into audio and video
audiobitrate=totalbitrate/4
logging.info(f"audio bitrate: {audiobitrate}kbps")
videobitrate=totalbitrate*(3/4)
logging.info(f"video bitrate: {videobitrate}kbps")

# recode with ffmpeg
logging.info("recoding video...")
print("\nShrinking Video, this usually takes a while...")
os.system(f"{expath}ffmpeg -hide_banner -loglevel error -nostats -i \"{filein}\" -filter:v fps=30 -vcodec libx264 -b:v {videobitrate}k -b:a {audiobitrate}k output.mp4")
print("Done!")
logging.info("recoding complete")

# get the new file size
newsize=os.path.getsize("output.mp4")/1000
logging.info(f"size of output file: {newsize}")

# done!
complete()