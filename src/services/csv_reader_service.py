import csv
import io




class CSVReader:

    def read(self, stream):

        text_stream = io.TextIOWrapper(stream,encoding="utf-8")
        reader = csv.DictReader(text_stream)

        for row in reader:
            yield row