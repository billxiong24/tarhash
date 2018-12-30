import tarhash
import uuid
import shutil
import os
import subprocess
import tarfile
import filecmp

HASH_FNAME="tar_hashes"
HASH_EXT=".HASH.TXT"
TEMP_FNAME="temp"

def package_dir(in_dir, tar_file):

    rand_id = uuid.uuid4().hex
    hash_file = "%s%s%s" %(HASH_FNAME, rand_id, HASH_EXT)
    # contains the real data
    tmp_tar = "%s%s"%(rand_id, tar_file)
    res = tarhash.write_tar_sums_file(in_dir, tmp_tar, hash_file, to_write=True)

    # something went wrong
    if res is not 0:
        return

    # package tar and hash file in another tar
    tar_package = tarfile.open(tar_file, "w:gz")
    tar_package.add(tmp_tar)
    tar_package.add(hash_file)
    tar_package.close()
    # clean up
    os.remove(tmp_tar)
    os.remove(hash_file)

def unpackage_and_verify_tar(tar_file):
    try:
        if not tarfile.is_tarfile(tar_file):
            logging.error("File '%s' is not a tar file.\n" % (tar_file))
            return False
    except IOError, e:
        logging.error("File '%s' does not exist.\n" % (tar_file))
        return False

    tar_obj = tarfile.open(tar_file, "r|*")

    hash_txt = ""
    rand_id = uuid.uuid4().hex
    calc_hash_fname = "%s%s%s" % (TEMP_FNAME, rand_id, HASH_EXT)
    for member in tar_obj:
        fd = tar_obj.extract(member)
        # the tar file with all the data
        if member.name.endswith(tar_file):
            tarhash.calc_tar_sums_from_tar(member.name,calc_hash_fname) 
            os.remove(member.name)
        # the txt file with hashes
        elif member.name.startswith(HASH_FNAME) and member.name.endswith(HASH_EXT):
            hash_txt = member.name

    tar_obj.close()

    cmp_res = filecmp.cmp(hash_txt, calc_hash_fname)
    os.remove(calc_hash_fname)
    os.remove(hash_txt)

    return cmp_res

package_dir("env", "content.tar")
print unpackage_and_verify_tar("content.tar")
