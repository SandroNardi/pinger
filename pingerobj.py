import texttable as tt
import json


class Pinger:
    def __init__(self, name, serial, pingid):
        self.serial = serial
        self.pingid = pingid
        self.name = name

    def __repr__(self):
        rep = "["+self.serial+","+self.pingid+"]"
        return rep

    def toArray(self):
        return [self.name, self.serial, self.pingid]


if __name__ == "__main__":

    tb = tt.Texttable()
    tb.header(["serial", " ID"])

    ping1 = Pinger("aaaa", "bbbb", "cccc")
    tb.add_row(ping1.toArray())
    # print(repr(ping1))
    #tb.add_row(["serial", " ID"])
    print(tb.draw())

# new class
