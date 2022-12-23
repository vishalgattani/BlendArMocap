'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import mediapipe as mp
from mediapipe.framework.formats import classification_pb2

from . import detector_interface

from scipy.spatial import distance
import numpy as np
import bpy

def set_bpy_location(name, xyz):
     bpy.data.objects[name].location = xyz

def set_bpy_euler_rotation(name, xyz):
    bpy.data.objects[name].rotation_euler = xyz

def set_bpy_scale(name, xyz):
    bpy.data.objects[name].scale = xyz

# Variables:
# x:input value;
# a,b:input range
# c,d:output range
# y:return value
# Function:

def mapFromTo(x,a,b,c,d):
   y=(x-a)/(b-a)*(d-c)+c
   return y

class HandDetector(detector_interface.RealtimeDetector):
    # https://google.github.io/mediapipe/solutions/hands#python-solution-api
    def image_detection(self):
        with self.solution.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_detection(mp_lib)

    def stream_detection(self):
        with self.solution.Hands(
                min_detection_confidence=0.8,
                min_tracking_confidence=0.5,
                static_image_mode=False,
                max_num_hands=2
        ) as mp_lib:
            while self.stream.capture.isOpened():
                return self.exec_detection(mp_lib)

    def initialize_model(self):
        self.solution = mp.solutions.hands

    def seperate_hands(self, hand_data):
        left_hand = [data[0] for data in hand_data if data[1][1] is False]
        right_hand = [data[0] for data in hand_data if data[1][1] is True]
        return left_hand, right_hand

    def cvt_hand_orientation(self, orientation: classification_pb2):
        if not orientation:
            return None

        return [[idx, "Right" in str(o)] for idx, o in enumerate(orientation)]

    def get_detection_results(self, mp_res):
        data = [self.cvt2landmark_array(hand) for hand in mp_res.multi_hand_world_landmarks]
        # multi_hand_world_landmarks // multi_hand_landmarks
        left_hand_data, right_hand_data = self.seperate_hands(
            list(zip(data, self.cvt_hand_orientation(mp_res.multi_handedness))))
        if(left_hand_data):
            lh_it_coords = np.asarray(left_hand_data[0][8][1])
            lh_tt_coords = np.asarray(left_hand_data[0][4][1])
            cosine_angle = np.dot(lh_it_coords, lh_tt_coords) / (np.linalg.norm(lh_it_coords) * np.linalg.norm(lh_tt_coords))
            left_gripper_angle = np.arccos(cosine_angle)
            left_gripper_angle = np.degrees(left_gripper_angle)
            left_pinch_distance = distance.euclidean(lh_it_coords,lh_tt_coords)
            # print("L:",left_gripper_angle,left_pinch_distance)
            val = mapFromTo(left_gripper_angle,10,80,-17.5,60)
            set_bpy_euler_rotation("left_gripper_joint",(0,0, np.radians(val)))
        if(right_hand_data):
            rh_it_coords = np.asarray(right_hand_data[0][8][1])
            rh_tt_coords = np.asarray(right_hand_data[0][4][1])
            cosine_angle = np.dot(rh_it_coords, rh_tt_coords) / (np.linalg.norm(rh_it_coords) * np.linalg.norm(rh_tt_coords))
            right_gripper_angle = np.arccos(cosine_angle)
            right_gripper_angle = np.degrees(right_gripper_angle)
            right_pinch_distance = distance.euclidean(rh_it_coords,rh_tt_coords)
            # print("R:",right_gripper_angle,right_pinch_distance)
            val = mapFromTo(right_gripper_angle,10,80,17.5,-60)
            set_bpy_euler_rotation("right_gripper_joint",(0,0, np.radians(val)))

        scene = bpy.context.scene
        objects = [obj for obj in scene.objects]



        # right_gripper_joint = bpy.context.scene.objects["right_gripper_joint"]
        # right_gripper_joint = bpy.data.objects["right_gripper_joint"]





        return left_hand_data, right_hand_data

    def contains_features(self, mp_res):
        if not mp_res.multi_hand_landmarks and not mp_res.multi_handedness:
            return False
        return True

    def draw_result(self, s, mp_res, mp_drawings):
        for hand in mp_res.multi_hand_landmarks:
            mp_drawings.draw_landmarks(s.frame, hand, self.solution.HAND_CONNECTIONS)


# region manual tests
def init_detector_manually(processor_type: str = "RAW"):
    m_detector = HandDetector()
    from ..cgt_utils import stream
    m_detector.stream = stream.Webcam()
    m_detector.initialize_model()

    from ..cgt_patterns import events
    if processor_type == "RAW":
        m_detector.observer = events.PrintRawDataUpdate()
    else:
        from ..cgt_bridge import print_bridge
        from ..cgt_processing import hand_processing
        bridge = print_bridge.PrintBridge
        target = hand_processing.HandProcessor(bridge)
        m_detector.observer = events.DriverDebug(target)

    m_detector.listener = events.UpdateListener()
    m_detector.listener.attach(m_detector.observer)
    return m_detector


if __name__ == '__main__':
    detection_type = "image"
    detector = init_detector_manually("PROCESSED")

    if detection_type == "image":
        for _ in range(50):
            detector.image_detection()
    else:
        detector.stream_detection()

    del detector
# endregion
