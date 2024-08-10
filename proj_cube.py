import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
class VideoWindow(QMainWindow):
def __init__(self):
        super().__init__()

        self.setWindowTitle("QR Code Detector")

        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel(self)

        self.label.resize(800, 600)

        self.cap = cv2.VideoCapture(0)

        self.timer = QTimer()

        self.timer.timeout.connect(self.update_frame)

        self.timer.start(30)

 

    def draw_cube(self, img, imgpts, color=(105, 0, 255)):

        imgpts = np.int32(imgpts).reshape(-1, 2)

 

        # Draw ground floor in green

        cv2.drawContours(img, [imgpts[:4]], -1, color, -3)

 

        # Draw pillars in blue color

        for i, j in zip(range(4), range(4, 8)):

            cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), color, 3)

 

        # Draw top layer in red color

        cv2.drawContours(img, [imgpts[4:]], -1, color, 3)

 

    def update_frame(self):

        ret, frame = self.cap.read()

        if not ret:

            return

 

        decoded_objects = decode(frame)

        for obj in decoded_objects:

            points = obj.polygon

            if len(points) == 4:

                points = np.array([(p.x, p.y) for p in points], dtype=np.float32)

                hull = cv2.convexHull(points).astype(int)

                cv2.polylines(frame, [hull], True, (0, 255, 0), 2)

 

                # Define the 3D coordinates of the QR code corners in the real world (assuming a square QR code)

                qr_size = 0.5  # Define the real-world size of the QR code (e.g., 1 unit)

                objp = np.array([

                    [0, 0, 0],

                    [qr_size, 0, 0],

                    [qr_size, qr_size, 0],

                    [0, qr_size, 0]

                ], dtype=np.float32)

 

                camera_matrix = np.array([

                    [frame.shape[1], 0, frame.shape[1] / 2],

                    [0, frame.shape[1], frame.shape[0] / 2],

                    [0, 0, 1]

                ], dtype=np.float32)

 

                dist_coeffs = np.zeros((4, 1))

 

                try:

                    retval, rvec, tvec = cv2.solvePnP(objp, points, camera_matrix, dist_coeffs)

                    if not retval:

                        print("solvePnP failed")

                        continue

 

                    # Project a 3D cube on top of the QR code

                    cube_size = qr_size  # Cube size should match the QR code size

                    cube_points = np.float32([

                        [0, 0, 0], [cube_size, 0, 0], [cube_size, cube_size, 0], [0, cube_size, 0],

                        [0, 0, cube_size], [cube_size, 0, cube_size], [cube_size, cube_size, cube_size], [0, cube_size, cube_size]

                    ])

 

                    cube_imgpts, _ = cv2.projectPoints(cube_points, rvec, tvec, camera_matrix, dist_coeffs)

                    self.draw_cube(frame, cube_imgpts)

                except cv2.error as e:

                    print(f"cv2.solvePnP error: {e}")

 

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_image.shape

        bytes_per_line = ch * w

        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self.label.setPixmap(QPixmap.fromImage(convert_to_Qt_format))

 

    def closeEvent(self, event):

        self.cap.release()

 

def main():

    import sys

    app = QApplication(sys.argv)

    window = VideoWindow()

    window.show()

    sys.exit(app.exec_())

 

if __name__ == "__main__":

    main()
