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
from .mp_detector_node import DetectorNode
from typing import Mapping, Tuple
from mediapipe.python.solutions import face_mesh_connections
from mediapipe.python.solutions.drawing_utils import DrawingSpec


class FaceDetector(DetectorNode):
    def __init__(self, *args, **kwargs):
        DetectorNode.__init__(self, *args, **kwargs)
        self.solution = mp.solutions.face_mesh

    def update(self, data, frame):
        with self.solution.FaceMesh(
                max_num_faces=1,
                static_image_mode=False,
                refine_landmarks=True,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_detection(mp_lib), frame

    def empty_data(self):
        return [[[]]]

    def detected_data(self, mp_res):
        return [self.cvt2landmark_array(landmark) for landmark in mp_res.multi_face_landmarks]

    def contains_features(self, mp_res):
        if not mp_res.multi_face_landmarks:
            return False
        return True

    @staticmethod
    def get_custom_face_mesh_contours_style() -> Mapping[Tuple[int, int], DrawingSpec]:
        _THICKNESS_CONTOURS = 2

        _RED = (48, 48, 255)
        _WHITE = (224, 224, 224)

        _FACEMESH_CONTOURS_CONNECTION_STYLE = {
            face_mesh_connections.FACEMESH_LIPS:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_LEFT_EYE:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_LEFT_EYEBROW:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_RIGHT_EYE:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_RIGHT_EYEBROW:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_FACE_OVAL:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
        }

        face_mesh_contours_connection_style = {}
        for k, v in _FACEMESH_CONTOURS_CONNECTION_STYLE.items():
            for connection in k:
                face_mesh_contours_connection_style[connection] = v
        return face_mesh_contours_connection_style

    def draw_result(self, s, mp_res, mp_drawings):
        """Draws the landmarks and the connections on the image."""
        for face_landmarks in mp_res.multi_face_landmarks:
            self.drawing_utils.draw_landmarks(
                image=self.stream.frame,
                landmark_list=face_landmarks,
                connections=self.solution.FACEMESH_CONTOURS,
                connection_drawing_spec=self.get_custom_face_mesh_contours_style(),
                # connection_drawing_spec=self.drawing_style.get_default_face_mesh_contours_style(),
                landmark_drawing_spec=None)

                # image=self.stream.frame,
                # landmark_list=face_landmarks,
                # connections=self.solution.FACEMESH_IRISES,
                # landmark_drawing_spec=None,
                # connection_drawing_spec=self.drawing_style.get_default_face_mesh_iris_connections_style())


# region manual tests
if __name__ == '__main__':
    from . import cv_stream
    from ...cgt_core.cgt_calculators_nodes import calc_face_rot_sca
    detector = FaceDetector(cv_stream.Stream(0))
    calc = calc_face_rot_sca.FaceRotationcalculator()
    frame = 0
    for _ in range(50):
        frame += 1
        data, frame = detector.update(None, frame)
        data, frame = calc.update(data, frame)
        print(data)

    del detector
# endregion
