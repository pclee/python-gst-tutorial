#!/usr/bin/env python3

# http://docs.gstreamer.com/pages/viewpage.action?pageId=327735

import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject, GLib

from helper import bus_call


def main():

    # initialize GStreamer
    Gst.init(None)

    playbin = Gst.ElementFactory.make("playbin", None)
    if not playbin:
        sys.stderr.write("'playbin' gstreamer plugin missing\n")
        sys.exit(1)

    uri = Gst.filename_to_uri(
        "/home/peter/study/gstreamer/bbb_sunflower_1080p_60fps_normal.mp4"
    )
    playbin.set_property("uri", uri)

    # create an event loop and feed gstreamer bus messages to it
    loop = GLib.MainLoop()

    # wait until EOS or error
    bus = playbin.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    # start playing and listen to events
    playbin.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except:
        pass

    # free resources
    playbin.set_state(Gst.State.NULL)


if __name__ == "__main__":
    sys.exit(main())
