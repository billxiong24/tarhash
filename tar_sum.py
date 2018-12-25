import tarfile
import hashlib
import subprocess
import sys
import os

def write_tar_sums_file(in_dir, tar_file, out_file):
    # tar -cvpf back.tar billxiong24/msgtb | xargs -I '{}' sh -c "test -f '{}' && md5sum '{}'" | cut -f 1 -d " "
    cmd = "tar -cvpf %s %s | xargs -I '{}' sh -c \"test -f '{}' && md5sum '{}'\" | cut -f 1 -d ' ' | tee %s" % (tar_file, in_dir, out_file)
    return subprocess.call(cmd, shell=True)

def make_tarfile(out_file, in_dir):
    t = tarfile.open(out_file, "w:gz")
    t.add(in_dir, arcname=os.path.basename(in_dir))
    t.close()


def calc_tar_sums(input_file, out_file=sys.stdout):
    out_fd = None
    if out_file is sys.stdout:
        out_fd = sys.stdout
    else:
        out_fd = open(out_file, 'w')

    hashes = []
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
        fd.write(generate_hashes(fd))
    return 0

write_tar_sums_file("msgtb", "back.tar", "hashes.md5")
sys.stdout.write("---------------\n")
calc_tar_sums("back.tar")
