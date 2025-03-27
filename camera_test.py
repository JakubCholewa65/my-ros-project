#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from sensor_msgs.msg import CompressedImage
import cv2
from cv_bridge import CvBridge

class CameraReaderNode(DTROS):

    def __init__(self, node_name):
        # initialize the DTROS parent class
        super(CameraReaderNode, self).__init__(node_name=node_name, node_type=NodeType.VISUALIZATION)
        # static parameters
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self._camera_topic = f"/{self._vehicle_name}/camera_node/image/compressed"
        # bridge between OpenCV and ROS
        self._bridge = CvBridge()
        # create window
        self._window = "camera-reader"
        cv2.namedWindow(self._window, cv2.WINDOW_AUTOSIZE)
        # construct subscriber
        self.sub = rospy.Subscriber(self._camera_topic, CompressedImage, self.callback)

        # initialize folder and counter
        self.screenshot_counter = 0
        self.current_folder = 1
        self.max_screenshots_per_folder = 4

        # ensure screenshots base directory exists
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    def callback(self, msg):
        # convert JPEG bytes to CV image
        image = self._bridge.compressed_imgmsg_to_cv2(msg)
        # display frame
        cv2.imshow(self._window, image)

        # check for key press
        key = cv2.waitKey(1) & 0xFF

        # if 's' is pressed, save the screenshot
        if key == ord('s'):
            self.save_screenshot(image)

    def save_screenshot(self, image):
        # create directory for the current folder if it doesn't exist
        folder_path = os.path.join("screenshots", str(self.current_folder))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # generate a filename based on the counter
        filename = os.path.join(folder_path, "screenshot_{}.png".format(self.screenshot_counter + 1))

        # save the image
        cv2.imwrite(filename, image)
        rospy.loginfo(f"Zapisano zrzut ekranu: {filename}")

        # increment screenshot counter
        self.screenshot_counter += 1

        # if we've reached the max number of screenshots per folder, move to the next folder
        if self.screenshot_counter >= self.max_screenshots_per_folder:
            self.screenshot_counter = 0
            self.current_folder += 1

if __name__ == '__main__':
    # create the node
    node = CameraReaderNode(node_name='camera_reader_node')
    # keep spinning
    rospy.spin()

