from flask import Flask, jsonify, render_template, Response
import cv2 
import mediapipe as mp 
import numpy as np

app = Flask(__name__)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Predefined angles for corrections (you may define your own values)
angles = {'le': 169.8,
 're': 168.97,
 'lal': 174.19,
 'ral': 179.88,
 'lb': 179.86,
 'rb': 130.25,
 'lk': 179.75,
 'rk': 40.47}
feedback = {'le': "Nil",
 're': "Nil",
 'lal': "Nil",
 'ral': "Nil",
 'lb': "Nil",
 'rb': "Nil",
 'lk': "Nil",
 'rk': "Nil"}
Score = 0

def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Mid point
    c = np.array(c)  # End point
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def generate_frames():
    global Score
    global feedback
    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            score = 0
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark

                # Coordinates
                l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                r_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                r_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                r_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                r_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                # Calculate angles
                vid_le = calculate_angle(l_shoulder, l_elbow, l_wrist)
                vid_re = calculate_angle(r_shoulder, r_elbow, r_wrist)
                vid_lal = calculate_angle(l_elbow, l_shoulder, l_hip)
                vid_ral = calculate_angle(r_elbow, r_shoulder, r_hip)
                vid_lb = calculate_angle(l_shoulder, l_hip, l_knee)
                vid_rb = calculate_angle(r_shoulder, r_hip, r_knee)
                vid_lk = calculate_angle(l_hip, l_knee, l_ankle)
                vid_rk = calculate_angle(r_hip, r_knee, r_ankle)

                # Check for corrections and display feedback
                if(vid_re > angles['re']+10) :
                    feedback['re']="BEND MORE"
                    # cv2.putText(image, "RIGHT ELBOW : BEND MORE", (40,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                elif(vid_re < angles['re']-10) :
                    feedback['re']="BENT TOO MUCH"
                    # cv2.putText(image, "RIGHT ELBOW : BENT TOO MUCH", (40,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                else :
                    feedback['re']="CORRECT!!!"
                    # cv2.putText(image, "RIGHT : CORRECT!!!", (40,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    score += 1
                
                if(vid_le > angles['le']+10) :
                    feedback['le']="BEND MORE"
                    # cv2.putText(image, "LEFT ELBOW : BEND MORE", (40,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                elif(vid_le < angles['le']-10) :
                    feedback['le']="BENT TOO MUCH"
                    # cv2.putText(image, "LEFT ELBOW : BENT TOO MUCH", (40,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                else :
                    feedback['le']="CORRECT!!!"
                    # cv2.putText(image, "LEFT ARM : CORRECT!!!", (40,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    score += 1
                
                if(vid_lal > angles['lal']+10) :
                    feedback['lal']="LIFT HIGHER"
                    # cv2.putText(image, "LEFT ARM : LIFT HIGHER", (40,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                elif(vid_lal < angles['lal']-10) :
                    feedback['lal']="LIFTED TOO MUCH"
                    # cv2.putText(image, "LEFT ARM : LIFTED TOO MUCH", (40,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                else :
                    feedback['lal']="CORRECT!!!"
                    # cv2.putText(image, "LEFT SIDE : CORRECT!!!", (40,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    score += 1
                
                if(vid_ral > angles['ral']+10) :
                    feedback['ral']="LIFT HIGHER"
                    # cv2.putText(image, "RIGHT ARM : LIFT HIGHER", (40,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                elif(vid_ral < angles['ral']-10) :
                    feedback['ral']="LIFTED TOO MUCH"
                    # cv2.putText(image, "RIGHT ARM : LIFTED TOO MUCH", (40,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                else :
                    feedback['ral']="CORRECT!!!"
                    # cv2.putText(image, "RIGHT SIDE : CORRECT!!!", (40,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    score += 1
                
                if(vid_lb > angles['lb']+20) :
                    feedback['lb']="BEND MORE"
                    # cv2.putText(image, "LEFT SIDE : BEND MORE", (40,120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                elif(vid_lb < angles['lb']-20) :
                    feedback['lb']="BENT TOO MUCH"
                    # cv2.putText(image, "LEFT SIDE : BENT TOO MUCH", (40,120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                else :
                    feedback['lb']="CORRECT!!!"
                    # cv2.putText(image, "LEFT SIDE : CORRECT!!!", (40,120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    score += 1
                
                if(vid_rb > angles['rb']+20) :
                    feedback['rb']="BEND MORE"
                    # cv2.putText(image, "RIGHT SIDE : BEND MORE", (40,140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                elif(vid_rb < angles['rb']-20) :
                    feedback['rb']="BENT TOO MUCH"
                    # cv2.putText(image, "RIGHT SIDE : BENT TOO MUCH", (40,140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                else :
                    feedback['rb']="CORRECT!!!"
                    # cv2.putText(image, "RIGHT SIDE : CORRECT!!!", (40,140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    score += 1

                if(vid_lk > angles['lk']+20) :
                    feedback['lk']="BEND MORE"
                    # cv2.putText(image, "LEFT KNEE : BEND MORE", (40,160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                elif(vid_lk < angles['lk']-20) :
                    feedback['lk']="BENT TOO MUCH"
                    # cv2.putText(image, "LEFT KNEE : BENT TOO MUCH", (40,160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                else :
                    feedback['lk']="CORRECT!!!"
                    # cv2.putText(image, "LEFT KNEE : CORRECT!!!", (40,160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    score += 1
                
                if(vid_rk > angles['rk']+15) :
                    feedback['rk']="BEND MORE"
                    # cv2.putText(image, "RIGHT KNEE : BEND MORE", (40,180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                elif(vid_rk < angles['rk']-15) :
                    feedback['rk']="BENT TOO MUCH"
                    # cv2.putText(image, "RGIHT KNEE : BENT TOO MUCH", (40,180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (5, 5, 255), 2, cv2.LINE_AA)
                else :
                    feedback['rk']="CORRECT!!!"
                    # cv2.putText(image, "RIGHT KNEE : CORRECT!!!", (40,180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    score += 1  
                if(score>=6):
                    font_size=0.7
                    bgr=(0,150,0)
                else:
                    font_size=0.5
                    bgr=(255,5,5)
                score=score*12.5
                Score = score
                # cv2.putText(image, "SCORE:  " + str(score)+"/100", (40,300), cv2.FONT_HERSHEY_SIMPLEX, font_size, bgr, 2, cv2.LINE_AA) 

            except:
                pass

            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            _, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')  # HTML page to show the video feed

@app.route('/video_page')
def video_page():
    return render_template('home.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/getScore')
def getScore():
    global Score
    global feedback
    return jsonify({'score':Score,'feedback':feedback})

if __name__ == "__main__":
    app.run(debug=True)
