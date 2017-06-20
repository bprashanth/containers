"""
This scripts demonstrates how to use mitmproxy's filter pattern in scripts.
Usage:
    mitmdump -s "flowfilter.py FILTER"
"""
import sys
from mitmproxy import flowfilter


class Filter:
    def __init__(self, spec):
        self.filter = flowfilter.parse(spec)
        self.raw_filter = spec

    def print_flow(self, flow):
        print("##################### Flow ###################")
        print(flow)
        print("##################### Request headers ###################")
        for i in flow.request.headers:
          print("%s %s" % (i, flow.request.headers[i]))
        print("##################### Response headers ######################")
        for i in flow.response.headers:
          print("%s %s" % (i, flow.response.headers[i]))
        print("##################### End Flow ######################")


    def response(self, flow):
        if flowfilter.match(self.filter, flow):
            print("Flow matches filter:")
            print(flow)
        if (flow.server_conn.sni != None) & (str(flow.server_conn.sni).find(self.raw_filter) != -1):
            print("Flow matches SNI hostname:")
            print(flow)


def start():
    if len(sys.argv) != 2:
        raise ValueError("Usage: -s 'filt.py FILTER'")

    return Filter(sys.argv[1])
