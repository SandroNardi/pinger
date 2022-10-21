import texttable as tt
import json


class Pinger:
    def __init__(self, serial, pingid):
        self.serial = serial
        self.pingid = pingid

    def __repr__(self):
        rep = "["+self.serial+","+self.pingid+"]"
        return rep

    def printresult(self):
        print("Serial " + self.serial + " ID: " + self.pingid)


if __name__ == "__main__":

    tb = tt.Texttable()
    tb.header(["serial", " ID"])

    ping1 = Pinger("aaaa", "bbbb")
    tb.add_row(repr(ping1))
    # print(repr(ping1))

    print(tb.draw)