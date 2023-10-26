import os
import sys
import json
import time

stage = "start"

written_lines = 0
def log(s):
    global written_lines
    written_lines += len(s.split("\n"))
    print(s)
    
def inp(s):
    global written_lines
    written_lines += len(s.split("\n"))
    return input(s)

def delete_last_line(count=True):
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')
    if count:
        global written_lines
        written_lines -= 1

def write_line(s, delay=.03):
    length = len(s)
    if length > 0:
        for i in range(length):
            if i != 0:
                delete_last_line()
            log(s[:i + 1])
            time.sleep(delay)

def check_folder_exists(path):
    exists = os.path.isdir(path)
    log(f"{'✅' if exists else '❌'} Checking path {path}")
    return exists, path

def main():
    global stage, written_lines
    stage = "retreive assets folder"
    
    assetsFolder = os.path.normpath(os.path.expandvars(inp("📁 Path to assets folder (ex. %appdata%/.minecraft/assets): "))).replace("\\", "/")
    if not os.path.isdir(assetsFolder):
        log("❌ Path must be an existing folder")
        return
    
    stage = "check indexes folder"
    indexesExist, indexesFolder = check_folder_exists(assetsFolder + "/indexes")
    if not indexesExist:
        log("❌ Indexes folder not found!")
        return

    stage = "check objects folder"
    objectsExist, objectsFolder = check_folder_exists(assetsFolder + "/objects")
    if not objectsExist:
        log("❌ Objects folder not found!")
        return
    
    stage = "retreive version"
    versionFile: str
    while True:
        options = []
        for file in os.listdir(indexesFolder):
            if file.endswith(".json"):
                options.append(file[:-5])
        
        log(f"📀 Available options: {', '.join(options)}")
        version = inp("📀 Please enter a version: ").replace("\\", "/").replace("/", "")
        versionFile = indexesFolder + f"/{version}.json"
        
        if not os.path.isfile(versionFile):
            log(f"❌ Version 1.{version} not found. Press Ctl+C to cancel")
        else:
            break
    
    stage = "load index -> read"
    content: str
    with open(versionFile, "r") as f:
        content = f.read()
    
    stage = "retreive export folder"
    exportFolder = os.path.normpath(os.path.expandvars(inp("📁 Path to export folder (ex. C:/exported_assets/): "))).replace("\\", "/")
    if not os.path.isdir(exportFolder):
        log("❌ Path must be an existing folder")
        return
    if os.listdir(exportFolder):
        log("❌ Folder is not empty! Please choose a different folder")
        return
    
    stage = "load index -> load json"
    index = json.loads(content)
    
    stage = "load index -> get objects"
    exported = 0
    doCopy = {}

    objectIndexes = index["objects"]

    for k in objectIndexes:
        stage = f"load index -> loop through object [{k}]"
        iHash = objectIndexes[k]["hash"]
        hashPath = f"{iHash[:2]}/{iHash}"
        path = f"{objectsFolder}/{hashPath}"
        if os.path.isfile(path):
            stage = f"load index -> loop through object [{k}] -> add file to copy"
            doCopy[path] = f"{exportFolder}/{k}"

    toCopy = len(doCopy)
    for k in doCopy:
        stage = "copy file"
        v = doCopy[k]

        stage = "copy file -> create dirs"
        os.makedirs(os.path.dirname(v), exist_ok=True)

        stage = "copy file -> copy file -> open read"
        with open(k, "rb") as f:
            stage = "copy file -> copy file -> open write"
            with open(v, "wb") as f2:
                stage = "copy file -> copy file -> write & read"
                f2.write(f.read())

        stage = "copy file -> stats"
        if exported > 0:
            delete_last_line()
        exported += 1
        log(f"⏳ {toCopy - exported} files left to export...")


    stage = "finish anim - delete lines"
    for i in range(written_lines):
        time.sleep(.05)
        delete_last_line(False)

    stage = "finish anim - write finish text"
    time.sleep(.1)
    
    write_line(f"✅ Exported {exported} file/s!")
    write_line(f"     Assets folder: {assetsFolder}", 0.01)
    write_line(f"     Version file: {versionFile}", 0.01)
    write_line(f"     Exported files: {exportFolder}", 0.01)
    write_line(f"❤ Thanks for using the tool! ~pierrelasse")

    stage = "done"
    
if __name__ == "__main__":
    try:
        stage = "start main"
        main()
    except KeyboardInterrupt:
        log(f"\n🛑 Exiting (stage: {stage})")
        exit()
    except Exception as ex:
        log("❌ Fatal error (stage: {}): {}".format(stage, ex))
