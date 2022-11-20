import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst


def format_ns(ns):
    s, ns = divmod(ns, 1000000000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)

    return "%u:%02u:%02u.%09u" % (h, m, s, ns)


def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True
