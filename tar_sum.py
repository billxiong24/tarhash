import tarfile
import hashlib
import sys
import os

def generate_hashes(fd, output_file=sys.stdout):
    CHUNK_SIZE = 1024 * 100
    calc_hash = hashlib.md5()
    data = fd.read(CHUNK_SIZE)
    while data:
        calc_hash.update(data)
        data = fd.read(CHUNK_SIZE)

    fd.close()
    output_file.write(calc_hash.hexdigest() + "\n")

def write_tar_sums(in_dir, out_file=sys.stdout):
    for subdir, dirs, files in os.walk(in_dir):
        for f in files:
            filepath = subdir + os.sep + f 

            with open(filepath, "rb") as fd:
                generate_hashes(fd, out_file)


def make_tarfile(out_file, in_dir):
    t = tarfile.open(out_file, "w:gz")
    t.add(in_dir, arcname=os.path.basename(in_dir))


def calc_tar_sums(input_file, output_file=sys.stdout):
    try:
        if not tarfile.is_tarfile(input_file):
            sys.stderr.write("File is not a tar file.\n")
            return 1
    except IOError, e:
        sys.stderr.write("File does not exist.\n")
        return 2

    # file exists and is a tar file, open file in read and stream mode
    tar_obj = tarfile.open(input_file, "r|*")
    # can't do getmembers, because that reads through the entire stream
    for member in tar_obj:
        if not member.isfile():
            continue
        # file exists, don't have to check for existence
        # can't do member.name, because that reads ahead of the stream
        fd = tar_obj.extractfile(member)
        # not a regular file nor some link
        if fd is None:
            continue
        generate_hashes(fd, output_file)
    return 0



#calc_tar_sums("back.tar")
