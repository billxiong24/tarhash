import tarfile
import hashlib
import subprocess
import sys
import os
import logging

logging.getLogger().setLevel(logging.INFO)

def _generate_hashes(fd):
    CHUNK_SIZE = 1024 * 100
    calc_hash = hashlib.md5()
    data = fd.read(CHUNK_SIZE)
    while data:
        calc_hash.update(data)
        data = fd.read(CHUNK_SIZE)

    fd.close()
    return calc_hash.hexdigest()

def write_tar_sums_file(in_dir, tar_file, out_file=None, to_write=False):
    if not os.path.isdir(in_dir):
        logging.error("Target directory %s does not exist." % (in_dir))
        return 1

    if out_file is None and to_write is True:
        logging.error("Must specify a valid output file for hashes.")
        return 1

    if out_file is not None:
        to_write = True

    cmd=""
    if to_write is False:
        cmd = "tar -cvpf %s %s | xargs -I '{}' sh -c \"test -f '{}' && md5sum '{}'\" | cut -f 1 -d ' '" % (tar_file, in_dir)
    else:
        cmd = "tar -cvpf %s %s | xargs -I '{}' sh -c \"test -f '{}' && md5sum '{}'\" | cut -f 1 -d ' ' > %s" % (tar_file, in_dir, out_file)

    exit_code = subprocess.call(cmd, shell=True)
    if exit_code is 0:
        logging.info("Tar file and hashes successfully created.")
        return 0

    logging.error("Something went wrong when creating tar file.")
    return 1

def calc_tar_sums_from_tar(input_file, out_file=sys.stdout):
    out_fd = None
    if out_file is sys.stdout:
        out_fd = sys.stdout
    else:
        out_fd = open(out_file, 'w')

    if out_file is not sys.stdout:
        logging.info("Opened '%s' for writing..." % (out_file))

    hashes = []
    try:
        if not tarfile.is_tarfile(input_file):
            logging.error("File '%s' is not a tar file.\n" % (input_file))
            return 1
    except IOError, e:
        logging.error("File '%s' does not exist.\n" % (input_file))
        return 2

    # file exists and is a tar file, open file in read and stream mode
    tar_obj = tarfile.open(input_file, "r|*")
    logging.info("Opened '%s' for reading..." % (input_file))
    # can't do getmembers, because that reads through the entire stream
    for member in tar_obj:
        if not os.path.isfile(member.name):
            continue
        # file exists, don't have to check for existence
        # can't do member.name, because that reads ahead of the stream
        fd = None
        if member.isfile():
            fd = tar_obj.extractfile(member)
        elif member.issym():
            fd = open(member.name)

        # not a regular file nor some link
        if fd is None:
            continue
        logging.info("Writing hash of %s..." % (member.name))
        out_fd.write(_generate_hashes(fd) + "\n")

    logging.info("Successfully calculated hashes for all files in '%s'" % (input_file))
    tar_obj.close()
    out_fd.close()
    return 0

#write_tar_sums_file("env", "back2.tar", "hash_in.md5")
#calc_tar_sums_from_tar("back2.tar", "hash_out.md5")
