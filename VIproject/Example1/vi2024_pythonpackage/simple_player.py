import sys
import time
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy
import typer

from azure_kinect_video_player.playback_wrapper import AzureKinectPlaybackWrapper

app = typer.Typer()


@app.command()
def app_main(video_filename: Path = typer.Argument(..., help="kinect-training-set.mkv"),
             realtime_wait: bool = typer.Option(True, help="Wait for the next frame to be displayed"),
             rgb: bool = typer.Option(True, help="Display RGB image"),
             depth: bool = typer.Option(True, help="Display depth image"),
             ir: bool = typer.Option(True, help="Display IR image")):

    # Get the video filename from the command line
    video_filename = Path(video_filename)#video_filename

    # Create the playback wrapper
    playback_wrapper = AzureKinectPlaybackWrapper(video_filename,
                                                  realtime_wait=realtime_wait,
                                                  auto_start=False,
                                                  rgb=rgb,
                                                  depth=depth,
                                                  ir=ir)

    # Create windows for the colour, depth, and ir images
    if rgb:
        cv2.namedWindow("Colour", cv2.WINDOW_NORMAL)
    if depth:
        cv2.namedWindow("Depth", cv2.WINDOW_NORMAL)
    if ir:
        cv2.namedWindow("IR", cv2.WINDOW_NORMAL)

    # Start timer
    start_time = time.time()
    playback_wrapper.start()

    try:
        # Loop through the frames
        for colour_image, depth_image, ir_image in playback_wrapper.grab_frame():

            # If all images are None, break (probably reached the end of the video)
            if colour_image is None and depth_image is None and ir_image is None:
                break

            # YOUR OBJECT DETECTION / RECOGNITION CODE HERE!

            # Display the colour, depth, and ir images
            if rgb and colour_image is not None:
                cv2.imshow("Colour", colour_image)

            if depth and depth_image is not None:
                cv2.imshow("Depth", depth_image)

            if ir and ir_image is not None:
                cv2.imshow("IR", ir_image)

            # Wait for key press
            key = cv2.waitKey(1)

            # If q or ESC is pressed, break
            if key == ord("q") or key == 27:
                break

    except KeyboardInterrupt:
        pass

    # Stop timer
    end_time = time.time()

    # Print the time taken
    print("Time taken: {}s".format(end_time - start_time))

    # Close the windows
    cv2.destroyAllWindows()

    # Stop the playback wrapper
    playback_wrapper.stop()

    return 0


if __name__ == "__main__":
    sys.exit(app())
