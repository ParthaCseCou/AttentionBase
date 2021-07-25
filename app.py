from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import csv
import time

from gaze_tracking import GazeTracking
app = Flask(__name__)

 # use 0 for web camera
# attention_level = []
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

#
# def put_current_level(x):
#     global attention_level
#     curent = time.time()
#     attention_level.append((curent, x))
#     x = attention_level[0]
#     y = attention_level[-1]
#     if y[0] - x[0] > 20.00:
#         attention_level.pop(0)
#
#     sum = 0
#     for attention in attention_level:
#         sum += attention[1]
#
#     return sum

web_cam, external = None, None
camera1 = cv2.VideoCapture(0)
camera2 = cv2.VideoCapture(0)
current = [time.time(), time.time()]
initial = [time.time(), time.time()]
result = [
    [['time', 'movement', 'attention_level', 'head movement']],
    [['time', 'movement', 'attention_level', 'head movement']],
]


def write_csv(rows, filename):
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def attention(x):
    if x >= 7:
        return 'high'
    elif x >= 4:
        return 'average'
    else:
        return 'low'


def gen_frames(camera_no):  # generate frame by frame from camera

    if camera_no == 'webcam':
        camera = camera1
        ind = 0
    else:
        camera = camera2
        ind = 1

    gaze = GazeTracking()
    print('hugammara sara')
    global result

    cnt, head_movement_count = 0, 0
    last, last_head = None, 'left'
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            gaze.refresh(frame)
            frame = gaze.annotated_frame()
            text = ""
            if gaze.is_blinking():
                text = "Blinking"
                last = text
            elif gaze.is_right():
                text = "Looking right"
                if text != last:
                    cnt += 1
                last = text
            elif gaze.is_left():
                text = "Looking left"
                if text != last:
                    cnt += 1
                last = text
            elif gaze.is_center():
                text = "Looking center"
                last = text

            if gaze.is_head_center():
                head_text = "Head on Center"
            elif gaze.is_head_left():
                head_text = "Head on left"
                if last_head == 'right':
                    last_head = 'left'
                    head_movement_count += 1
            else:
                head_text = "Head on right side"
                if last_head == 'left':
                    last_head = 'right'
                    head_movement_count += 1

            now = time.time()
            if now - current[ind] >= 20.0:
                result[ind].append([now - initial[ind], cnt, attention(cnt//2), head_movement_count])
                current[ind] = now
                cnt, head_movement_count = 0, 0

            cv2.putText(frame, text, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 1)
            cv2.putText(frame, head_text, (20, 70), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 1)
            left_pupil = gaze.pupil_left_coords()
            right_pupil = gaze.pupil_right_coords()
            cv2.putText(frame, "Left pupil:  " + str(left_pupil), (20, 110), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                        (0, 0, 255), 1)
            cv2.putText(frame, "Right pupil: " + str(right_pupil), (20, 150), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                        (0, 0, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    camera = request.args.get('camera', default='webcam')
    return Response(gen_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    camera = request.args.get('camera', default=None)
    return render_template('index.html', camera=camera)


@app.route('/get/camera/', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def get_camera():
    if request.method == 'POST':
        camera = request.form.get('camera')
        return redirect(url_for('index', camera=camera))


@app.route('/stop/camera/')
def stop_camera():
    return redirect(url_for('index'))


@app.route('/generate/csv/')
def generate_csv():
    camera = request.args.get('camera', default=None)
    global result
    now = str(time.time()).replace('.', '')
    if camera == 'webcam':
        write_csv(result[0], f'{now}_webcam.csv')
    else:
        write_csv(result[1], f'{now}_external_usb.csv')
    return redirect(url_for('index', camera=camera))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
