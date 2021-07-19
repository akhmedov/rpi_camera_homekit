import cv2
import time
import numpy as np
import mediapipe
from video_cap_async import VideoCaptureAsync

# run this in screen on RPi
# nohup raspivid -n -t 0 -w 640 -h 480 -rot 90 -hf -fps 30 -ih -fl -l -o - | nc -klvp 8081

# TODO: investigate UDP version of video server
# https://stackoverflow.com/questions/8309648/netcat-streaming-using-udp


def camera_parapeters():
    CAM_MTX = np.array([
        [1.53198867e+03, 0.00000000e+00, 7.09029855e+02],
        [0.00000000e+00, 1.53682876e+03, 5.43370205e+02],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    CAM_DIST = np.array([[0.17672693, -0.26866987, -0.00047228, -0.00544706,  0.0010136]])
    CAM_NEWMAT = np.array([[
        1.56913562e+03, 0.00000000e+00, 7.03693738e+02],
        [0.00000000e+00 ,1.56180469e+03, 5.42527490e+02],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    CAM_DATA_TABELD = {
        'focal_length_mm' : None,
        'matrix' : CAM_MTX,
        'dist' : CAM_DIST,
        'new_matrix' : CAM_NEWMAT,
        'focal_length_mm_datasheet' : [3.04, 3.04], 
        'sensor_res_px' : [3280, 2464], 
        'sensor_res_mm' : [3.68, 2.76],
        'f-stop' : 2.0, 
        'mount_height_m' : 0.845,
        'horizon_height_fromtop_proc_px' : 585,
        'name' : 'Rarpberry PI V2 NoIR'}
    fx_mm = CAM_NEWMAT[0][0] * CAM_DATA_TABELD['sensor_res_mm'][0] / CAM_DATA_TABELD['sensor_res_px'][0]
    fy_mm = CAM_NEWMAT[1][1] * CAM_DATA_TABELD['sensor_res_mm'][1] / CAM_DATA_TABELD['sensor_res_px'][1]
    print('Estimated focal length:', fy_mm)
    CAM_DATA_TABELD['focal_length_mm'] = [fx_mm, fy_mm]
    return CAM_DATA_TABELD


def drpth_height_estim(focal_length, obj_height, horizon, img_height, cam_height, sensor_height):
    dist = focal_length * cam_height * img_height / ((obj_height-horizon) * sensor_height)
    hgt = obj_height * dist * sensor_height / (focal_length * img_height)
    return dist, hgt


def person_bounding_box(pose, image_shape, hight_bias=0.05):
        keypoints_y = []
        keypoints_x = []
        for data_point in pose.landmark:
            keypoints_x.append(data_point.x)
            keypoints_y.append(data_point.y)
        top = int(image_shape[1] * min(keypoints_y))
        bot = int(image_shape[1] * max(keypoints_y))
        left = int(image_shape[0] * min(keypoints_x))
        right = int(image_shape[0] * max(keypoints_x))
        top -= int(hight_bias * (bot - top))
        return (left, bot), (right, top)


DISTANCE_QUEUE_LEN = 10

SOURCE_VIDEO_STREAM = 'tcp://192.168.31.106:8081'
DISPLAY_RES_SCALE = 1
PROC_RES_SCALE = 1
CAM_PARAM = camera_parapeters()
print(CAM_PARAM)

mpDraw = mediapipe.solutions.drawing_utils
mpPose = mediapipe.solutions.pose
pose = mpPose.Pose()

# tcp stream must handle frames one by one so we need to "skip" them 
# during the proccessing piplene to prevent "freezing"
cap = VideoCaptureAsync(SOURCE_VIDEO_STREAM)
cap_shape = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
proc_shape = int(PROC_RES_SCALE * cap_shape[0]), int(PROC_RES_SCALE * cap_shape[1])
disp_shape = int(DISPLAY_RES_SCALE * cap_shape[0]), int(DISPLAY_RES_SCALE * cap_shape[1])
print('Caption frame shape:', cap_shape)
print('Proccessing frame shape:', proc_shape)
print('Display frame shape:', disp_shape)


mapx, mapy = cv2.initUndistortRectifyMap(CAM_PARAM['matrix'], CAM_PARAM['dist'], None, CAM_PARAM['new_matrix'], cap_shape, 5)

# mesure and compare capture and record runtime to define FPS
# out = cv2.VideoWriter('./capture.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 5, disp_shape)

distance = list()
distance_avarage = 0.0

hight = list()
hight_avarage = 0.0

prev_frame_time = 0
new_frame_time = 0

while cap.isOpened():

    _, frame_bgr = cap.read()
    frame_bgr = cv2.remap(frame_bgr, mapx, mapy, cv2.INTER_LINEAR)
    frame_bgr = cv2.resize(frame_bgr, proc_shape)

    horizon1 = 0, CAM_PARAM['horizon_height_fromtop_proc_px']
    horizon2 = proc_shape[0], CAM_PARAM['horizon_height_fromtop_proc_px']
    cv2.line(frame_bgr, horizon1, horizon2, (255, 255, 0), thickness=2) # horizon

    dist = 0
    hgt = 0
    skeleton_model = pose.process(frame_bgr)
    if skeleton_model.pose_landmarks:
        mpDraw.draw_landmarks(frame_bgr, skeleton_model.pose_landmarks, mpPose.POSE_CONNECTIONS)
        pt1, pt2 = person_bounding_box(skeleton_model.pose_landmarks, proc_shape)
        frame_bgr = cv2.rectangle(frame_bgr, pt1, pt2, (255, 255, 0), thickness=2)

        obj_h_px = pt1[1] - CAM_PARAM['horizon_height_fromtop_proc_px']
        dist = 2.2 * CAM_PARAM['focal_length_mm'][1] * CAM_PARAM['mount_height_m'] * proc_shape[1] / (obj_h_px * CAM_PARAM['sensor_res_mm'][1])
        hgt = CAM_PARAM['mount_height_m'] * (pt1[1] - pt2[1]) / (CAM_PARAM['horizon_height_fromtop_proc_px'])
        distance.append(dist)
        hight.append(hgt)
    else:
        distance.append(0)
        hight.append(0)

    # try:
    #     faces, boxes, scores, landmarks = face_detector.detect_align(frame_bgr)
    #     genders, ages = age_gender_detector.detect(faces)
    #     for i in range(len(boxes)):
    #         bbox = boxes[i].cpu().detach().numpy().astype('int64')
    #         motion_mask = cv2.rectangle(motion_mask, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (36, 255, 12), 1)
    #         cv2.putText(motion_mask, f'{genders[i]}, {ages[i]}', (int(bbox[0]), int(bbox[1] - 1)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
    # except:
    #     pass


    if len(distance) > DISTANCE_QUEUE_LEN:
        distance_avarage = sum(distance) / len(distance)
        distance_avarage = round(distance_avarage, 2)
        distance = list()
        hight_avarage = sum(hight) / len(hight)
        hight_avarage = round(hight_avarage, 2)
        hight = list()

    new_frame_time = time.time()
    fps = str(int(1/(new_frame_time-prev_frame_time)))
    prev_frame_time = new_frame_time
    cv2.putText(frame_bgr, 'FPS: ' + fps, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 0), 3, cv2.LINE_AA)
    dist_text = str(distance_avarage) if distance_avarage > 0 else str(0.0)
    cv2.putText(frame_bgr, 'DST: ' + dist_text, (7, 140), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 0), 3, cv2.LINE_AA)
    cv2.putText(frame_bgr, 'HGT: ' + str(hight_avarage), (7, 210), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 0), 3, cv2.LINE_AA)

    frame_bgr = cv2.resize(frame_bgr, disp_shape)
    # out.write(frame_bgr)
    cv2.imshow('image', frame_bgr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
# out.release()
cv2.destroyAllWindows()
