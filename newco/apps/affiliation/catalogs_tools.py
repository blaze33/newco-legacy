import csv
from urllib2 import Request, urlopen, URLError


def csv_url2dict(csv_url):
    # TODO: check the meaning of the date in headers and skip db updating
    #       if csv hasn't changed

    req = Request(csv_url)
    try:
        csv_file = urlopen(req)
    except URLError, e:
        if hasattr(e, "reason"):
            print "Failed to reach a server."
            print "Reason: %s" % e.reason
        elif hasattr(e, "code"):
            print "The server couldn\'t fulfill the request."
            print "Error code: %s" % e.code
        return None
    else:
        csv_header = csv_file.readline()
        csv_dialect = csv.Sniffer().sniff(csv_header, delimiters=";")

        # Cleaning header by removing \r\n at the EOL + doublequotes
        cleaned_csv_header = str.replace(csv_header[:-2],
                                                    csv_dialect.quotechar, '')
        # Manually extracting fieldnames.
        fieldnames = str.split(cleaned_csv_header, csv_dialect.delimiter)

        return csv.DictReader(csv_file, fieldnames=fieldnames,
                                        dialect=csv_dialect)
