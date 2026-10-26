import gzip
from botocore.response import StreamingBody




class Decompressor:


    def decompress(self, stream: StreamingBody):
        return gzip.GzipFile(fileobj=stream,mode="rb")