from pyspark import SparkContext
import os
import hashlib

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
# def generate_hashes(fd, output_file=sys.stdout):
#     CHUNK_SIZE = 1024 * 100
#     calc_hash = hashlib.md5()
#     data = fd.read(CHUNK_SIZE)
#     while data:
#         calc_hash.update(data)
#         data = fd.read(CHUNK_SIZE)

#     fd.close()
#     output_file.write(calc_hash.hexdigest() + "\n")

# def write_tar_sums(in_dir, out_file=sys.stdout):
#     for subdir, dirs, files in os.walk(in_dir):
#         for f in files:
#             filepath = subdir + os.sep + f 

#             with open(filepath, "rb") as fd:
#                 generate_hashes(fd, out_file)


# def make_tarfile(out_file, in_dir):
#     t = tarfile.open(out_file, "w:gz")
#     t.add(in_dir, arcname=os.path.basename(in_dir))
