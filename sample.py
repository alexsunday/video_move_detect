#!/usr/bin/env python
# encoding: utf-8
'''
Created on 2015年3月23日

@author: Sunday
'''
import sys
import copy
import time
import datetime

import cv2

GL_TIME = 0


def warnning(frame):
    global GL_TIME
    curstamp = time.time()
    if curstamp - GL_TIME < 30:
        print u'10秒内重复告警将忽略'
        return None
    GL_TIME = curstamp
    timestamp = datetime.datetime.now()
    fname = '%s.png' % timestamp.strftime("%Y%m%d%H%M%S")
    cv2.imwrite(fname, frame)
    print u'[%s] 告警, 已截图 => %s' % (timestamp.strftime("%H:%M:%S"), fname)


def main():
    filename = sys.argv[1]
    CPOINT = 10000
    THRESHOLDFLAGS = cv2.cv.CV_THRESH_BINARY
    capture = cv2.VideoCapture()
    capture.open(filename)
    retval, frame1 = capture.read()
    status = 0

    if not retval:
        print u'Error on open VIDEO STREAM.'
        return sys.exit(1)
    print u'视频流连接成功'
    frame1_gray = cv2.cvtColor(frame1, cv2.cv.CV_BGR2GRAY)
    bg1, bg2, bg3 = None, None, None
    while True:
        flag, cur_frame = capture.read()
        if not flag:
            break
        c_f_gray = cv2.cvtColor(cur_frame, cv2.cv.CV_BGR2GRAY)
        c_f_diffed = cv2.absdiff(c_f_gray, frame1_gray)
        _, c_f_thred = cv2.threshold(c_f_diffed, 60, 1, THRESHOLDFLAGS)
        if status == 0 and cv2.countNonZero(c_f_thred) > CPOINT:
            bg1 = copy.deepcopy(c_f_diffed)
            status = 1
        elif status == 1 and cv2.countNonZero(c_f_thred) < CPOINT:
            warnning(cur_frame)
            status = 0
        elif status == 1 and cv2.countNonZero(c_f_thred) > CPOINT:
            bg2 = copy.deepcopy(c_f_diffed)
            f2_diffed = cv2.absdiff(bg1, bg2)
            _, f2_thred = cv2.threshold(f2_diffed, 20, 1, THRESHOLDFLAGS)
            if cv2.countNonZero(f2_thred) > 3000:
                warnning(cur_frame)
                status = 0
            else:
                status = 2
        elif status == 2 and cv2.countNonZero(c_f_thred) < CPOINT:
            warnning(cur_frame)
            status = 0
        elif status == 2 and cv2.countNonZero(c_f_thred) > 10000:
            bg3 = copy.deepcopy(c_f_diffed)
            f3_diffed = cv2.absdiff(bg2, bg3)
            _, f3_thred = cv2.threshold(f3_diffed, 20, 1, THRESHOLDFLAGS)
            if cv2.countNonZero(f3_thred) > 3000:
                warnning(cur_frame)
            else:
                del frame1_gray
                frame1_gray = c_f_gray
            status = 0


if __name__ == '__main__':
    main()
