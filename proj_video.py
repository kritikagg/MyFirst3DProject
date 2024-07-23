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

        # Load the video to play
        self.video = cv2.VideoCapture('C:\\Users\\User 2\\Downloads\\video.mp4')
        self.play_video = False
        self.video_frame = None

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        decoded_objects = decode(frame)
        self.play_video = False

        for obj in decoded_objects:
            points = obj.polygon
            if len(points) == 4:
                self.play_video = True

                # Get the bounding box of the QR code
                points = np.array([(p.x, p.y) for p in points], dtype=np.float32)
                rect = cv2.boundingRect(points)
                x, y, w, h = rect

                ret, video_frame = self.video.read()
                if ret:
                    # Resize the video frame to fit the QR code area
                    video_frame_resized = cv2.resize(video_frame, (w, h))
                    video_frame_rgb = cv2.cvtColor(video_frame_resized, cv2.COLOR_BGR2RGB)
                    h, w, ch = video_frame_rgb.shape
                    bytes_per_line = ch * w
                    convert_to_Qt_format = QImage(video_frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

                    # Overlay the video frame on the camera frame
                    frame[y:y+h, x:x+w] = video_frame_resized
                else:
                    # Reset video playback if it ends
                    self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

                break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(convert_to_Qt_format))

    def closeEvent(self, event):
        self.cap.release()
        self.video.release()

def main():
    import sys
    app = QApplication(sys.argv)
    window = VideoWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
