import tarfile
import hashlib
import subprocess
import sys
import os
import logging

def generate_hashes(fd):
    CHUNK_SIZE = 1024 * 100
    calc_hash = hashlib.md5()
    data = fd.read(CHUNK_SIZE)
    while data:
        calc_hash.update(data)
        data = fd.read(CHUNK_SIZE)

    fd.close()
    return calc_hash.hexdigest()

def write_tar_sums_file(in_dir, tar_file, out_file):
    if not os.path.isdir(in_dir):
        logging.error("Target directory %s does not exist." % (in_dir))
        return 1
    
    cmd = "tar -cvpf %s %s | xargs -I '{}' sh -c \"test -f '{}' && md5sum '{}'\" | cut -f 1 -d ' ' > %s" % (tar_file, in_dir, out_file)
    exit_code = subprocess.call(cmd, shell=True)
    if exit_code == 0:
        logging.info("Tar file and hash file successfully created.")
    else:
        logging.error("Something went wrong when creating tar file.")

def calc_tar_sums_from_tar(input_file, out_file=sys.stdout):
    out_fd = None
    if out_file is sys.stdout:
        out_fd = sys.stdout
    else:
        out_fd = open(out_file, 'w')

    hashes = []
    try:
        if not tarfile.is_tarfile(input_file):
            logging.error("File is not a tar file.\n")
            return 1
    except IOError, e:
        logging.error("File does not exist.\n")
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
        out_fd.write(generate_hashes(fd) + "\n")
    return 0

write_tar_sums_file("msgtb", "back.tar", "hashes.md5")
calc_tar_sums_from_tar("back.tar", "hash_sink.md5")
