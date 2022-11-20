#!/usr/bin/env python3

# http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+2%3A+GStreamer+concepts

import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib, GObject

from helper import bus_call

# initialize GStreamer
Gst.init(None)

# create the elements
source = Gst.ElementFactory.make("videotestsrc", "source")
filter_vertigo = Gst.ElementFactory.make("vertigotv", "vertigo-filter")
videoconvert = Gst.ElementFactory.make("videoconvert", "video-convert")
sink = Gst.ElementFactory.make("autovideosink", "sink")

# create the empty pipeline
pipeline = Gst.Pipeline.new("test-pipeline")

if not pipeline or not source or not filter_vertigo or not videoconvert or not sink:
    print("ERROR: Not all elements could be created")
    sys.exit(1)

# build the pipeline
pipeline.add(source)
pipeline.add(filter_vertigo)
pipeline.add(videoconvert)
pipeline.add(sink)
if not source.link(filter_vertigo):
    print("ERROR: Could not link source to filter-vertigo")
    sys.exit(1)

if not filter_vertigo.link(videoconvert):
    print("ERROR: Could not link filter-vertigo to videoconvert")
    sys.exit(1)

if not videoconvert.link(sink):
    print("ERROR: Could not link videoconvert to sink")
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
bus.add_signal_watch()
bus.connect("message", bus_call, loop)

try:
    loop.run()
except:
    pass

pipeline.set_state(Gst.State.NULL)
