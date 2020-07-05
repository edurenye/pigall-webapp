#!/usr/bin/env python

from flask import Flask, render_template, Response
from fuzzy_alert import FuzzyDangerDetector
from PIL import Image
import base64
import cv2
import flask
import numpy as np
import os
import sys
import io
import threading
from model import load_model
from app_utils import *

global dangerDetector
global currentFrame
global currentObjects
global imageSize
global model
global recording


print('Python version: ', sys.version, file=sys.stderr)
app = Flask(__name__)
recording = True
currentFrame = None
currentObjects = {
    'crosswalk': [],
    'dashed_crosswalk': [],
    'pedestrian_green': [],
    'pedestrian_off': [],
    'pedestrian_red': []
}
imageSize = 416
model_path = os.path.join(app.root_path, 'weights/best-yolov5s.pt')
classes_path = os.path.join(app.root_path, 'data', '_classes.txt')
model = load_model(app, model_type='pytorch', model_path=model_path, classes_path=classes_path)
danger_detector = FuzzyDangerDetector()


# Configurations with app.config['key'] or tinydb.

def run_recording_job():
    global recording
    global currentFrame
    global imageSize
    print('Recording job started.', file=sys.stderr)
    vc = cv2.VideoCapture(0)
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    offset_w = int(round((width - imageSize) / 2))
    print('Width offset: ', offset_w, file=sys.stderr)
    offset_h = int(round((height - imageSize) / 2))
    print('Height offset: ', offset_h, file=sys.stderr)
    success, frame = vc.read()
    print('Camera shape: ', np.shape(frame), file=sys.stderr)
    print('Frame shape: ', np.shape(frame[offset_h:offset_h + imageSize, offset_w:offset_w + imageSize]),
          file=sys.stderr)
    while True:
        if recording:
            success, frame = vc.read()
            if success:
                cropped_frame = frame[offset_h:offset_h + imageSize, offset_w:offset_w + imageSize]
                currentFrame = cropped_frame
            else:
                currentFrame = None
        else:
            currentFrame = None


thread = threading.Thread(target=run_recording_job)
thread.start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/capture')
def capture():
    """Video streaming"""
    return render_template('capture.html')


def gen():
    """Video streaming generator function."""
    while True:
        frame = currentFrame
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame)
            buff = io.BytesIO()
            pil_img.save(buff, format="JPEG")
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buff.getvalue() + b'\r\n')
        else:
            return None


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_detect():
    """Video streaming generator function."""
    while True:
        img, predictions = model.make_prediction(currentFrame)
        update_current_objects(currentObjects, predictions)
        dangers = get_dangers(danger_detector, currentObjects, imageSize)

        for danger in dangers:
            print(danger[2][0], danger[2][1])
            img = cv2.putText(img, str(danger[0]) + ' ' + str(danger[1]) + ' danger',
                              (int(danger[2][0]), int(danger[2][1])),
                              cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 255), 1)

        if img is not None:
            pil_img = Image.fromarray(img)
            buff = io.BytesIO()
            pil_img.save(buff, format="JPEG")
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buff.getvalue() + b'\r\n')
        else:
            return None


@app.route('/detect')
def detect():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_detect(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/raw_video_feed')
def raw_video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    frame = currentFrame
    pil_img = Image.fromarray(frame)
    buff = io.BytesIO()
    pil_img.save(buff, format="JPEG")
    encoded_img = base64.encodebytes(buff.getvalue()).decode('utf-8')
    response = {'Status': 'Success', 'message': '', 'ImageBytes': encoded_img}
    return flask.jsonify(response)


@app.route('/save_image', methods=['POST'])
def save_image():
    frame = currentFrame
    img_name = 'frame_' + time.strftime('%Y%m%d-%H%M%S') + '.jpg'
    img_path = os.path.join(app.root_path, 'saved_images', img_name)
    cv2.imwrite(img_path, frame)
    print('Saved image as: ' + img_name, file=sys.stderr)
    data = {'message': 'Image saved', 'code': 'SUCCESS'}
    return flask.make_response(flask.jsonify(data), 200)


@app.route('/save_clip', methods=['POST'])
def save_clip():
    capture_duration = 20
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    clip_name = 'clip_' + time.strftime('%Y%m%d-%H%M%S') + '.avi'
    clip_path = os.path.join(app.root_path, 'saved_clips', clip_name)
    frame_shape = np.shape(currentFrame)
    print('Saving clip with shape: ', frame_shape, file=sys.stderr)
    out = cv2.VideoWriter(clip_path, fourcc, 20.0, (frame_shape[0], frame_shape[1]))
    start_time = time.time()
    while int(time.time() - start_time) < capture_duration:
        frame = currentFrame
        if frame is not None:
            out.write(frame)
        else:
            break
    out.release()
    print('Saved clip as: ' + clip_path, file=sys.stderr)
    data = {'message': 'Clip saved', 'code': 'SUCCESS'}
    return flask.make_response(flask.jsonify(data), 200)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
