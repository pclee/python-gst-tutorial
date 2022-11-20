#!/usr/bin/env python3

import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

from helper import bus_call

# http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+3%3A+Dynamic+pipelines


class Player(object):
    def __init__(self):
        # initialize GStreamer
        Gst.init(None)

        # create the elements
        self.source = Gst.ElementFactory.make("uridecodebin", "source")
        self.convert = Gst.ElementFactory.make("audioconvert", "convert")
        self.resample = Gst.ElementFactory.make("audioresample", "resample")
        self.sink = Gst.ElementFactory.make("autoaudiosink", "sink")

        # create empty pipeline
        self.pipeline = Gst.Pipeline.new("test-pipeline")

        if (
            not self.pipeline
            or not self.source
            or not self.convert
            or not self.resample
            or not self.sink
        ):
            print("ERROR: Could not create all elements")
            sys.exit(1)

        # build the pipeline. we are NOT linking the source at this point.
        # will do it later
        self.pipeline.add(self.source)
        self.pipeline.add(self.convert)
        self.pipeline.add(self.resample)
        self.pipeline.add(self.sink)
        if not self.convert.link(self.sink):
            print("ERROR: Could not link 'convert' to 'sink'")
            sys.exit(1)

        # set the URI to play
        self.source.set_property(
            "uri",
            "https://www.freedesktop.org/software/gstreamer-sdk/data/media/sintel_trailer-480p.webm",
        )

        # connect to the pad-added signal
        self.source.connect("pad-added", self.on_pad_added)

        loop = GLib.MainLoop()

        # listen to the bus
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", bus_call, loop)

        # start playing
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Unable to set the pipeline to the playing state")
            sys.exit(1)
        try:
            loop.run()
        except:
            pass

        self.pipeline.set_state(Gst.State.NULL)

    # handler for the pad-added signal
    def on_pad_added(self, src, new_pad):
        sink_pad = self.convert.get_static_pad("sink")
        print(
            "Received new pad '{0:s}' from '{1:s}'".format(
                new_pad.get_name(), src.get_name()
            )
        )

        # if our converter is already linked, we have nothing to do here
        if sink_pad.is_linked():
            print("We are already linked. Ignoring.")
            return

        # check the new pad's type
        new_pad_caps = new_pad.get_current_caps()
        new_pad_struct = new_pad_caps.get_structure(0)
        new_pad_type = new_pad_struct.get_name()

        if not new_pad_type.startswith("audio/x-raw"):
            print(
                "It has type '{0:s}' which is not raw audio. Ignoring.".format(
                    new_pad_type
                )
            )
            return

        # attempt the link
        ret = new_pad.link(sink_pad)
        if not ret == Gst.PadLinkReturn.OK:
            print("Type is '{0:s}}' but link failed".format(new_pad_type))
        else:
            print("Link succeeded (type '{0:s}')".format(new_pad_type))

        return


if __name__ == "__main__":
    p = Player()
