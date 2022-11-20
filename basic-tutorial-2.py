#!/usr/bin/env python3

# http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+2%3A+GStreamer+concepts

import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib, GObject


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


def main(args):
    # initialize GStreamer
    Gst.init(None)

    # create the elements
    source = Gst.ElementFactory.make("videotestsrc", "source")
    sink = Gst.ElementFactory.make("autovideosink", "sink")

    # create the empty pipeline
    pipeline = Gst.Pipeline.new("test-pipeline")

    if not pipeline or not source or not sink:
        print("ERROR: Not all elements could be created")
        sys.exit(1)

    # build the pipeline
    pipeline.add(source)
    pipeline.add(sink)
    if not source.link(sink):
        print("ERROR: Could not link source to sink")
        sys.exit(1)

    # modify the source's properties
    source.set_property("pattern", 0)

    loop = GLib.MainLoop()

    # start playing
    ret = pipeline.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("ERROR: Unable to set the pipeline to the playing state")

    # wait for EOS or error
    bus = pipeline.get_bus()
    # msg = bus.timed_pop_filtered(
    #     Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS
    # )
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    try:
        loop.run()
    except:
        pass

    # cleanup
    pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
