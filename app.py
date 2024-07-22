from flask import Flask, render_template, jsonify
import cv2

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect_qr')
def detect_qr():
    # QR code detection logic
    return jsonify({"coupon": "Congratulations! You've won a 20% discount!"})

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/detect_qr')
def detect_qr():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    while True:
        _, img = cap.read()
        data, bbox, _ = detector.detectAndDecode(img)
        if data:
            cap.release()
            return jsonify({"coupon": "Congratulations!"})
