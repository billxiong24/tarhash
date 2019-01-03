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

sc = SparkContext("local", "tarhash")
files = list(os.walk("msgtb"))
words = sc.parallelize(files).flatMap(lambda xs: [(xs[0] + os.sep + x) for x in xs[2]]) # transform os.walk into a list of file paths
hashes = words.map(generate_hash).sortBy(lambda x: x, ascending=True)
hashes.saveAsTextFile("hashes")


t = tarfile.open("temp.tar", "w:gz")
t.add("msgtb", arcname=os.path.basename("msgtb"))
t.add("hashes/part-00000")
# t.addfile(tarfile.TarInfo("hashes.txt"), fd)
t.close()
