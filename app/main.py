import sys
import os
import zlib

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

        print(content)

        

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()

