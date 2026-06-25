import sys
import os
import zlib
import hashlib

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)
    
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")

    elif command == 'cat-file':
        shahash = sys.argv[3] # getting the hash from the command

        path = os.path.join('.git', "objects", shahash[:2], shahash[2:]) # constructing the git file path

        with open(path, 'rb') as f: # reading the raw bytes from the file into a variable
            content = f.read()

        content = zlib.decompress(content) # decopressing the file to give us: b"blob 11\x00hello world"

        content = content.split(b"\x00")[1].decode() # splitting by the bull bytes seprator, then deocding it to give us the text

        print(content, end="") # by default print() adds a \n at the end
    
    elif command == 'hash-object':
        filename = sys.argv[3] # get the filename | git hash-object -w file.txt

        with open(filename, 'rb') as f: # read the content of the file
            content = f.read()
        
        header = f"blob {len(content)}\0" # constructing the blob header

        blob_object = header.encode() + content # combining the header and the content | blob <size>\0<content>

        shahash_object = hashlib.sha1(blob_object) # constructs the hash object with the blob

        shahash = shahash_object.hexdigest() # extracts the result as a 40 char hash

        compressed_blob = zlib.compress(blob_object) # compressing the blob into bytes

        path = os.path.join('.git', "objects", shahash[:2], shahash[2:]) # the path we need

        dir_path = os.path.join('.git', 'objects', shahash[:2]) # create the folder path only

        if not os.path.exists(dir_path): # check if the dir exists
            os.mkdir(dir_path) # create the full path

        with open(path, 'wb') as f: # write the blob to the file
            f.write(compressed_blob)

        print(shahash)


    elif command == 'ls-tree':
        shahash = sys.argv[3]

        path = os.path.join('.git', 'objects', shahash[:2], shahash[2:])

        with open(path, 'rb') as f:
            content = f.read()

        content = zlib.decompress(content)

        content = content.split(b"\x00", 1)[1] # strip the tree header | tree 123\x00100644 file.txt\x00<20 bytes>100644 readme.md\x00<20 bytes>

        entries = []

        while content:
            null_index = content.index(b"\x00")

            mode_and_filename = content[:null_index]

            filename = mode_and_filename.split(b" ", 1)[1].decode()

            content = content[null_index + 1:] # move to the sha which is after the null_index

            sha = content[:20] # the sha is 20 bytes

            content = content[20:] # get to the next mode and filename

            entries.append(filename)

        for entry in entries:
            print(entry)


    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()

