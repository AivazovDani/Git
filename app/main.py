import sys
import os
import zlib
import hashlib



def write_tree(path):

    entries = [] # storing each file and dir entry individually in the format | <mode> <name>\x00<20 binary bytes SHA>

    for item in sorted(os.listdir(path)): # sorting alphabetically each directory in the current path | "." => pyhton/git/codecrafters

        if item == ".git": # ignore git's internal directory and track only my actual project files
            continue

        full_path = os.path.join(path, item) # pyhton/git/codecrafters/file.txt / pyhton/git/codecrafters/src

        if os.path.isfile(full_path): # if the full path is file

            with open(full_path, 'rb') as f:
                content = f.read() # read the content into byte object

                header = f"blob {len(content)}\0" # create the blob header

                blob_object = header.encode() + content # create the blob byte object
                
                shahash_object = hashlib.sha1(blob_object) # create the sha hash the blob object

                shahash = shahash_object.digest() # make it 20 bytes | summerizing

                entry = f"100644 {item}\x00".encode() + shahash # create the tree object | <mode> <name>\x00<20 binary bytes SHA>


                entries.append(entry)

        elif os.path.isdir(full_path): # if the full path is a subdirectory (directory in a directory)
            sub_sha = write_tree(full_path) # calling the subdirecotry recursivly so i can get the hash for the child tree before writing the parent tree to the storage
            entry = f"40000 {item}\x00".encode() + bytes.fromhex(sub_sha)
            entries.append(entry)

    tree_data = b"".join(entries) # combines all the tree data from my list into bytes | bytes only

    header = f'tree {len(tree_data)}\x00'.encode() # creates the tree header with the lenght of the tree data | bytes only
    
    full_tree = header + tree_data # creating the full tree structure

    h = hashlib.sha1(full_tree) # hashing the full tree
    sha_hash = h.hexdigest() # summerizing the full tree into 40 bytes

    path = os.path.join('.git', "objects", sha_hash[:2], sha_hash[2:]) # creating the path for my git object directory storage

    dir_path = os.path.join('.git', 'objects', sha_hash[:2]) # creating the folder for the git object directory storage

    if not os.path.exists(dir_path): # checking if the folder exists
        os.mkdir(dir_path)

    with open(path, 'wb') as f: # writing the tree to the storage
        f.write(zlib.compress(full_tree))


    return sha_hash

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
            null_index = content.index(b"\x00") # getting the null index which is equal to one byte

            mode_and_filename = content[:null_index]

            filename = mode_and_filename.split(b" ", 1)[1].decode() # getting the filename as text

            content = content[null_index + 1:] # move to the sha which is after the null_index

            sha = content[:20] # the sha is 20 bytes

            content = content[20:] # get to the next mode and filename

            entries.append(filename)

        for entry in entries:
            print(entry)


    elif command == 'write-tree':
        sha = write_tree(".")
        print(sha)

    elif command == 'commit-tree':
        content = f"tree {sys.argv[2]}\n"

        if sys.argv[3] == '-p':
            content += f"parent {sys.argv[4]}\n"
            content += f"author John Doe <john@example.com> 1234567890 +0000\n"
            content += f"committer John Doe <john@example.com> 1234567890 +0000\n"
            content += f"\n"
            content += sys.argv[6]

        else:
            content += f"author John Doe <john@example.com> 1234567890 +0000\n"
            content += f"committer John Doe <john@example.com> 1234567890 +0000\n"
            content += f"\n"
            content += sys.argv[4]
        

        byte_content = content.encode()

        header = f"commit {len(byte_content)}\x00".encode()

        full_commit = header + byte_content

        shahash_object = hashlib.sha1(full_commit)

        shahash = shahash_object.hexdigest()

        path = os.path.join('.git', 'objects', shahash[:2], shahash[2:])

        dir_path = os.path.join('.git', 'objects', shahash[:2])

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        with open(path, 'wb') as f:
            f.write(zlib.compress(full_commit))

        print(shahash)


    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()

