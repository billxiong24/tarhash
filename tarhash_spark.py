from pyspark import SparkContext
import os
import hashlib
import tarfile
import shutil

def generate_hash(fname):
    fd = open(fname, "rb")
    CHUNK_SIZE = 1024 * 100
    calc_hash = hashlib.md5()
    data = fd.read(CHUNK_SIZE)
    while data:
        calc_hash.update(data)
        data = fd.read(CHUNK_SIZE)

    fd.close()
    return calc_hash.hexdigest()

def create_hash_file(tar_list):
    files = []
    for fname in tar_list:
        # TODO check if file exists/ is file
         files += list(os.walk(fname))

    print files
    # sc = SparkContext("local[8]", "tarhash")
    # words = sc.parallelize(files).flatMap(lambda xs: [(xs[0] + os.sep + x) for x in xs[2]]) # transform os.walk into a list of file paths
    # words = words.map(lambda el : (el, el)).partitionBy(8)
    # hashes = words.map(lambda el: generate_hash(el[0])).sortBy(lambda x: x, ascending=True)
    # hashes.coalesce(1).saveAsTextFile("hashes")


create_hash_file(["msgtb", "testdir"])
# t = tarfile.open("temp.tar", "w:gz")
# t.add("env", arcname=os.path.basename("env"))
# t.add("hashes/part-00000")
# t.addfile(tarfile.TarInfo("hashes.txt"), fd)
# t.close()
