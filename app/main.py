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
        filename = sys.argv[3]

        with open(filename, 'rb') as f:
            content = f.read()
        
        header = f"blob {len(content)}\0" # constructing the blob header

        blob_object = header.encode() + content # combining the header and the content

        shahash_object = hashlib.sha1(blob_object) # constructs the hash object with the data

        shahash = shahash_object.hexdigest() # extracts the result as a 40 char hash

        compressed_blob = zlib.compress(blob_object) # compressing the blob

        path = os.path.join('.git', "objects", shahash[:2], shahash[2:])

        dir_path = os.path.join('.git', 'objects', shahash[:2]) # create the folder path only

        if not os.path.exists(dir_path): # check if the dir exists
            os.mkdir(path) # create the full path

        with open(path, 'wb') as f: # write the blob to the file
            f.write(compressed_blob)

        print(shahash)


    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()

