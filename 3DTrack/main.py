# -*- coding: UTF-8 -*-

import json
import sys
import time
import traceback
from datetime import datetime
import numpy as np
import scipy as sp
# from typing_extensions import Self
from queue import Queue
from threading import Lock
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, QTime, QTimer 
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QTextCursor
from pip import main
import Ui_BelowScreen
import conf
from logger import get_logger
from hm_trans import HMTransThread
from ha_trans import HATransThread
from hp_trans import HPTransThread
from deal_ai import InferenceThread_tensorrt
from scipy.spatial.transform import Rotation as R
import math

X_OFFSET = 81.3  # mm
Y_OFFSET = 30.3 # mm
W_US = 225.9
H_US = 180
X_RATIO = 0.3  # mm/pixel
Y_RATIO = 0.3  # mm/pixel
PX = (W_US/2) # mm
PY = 0  # m


 
#取消gstreamer的功能
NO_GSTREAMER = 1

if NO_GSTREAMER:
    import gi
    gi.require_version('Gst', '1.0')
    gi.require_version('GstVideo', '1.0')
    from gi.repository import GObject, Gst, GstVideo
    Gst.init(sys.argv)
    #Using UDP packets with RTP depayloaders to implement RTP streaming.
    #It have five stream
    #gpu
    # sendPipeline = Gst.parse_launch("v4l2src ! video/x-raw,width=1024,height=768,format=YUY2,framerate=30/1 ! \
    #     videoconvert ! nvvideoconvert ! nvv4l2h264enc ! h264parse ! rtph264pay ! tee name=t ! \
    #     queue ! udpsink host=127.0.0.1 port=5022 t. ! \
    #     queue name=2 ! udpsink host=127.0.0.1 port=5023 t. ! \
    #     queue name=3 ! udpsink host=127.0.0.1 port=5024 t. ! \
    #     queue name=4 ! udpsink host=127.0.0.1 port=5025 t. ! \
    #     queue name=5 ! udpsink host=127.0.0.1 port=5026")
    #cpu
    sendPipeline = Gst.parse_launch("v4l2src ! video/x-raw,width=1024,height=768,format=YUY2,framerate=30/1 ! \
        videoconvert ! x264enc ! h264parse ! rtph264pay ! tee name=t ! \
        queue ! udpsink host=127.0.0.1 port=5022 t. ! \
        queue name=2 ! udpsink host=127.0.0.1 port=5023 t. ! \
        queue name=3 ! udpsink host=127.0.0.1 port=5024 t. ! \
        queue name=4 ! udpsink host=127.0.0.1 port=5025 t. ! \
        queue name=5 ! udpsink host=127.0.0.1 port=5026")
    sendPipeline.set_state(Gst.State.PLAYING)

logger = get_logger()
class BelowScreenApp(QMainWindow, Ui_BelowScreen.Ui_MainWindow):

    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.should_stop = False
        self.puncture_no_alarm = True
        self.robotic_arm_no_alarm = True
        self.need_adjust_angle_depth = False  # 穿刺角度深度调整FLAG
        self.ablation_started = False  # 消融开始FLAG
        self.ablation_minute = 0  # 已消融时间（分钟）
        self.ablation_second = 0  # 已消融时间（秒钟）

        self.goal_pose = [0.303038, 0.473325 ,0.299189, -0.111969, 0.0547583, 0.778852]
        self.registration_matrix = np.zeros(shape=(4,4))
        get_rotation = R.from_euler('zyx', [-0.111969, 0.0547583, 0.778852], degrees=False)
        self.goal_relmatrix = get_rotation.as_matrix()

        get_position = np.array([0.303038, 0.473325 ,0.299189]).reshape(3,1)
        self.goal_relmatrix = np.insert(self.goal_relmatrix,[3],get_position,axis=1)
        self.goal_relmatrix = np.insert(self.goal_relmatrix,[3],[0,0,0,1],axis=0)

        self.get_relmatrix_flag = False

        self.puncture_angle_postion = 10
        self.puncture_angle_speed = 0.07
        self.puncture_depth_postion = 10
        self.puncture_depth_speed = 0.07

        self.btnImportPlan.clicked.connect(self.btnImportPlan_clicked)
        self.btnStartSurgery.clicked.connect(self.btnStartSurgery_clicked)

        self.tabRegistAutoManual.currentChanged.connect(self.tabRegistAutoManual_currentChanged)
        self.btnScanRegistManual.clicked.connect(self.btnScanRegistManual_clicked)
        self.btnSetStartPoint.clicked.connect(self.btnSetStartPoint_clicked)
        self.btnSetEndPoint.clicked.connect(self.btnSetEndPoint_clicked)
        self.btnScanRegistAuto.clicked.connect(self.btnScanRegistAuto_clicked)
        self.btnClearRegist.clicked.connect(self.btnClearRegist_clicked)
        self.btnFinishRegist.clicked.connect(self.btnFinishRegist_clicked)

        self.btnAutoTrace.clicked.connect(self.btnAutoTrace_clicked)
        self.btnFinishTrace.clicked.connect(self.btnFinishTrace_clicked)
    
        self.btnMoveFrontEnd.clicked.connect(self.btnMoveFrontEnd_clicked)
        self.btnSetAblationTime.clicked.connect(self.btnSetAblationTime_clicked)
        self.btnStartAblation.clicked.connect(self.btnStartAblation_clicked)
        self.btnFinishSurgery.clicked.connect(self.btnFinishSurgery_clicked)

        self.btnSaveVideo.clicked.connect(self.btnSaveVideo_clicked)
        self.btnScreenshot.clicked.connect(self.btnScreenshot_clicked)

        self.btnQuitSystem.clicked.connect(self.btnQuitSystem_clicked)

        self.stcTitleArea.setCurrentIndex(0)
        self.stcVideoArea.setCurrentIndex(0)
        self.stcSystemInfoArea.setCurrentIndex(1)
        self.stcOperationArea.setCurrentIndex(0)
        self.tabRegistAutoManual.setCurrentIndex(0)

        self.pgsRegistProgress.setRange(0, 100)
        self.picSysRunSt.setStyleSheet("border-image:url(res/red_light.png)")
        self.picRoboticArmSt.setStyleSheet("border-image:url(res/red_light.png)")
        self.picPunctureSt.setStyleSheet("border-image:url(res/red_light.png)")
        self.picAlarmSt.setStyleSheet("border-image:url(res/red_light.png)")

        self.mplayer = QMediaPlayer() 
        self.mplayer.setVideoOutput(self.vidPlayVideo)

        # 初始化对嵌入式主板送受信模块
        self.app_req2M_queue = Queue()
        self.app_req2M_queue_lock = Lock()

        self.mother_board_data = {}
        self.mother_board_data["Timestamp"] = ""
        self.mother_board_data["ErrorCode"] = ""
        self.mother_board_data["Angle"] = 0.0
        self.mother_board_data["SpinSpeed"] = 0.0
        self.mother_board_data["AngleStatus"] = 0
        self.mother_board_data["Depth"] = 0.0
        self.mother_board_data["DrilSpeed"] = 0.0
        self.mother_board_data["DepthStatus"] = 0
        self.mother_board_data["PierceForce"] = 0.0
        self.mother_board_data["GyroX"] = 0.0
        self.mother_board_data["GyroY"] = 0.0
        self.mother_board_data["GyroZ"] = 0.0
        self.mother_board_data["AcceX"] = 0.0
        self.mother_board_data["AcceY"] = 0.0
        self.mother_board_data["AcceZ"] = 0.0
        self.mother_board_data["DmpX"] = 0.0
        self.mother_board_data["DmpY"] = 0.0
        self.mother_board_data["DmpZ"] = 0.0
        self.mother_board_data["TiltX"] = 0.0
        self.mother_board_data["TiltY"] = 0.0
        self.mother_board_data["TiltZ"] = 0.0
        self.mother_board_data_lock = Lock()

        self.mother_board_resp = {}
        for tele_code in conf.ANS_MH_TELE_CODES:
            self.mother_board_resp[tele_code] = {}
        self.mother_board_resp_lock = Lock()

        self.hm_trans_thread = HMTransThread(
            self.app_req2M_queue,
            self.app_req2M_queue_lock,
            self.mother_board_data,
            self.mother_board_data_lock,
            self.mother_board_resp,
            self.mother_board_resp_lock
        )
         
   
        self.stop_signal.connect(self.hm_trans_thread.stop_slot)
        self.hm_trans_thread.finished.connect(self.hm_trans_thread.deleteLater)
        self.hm_trans_thread.device_st_signal.connect(self.puncture_st_slot)
        self.hm_trans_thread.alarm_st_signal.connect(self.puncture_alarm_st_slot)
        self.hm_trans_thread.auto_trace_signal.connect(self.puncture_motor_auto_trace_slot)


        

        # 初始化对机械臂送受信模块
        self.app_req2A_queue = Queue()
        self.app_req2A_queue_lock = Lock()

        self.robotic_arm_data = {}
        self.robotic_arm_data["Timestamp"] = ""
        self.robotic_arm_data["ErrorCode"] = ""
        self.robotic_arm_data["ArmStatus"] = 0
        self.robotic_arm_data["RobotTime"] = 0.0
        self.robotic_arm_data["PoseX"] = 0.0
        self.robotic_arm_data["PoseY"] = 0.0
        self.robotic_arm_data["PoseZ"] = 0.0
        self.robotic_arm_data["PoseRX"] = 0.0
        self.robotic_arm_data["PoseRY"] = 0.0
        self.robotic_arm_data["PoseRZ"] = 0.0
        self.robotic_arm_data["ForceX"] = 0.0
        self.robotic_arm_data["ForceY"] = 0.0
        self.robotic_arm_data["ForceZ"] = 0.0
        self.robotic_arm_data["ForceRX"] = 0.0
        self.robotic_arm_data["ForceRY"] = 0.0
        self.robotic_arm_data["ForceRZ"] = 0.0
        self.robotic_arm_data["TaskID"] = 0
        self.robotic_arm_data["HighPoint"] = 0
        self.robotic_arm_data["FinishFlag"] = 0
        self.robotic_arm_data["Progress"] = 0.0
        self.robotic_arm_data["HandMode"] = 0
        self.robotic_arm_data_lock = Lock()

        self.robotic_arm_resp = {}
        for tele_code in conf.ANS_AH_TELE_CODES:
            self.robotic_arm_resp[tele_code] = {}
        self.robotic_arm_resp_lock = Lock()

        self.ha_trans_thread = HATransThread(
            self.app_req2A_queue,
            self.app_req2A_queue_lock,
            self.robotic_arm_data,
            self.robotic_arm_data_lock,
            self.robotic_arm_resp,
            self.robotic_arm_resp_lock
        )
        self.stop_signal.connect(self.ha_trans_thread.stop_slot)
        self.ha_trans_thread.finished.connect(self.ha_trans_thread.deleteLater)
        self.ha_trans_thread.device_st_signal.connect(self.robotic_arm_st_slot)
        self.ha_trans_thread.alarm_st_signal.connect(self.robotic_arm_alarm_st_slot)
        self.ha_trans_thread.auto_trace_signal.connect(self.robotic_arm_auto_trace_slot)
        self.ha_trans_thread.robot_fd_signal.connect(self.robot_matrix_get_slot)

        # 初始化对配准AI送受信模块
        self.app_req2P_queue = Queue()
        self.app_req2P_queue_lock = Lock()

        self.AI_R_data = {}
        self.AI_R_data["Timestamp"] = ""
        self.AI_R_data["ErrorCode"] = ""
        self.AI_R_data["Controlword"] = 0
        self.AI_R_data["StatusWord"] = 0.0
        self.AI_R_data["Progress"] = 0.0
        self.AI_R_data["Matrix"] = []
        self.AI_R_data["points"] = []
        self.AI_R_data_lock = Lock()

        self.AI_R_resp = {}
        for tele_code in conf.ANS_AH_TELE_CODES:
            self.AI_R_resp[tele_code] = {}
        self.AI_R_resp_lock = Lock()

        self.hp_trans_thread = HPTransThread(
            self.app_req2P_queue,
            self.app_req2P_queue_lock,
            self.AI_R_data,
            self.AI_R_data_lock,
            self.AI_R_resp,
            self.AI_R_resp_lock
        )
        self.stop_signal.connect(self.hp_trans_thread.stop_slot)
        self.hp_trans_thread.finished.connect(self.hp_trans_thread.deleteLater)
        # self.hp_trans_thread.device_st_signal.connect(self.robotic_arm_st_slot)
        # self.hp_trans_thread.alarm_st_signal.connect(self.robotic_arm_alarm_st_slot)
        # self.hp_trans_thread.auto_trace_signal.connect(self.robotic_arm_auto_trace_slot)
        self.hp_trans_thread.regist_progress_signal.connect(self.regist_progress_slot)
        self.hp_trans_thread.matrix_set_signal.connect(self.registration_matrix_slot)




        self.deal_ai_thread = InferenceThread_tensorrt()
        self.deal_ai_thread.predition_data_signal.connect(self.prediction_data_send_slot)


        if NO_GSTREAMER:
            # Create GStreamer pipeline
            self.pipeline = Gst.parse_launch("udpsrc port=5022 ! application/x-rtp,encoding-name=H264 ! \
                rtpjitterbuffer latency=0 ! rtph264depay ! avdec_h264 ! tee name=tee ! \
                queue name=videoqueue ! videoconvert ! ximagesink")

            # Create bus to get events from GStreamer pipeline
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect('message::eos', self.on_eos)
            bus.connect('message::error', self.on_error)

            # This is needed to make the video output in our DrawingArea:
            bus.enable_sync_message_emission()
            bus.connect('sync-message::element', self.on_sync_message)

            #get window id for video flow
            self.windowId = self.imgShowImage.winId() 

        # 刷新系统情报区域用计时器
        self.refresh_sysinfo_timer = QTimer(self)
        self.refresh_sysinfo_timer.setSingleShot(True)
        self.refresh_sysinfo_timer.setInterval(1000)
        self.refresh_sysinfo_timer.timeout.connect(self.refresh_sysinfo_slot)

        self.hm_trans_thread.start()
        self.ha_trans_thread.start()
        self.hp_trans_thread.start()
        self.deal_ai_thread.start()
        self.refresh_sysinfo_timer.start()

    def closeEvent(self, event):
        self.should_stop = True
        self.stop_signal.emit()
        logger.info("[BelowScreenApp] Waiting for work threads go to stop...")
        try:
            if self.hm_trans_thread.isRunning():
                self.hm_trans_thread.quit()
                self.hm_trans_thread.wait()
            if self.ha_trans_thread.isRunning():
                self.ha_trans_thread.quit()
                self.ha_trans_thread.wait()
            if self.hp_trans_thread.isRunning():
                self.hp_trans_thread.quit()
                self.hp_trans_thread.wait()
            if self.deal_ai_thread.isRunning():
                self.deal_ai_thread.quit()
                self.deal_ai_thread.wait()
            self.refresh_sysinfo_timer.stop() 
                 
            if NO_GSTREAMER:
                sendPipeline.set_state(Gst.State.NULL)
        except Exception:
            print(traceback.format_exc())

        logger.info("[BelowScreenApp] Good Bye!")
        # event.accept()
        super(BelowScreenApp, self).closeEvent(event)


    ########################################
    # gstreamer事件处理函数群
    ########################################


    def probe_block(self, pad, buf):
        print("blocked") 
        filequeue = self.recordpipe.get_by_name("filequeue")
        self.pipeline.get_by_name("tee").unlink(self.recordpipe)
        filequeue.get_static_pad("sink").send_event(Gst.Event.new_eos()) 
        return Gst.PadProbeReturn.REMOVE

    def setup_pipeline(self):

        self.state = Gst.State.NULL  

        # instruct the bus to emit signals for each received message
        # and connect to the interesting signals
        bus = self.pipeline.get_bus()

        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self.on_sync_message) 

    def start_pipeline(self):
        self.pipeline.set_state(Gst.State.PLAYING) 

    def btnSaveVideo_clicked(self):
        try:
            if self.btnSaveVideo.text() == "录像":
                filename = "videoData/" + datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".mp4"
                print(filename)
                # gpu incode
                # self.recordpipe = Gst.parse_bin_from_description("queue name=filequeue ! videoconvert ! nvvideoconvert ! video/x-raw(memory:NVMM),format=NV12 ! nvv4l2h264enc ! h264parse ! avimux ! filesink location=" + filename, True)
                # cpu incode
                self.recordpipe = Gst.parse_bin_from_description("queue name=filequeue ! x264enc ! \
                    h264parse ! avimux ! filesink location=" + filename, True)
                self.pipeline.add(self.recordpipe)
                self.pipeline.get_by_name("tee").link(self.recordpipe) 
                self.recordpipe.set_state(Gst.State.PLAYING)
                self.btnSaveVideo.setText("保存录像")
            else:
                filequeue = self.recordpipe.get_by_name("filequeue")
                filequeue.get_static_pad("src").add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.probe_block)
                print("Stopped recording")   
                self.btnSaveVideo.setText("录像")

        except Exception:
            print(traceback.format_exc())


    #set gstreamer video flow to window
    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            msg.src.set_window_handle(self.windowId)


    def on_eos(self, bus, msg):
        print('on_eos(): seeking to start of video')
        self.pipeline.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0
        )    

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())    


    def stop_saveImage(self, pad, buf):
        imagequeue = self.screenshot.get_by_name("imagequeue")
        self.pipeline.get_by_name("tee").unlink(self.screenshot)
        imagequeue.get_static_pad("sink").send_event(Gst.Event.new_eos()) 
        print("Stopped screemshot")
        return Gst.PadProbeReturn.REMOVE


    def btnScreenshot_clicked(self):
        filename = "imageData/" + datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".jpg"
        print(filename)
        self.screenshot = Gst.parse_bin_from_description("queue name=imagequeue ! jpegenc ! filesink location=" + filename, True)
        self.pipeline.add(self.screenshot) 
        self.pipeline.get_by_name("tee").link(self.screenshot)
        self.screenshot.set_state(Gst.State.PLAYING)  
        imagequeue = self.screenshot.get_by_name("imagequeue")
        imagequeue.get_static_pad("src").add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.stop_saveImage)
         
 
    ########################################
    # 按钮点击事件处理函数群
    ########################################
    # 退出
    def btnQuitSystem_clicked(self):
        try:
            self.close()
        except Exception:
            print(traceback.format_exc())

    # 导入规划
    def btnImportPlan_clicked(self):
        try:
            self.mplayer.setMedia(QMediaContent(QFileDialog.getOpenFileUrl()[0])) 
            self.stcVideoArea.setCurrentIndex(1)
            self.mplayer.play()
        except Exception:
            print(traceback.format_exc())

    # 开始手术
    def btnStartSurgery_clicked(self):
        try:
            # 机械臂启停控制要求
            sending_msg_map = self.make_sending_msg_map("06ES_R_HA")
            sending_msg_map["10ArmControl"] = 1  # 连接机械臂
            self.send2_robotic_arm(sending_msg_map)

            self.pgsRegistProgress.reset()
            self.stcVideoArea.setCurrentIndex(0)
            self.stcOperationArea.setCurrentIndex(1)
            self.stcSystemInfoArea.setCurrentIndex(0) 
            self.stcTitleArea.setCurrentIndex(1)
            self.get_relmatrix_flag = False
            if NO_GSTREAMER:
                self.setup_pipeline()
                self.start_pipeline()
        except Exception:
            print(traceback.format_exc())

    # 自动配准：Tab按钮
    def tabRegistAutoManual_currentChanged(self):
        try:
            if self.tabRegistAutoManual.currentIndex() == 1:
                # 通知机械臂解锁脚踏板
                sending_msg_map = self.make_sending_msg_map("14BT_N_HA")
                sending_msg_map["12ButtonEnable"] = 1
                self.send2_robotic_arm(sending_msg_map)
        except Exception:
            print(traceback.format_exc())

    # 自动配准：设置起点
    def btnSetStartPoint_clicked(self):
        try:
            # 通知机械臂设置起始点
            sending_msg_map = self.make_sending_msg_map("16AU_R_HA")
            sending_msg_map["44AutoFlag1"] = 1
            sending_msg_map["45AutoFlag2"] = 0
            sending_msg_map["46AutoFlag3"] = 0
            self.send2_robotic_arm(sending_msg_map)
        except Exception:
            print(traceback.format_exc())

    # 自动配准：设置终点
    def btnSetEndPoint_clicked(self):
        try:
            # 通知机械臂设置终点
            sending_msg_map = self.make_sending_msg_map("16AU_R_HA")
            sending_msg_map["44AutoFlag1"] = 0
            sending_msg_map["45AutoFlag2"] = 1
            sending_msg_map["46AutoFlag3"] = 0
            self.send2_robotic_arm(sending_msg_map)
        except Exception:
            print(traceback.format_exc())

    # 自动配准：扫描配准 / 停止扫描配准
    def btnScanRegistAuto_clicked(self):
        try:
            if self.btnScanRegistAuto.text() == "扫描配准":
                # 通知机械臂开始自动扫描
                sending_msg_map = self.make_sending_msg_map("16AU_R_HA")
                sending_msg_map["44AutoFlag1"] = 0
                sending_msg_map["45AutoFlag2"] = 0
                sending_msg_map["46AutoFlag3"] = 1
                self.send2_robotic_arm(sending_msg_map)
                self.btnScanRegistAuto.setText("停止扫描配准")
                self.pgsRegistProgress.reset()

                # 通知AI配准开始进行配准
                sending_msg_map = self.make_sending_msg_map("05CM_R_HP")
                sending_msg_map["10ControlWord"] = 1 # TODO
                self.send2_registration_program(sending_msg_map)

            else:
                # 要求机械臂启停止
                sending_msg_map = self.make_sending_msg_map("06ES_R_HA")
                sending_msg_map["10ArmControl"] = 2
                self.send2_robotic_arm(sending_msg_map)
                self.btnScanRegistAuto.setText("扫描配准")

        except Exception:
            print(traceback.format_exc())

    # 手动配准：扫描配准 / 停止扫描配准
    def btnScanRegistManual_clicked(self):
        try:
            if self.btnScanRegistManual.text() == "扫描配准":
                # 通知机械臂解锁脚踏板
                sending_msg_map = self.make_sending_msg_map("14BT_N_HA")
                sending_msg_map["12ButtonEnable"] = 1
                self.send2_robotic_arm(sending_msg_map)
                # 通知AI配准开始进行配准
                sending_msg_map = self.make_sending_msg_map("05CM_R_HP")
                sending_msg_map["10ControlWord"] = 1 # TODO
                self.send2_registration_program(sending_msg_map)

                self.btnScanRegistManual.setText("停止扫描配准")
                self.pgsRegistProgress.reset()

            else:
                # 通知机械臂锁定脚踏板
                sending_msg_map = self.make_sending_msg_map("14BT_N_HA")
                sending_msg_map["12ButtonEnable"] = 0
                self.send2_robotic_arm(sending_msg_map)
                self.btnScanRegistManual.setText("扫描配准")
        except Exception:
            print(traceback.format_exc())

    # 清空配准
    def btnClearRegist_clicked(self):
        try:
            # # 通知机械臂锁定脚踏板
            # sending_msg_map = self.make_sending_msg_map("14BT_N_HA")
            # sending_msg_map["12ButtonEnable"] = 0
            # self.send2_robotic_arm(sending_msg_map)

            # # 要求机械臂启停止
            # sending_msg_map = self.make_sending_msg_map("06ES_R_HA")
            # sending_msg_map["10ArmControl"] = 2
            # self.send2_robotic_arm(sending_msg_map)
            
            # 通知AI配准开始进行配准
            sending_msg_map = self.make_sending_msg_map("05CM_R_HP")
            sending_msg_map["10ControlWord"] = 3 # TODO
            self.send2_registration_program(sending_msg_map)

            self.pgsRegistProgress.reset()
        except Exception:
            print(traceback.format_exc())

    # 完成配准
    def btnFinishRegist_clicked(self):
        try:
            # 通知机械臂锁定脚踏板
            sending_msg_map = self.make_sending_msg_map("14BT_N_HA")
            sending_msg_map["12ButtonEnable"] = 0
            self.send2_robotic_arm(sending_msg_map)

            # 要求机械臂启停止
            sending_msg_map = self.make_sending_msg_map("06ES_R_HA")
            sending_msg_map["10ArmControl"] = 2
            self.send2_robotic_arm(sending_msg_map)

            # 通知AI配准开始进行配准
            sending_msg_map = self.make_sending_msg_map("05CM_R_HP")
            sending_msg_map["10ControlWord"] = 2 # TODO
            self.send2_registration_program(sending_msg_map)

            self.stcOperationArea.setCurrentIndex(2)
            self.txtAutoTraceInfo.setText("")
            self.stcSystemInfoArea.setCurrentIndex(1)
        except Exception:
            print(traceback.format_exc())

    # 自动寻迹
    def btnAutoTrace_clicked(self):
        try:
            # 机械臂移动要求
            sending_msg_map = self.make_sending_msg_map("08CM_R_HA")
            sending_msg_map["32ExpPoseX"] = self.Goal_pose[0] # TODO
            sending_msg_map["33ExpPoseY"] = self.Goal_pose[1] # TODO
            sending_msg_map["34ExpPoseZ"] = self.Goal_pose[2] # TODO
            sending_msg_map["35ExpPoseRX"] = self.Goal_pose[3] # TODO
            sending_msg_map["36ExpPoseRY"] = self.Goal_pose[4] # TODO
            sending_msg_map["37ExpPoseRZ"] = self.Goal_pose[5] # TODO
            self.send2_robotic_arm(sending_msg_map)

            self.show_auto_trace_info("门字形运动开始")
            self.need_adjust_angle_depth = True
            
        except Exception:
            print(traceback.format_exc())

    # 调整穿刺角度深度
    def adjust_angle_depth(self):
        try:
            # 穿刺角度调整要求，张开电机（希望在机械臂运动至高点时发送）
            sending_msg_map = self.make_sending_msg_map("05CA_R_HM")
            sending_msg_map["20AngleExp"] = self.puncture_angle_postion # TODO
            sending_msg_map["21SpinSpeedExp"] = self.puncture_angle_speed # TODO
            self.send2_mother_board(sending_msg_map)

            # 穿刺深度调整要求，张开电机（希望在机械臂运动至高点时发送）
            sending_msg_map = self.make_sending_msg_map("07CD_R_HM")
            sending_msg_map["22DepthExp"] = self.puncture_depth_postion # TODO
            sending_msg_map["23DrilSpeedExp"] = self.puncture_depth_speed # TODO
            self.send2_mother_board(sending_msg_map)

            self.show_auto_trace_info("调整穿刺针角度及深度")
            self.need_adjust_angle_depth = False
        except Exception:
            print(traceback.format_exc())

    # 完成寻迹
    def btnFinishTrace_clicked(self):
        try:
            self.need_adjust_angle_depth = False
            self.stcOperationArea.setCurrentIndex(3)
            self.lcdAblationTime.display("00:00")
            self.stcSystemInfoArea.setCurrentIndex(2)
        except Exception:
            print(traceback.format_exc())

    # 移开前端
    def btnMoveFrontEnd_clicked(self):
        try:
            # 通知机械臂解锁脚踏板
            sending_msg_map = self.make_sending_msg_map("14BT_N_HA")
            sending_msg_map["12ButtonEnable"] = 1
            self.send2_robotic_arm(sending_msg_map)

            # 穿刺角度调整要求, 收缩电机
            sending_msg_map = self.make_sending_msg_map("05CA_R_HM")
            sending_msg_map["20AngleExp"] = 0 # TODO
            sending_msg_map["21SpinSpeedExp"] = self.puncture_angle_speed # TODO
            self.send2_mother_board(sending_msg_map)

            # 穿刺深度调整要求，收缩电机
            sending_msg_map = self.make_sending_msg_map("07CD_R_HM")
            sending_msg_map["22DepthExp"] = 0 # TODO
            sending_msg_map["23DrilSpeedExp"] = self.puncture_depth_speed # TODO
            self.send2_mother_board(sending_msg_map)

        except Exception:
            print(traceback.format_exc())

    # 设置消融时间
    def btnSetAblationTime_clicked(self):
        try:
            pass
        except Exception:
            print(traceback.format_exc())

    # 开始消融
    def btnStartAblation_clicked(self):
        try:
            self.ablation_minute = 0
            self.ablation_second = 0
            self.ablation_started = True
        except Exception:
            print(traceback.format_exc())

    # 结束手术
    def btnFinishSurgery_clicked(self):
        try:
            self.ablation_started = False

            sending_msg_map = self.make_sending_msg_map("14BT_N_HA")
            sending_msg_map["12ButtonEnable"] = 0
            self.send2_robotic_arm(sending_msg_map)

            self.stcOperationArea.setCurrentIndex(0)
            self.txtAutoTraceInfo.setText("")
            self.stcSystemInfoArea.setCurrentIndex(1)
        except Exception:
            print(traceback.format_exc())

    ########################################
    # 刷新界面情报处理函数群
    ########################################
    def refresh_sysinfo_slot(self):
        try:
            # 系统运行状态灯
            if (self.hm_trans_thread.get_had_shakehands()
                and self.ha_trans_thread.get_had_shakehands()
                ):
                self.picSysRunSt.setStyleSheet("border-image:url(res/green_light.png)")
            else:
                self.picSysRunSt.setStyleSheet("border-image:url(res/red_light.png)")

            # 已消融时间
            if self.ablation_started:
                self.ablation_second = self.ablation_second + 1 
                if self.ablation_second == 60:
                    self.ablation_second = 0
                    self.ablation_minute = self.ablation_minute + 1 
                str_ablation_time = "{:0>2d}:{:0>2d}".format(
                    self.ablation_minute, self.ablation_second)
                self.lcdAblationTime.display(str_ablation_time)

        except Exception:
            print(traceback.format_exc())
        
        self.refresh_sysinfo_timer.start()

    # 机械臂状态灯
    def robotic_arm_st_slot(self, state):
        try:
            if state:
                self.picRoboticArmSt.setStyleSheet("border-image:url(res/green_light.png)")
            else:
                self.picRoboticArmSt.setStyleSheet("border-image:url(res/red_light.png)")
        except Exception:
            print(traceback.format_exc())

    # 穿刺前端状态灯
    def puncture_st_slot(self, state):
        try:
            if state:
                self.picPunctureSt.setStyleSheet("border-image:url(res/green_light.png)")
            else:
                self.picPunctureSt.setStyleSheet("border-image:url(res/red_light.png)")
        except Exception:
            print(traceback.format_exc())

    # 系统报警状态灯
    def puncture_alarm_st_slot(self, state):
        try:
            self.puncture_no_alarm = state
            self.refresh_alarm_state()
        except Exception:
            print(traceback.format_exc())

    def robotic_arm_alarm_st_slot(self, state):
        try:
            self.robotic_arm_no_alarm = state
            self.refresh_alarm_state()
        except Exception:
            print(traceback.format_exc())

    def refresh_alarm_state(self):
        if self.puncture_no_alarm and self.robotic_arm_no_alarm:
            self.picAlarmSt.setStyleSheet("border-image:url(res/green_light.png)")
        else:
            self.picAlarmSt.setStyleSheet("border-image:url(res/red_light.png)")

    # 机械臂运动信息栏
    def robotic_arm_auto_trace_slot(self, state):
        try:
            self.show_auto_trace_info(state)

            if self.need_adjust_angle_depth:
                if "到达最高点" in state:
                    self.adjust_angle_depth()
        except Exception:
            print(traceback.format_exc())

    # 穿刺前端电机运动信息栏
    def puncture_motor_auto_trace_slot(self, state):
        try:
            if "穿刺针角度及深度调整完成" in state:
                self.show_auto_trace_info(state)
        except Exception:
            print(traceback.format_exc())

    # 自动配准进度显示
    def regist_progress_slot(self, progress):
        try:
            if progress >= 0 and progress <= 100:
                self.pgsRegistProgress.setValue(progress)
        except Exception:
            print(traceback.format_exc())

    def registration_matrix_slot(self,list):
        try:
            self.relmatrix = np.array(list).reshape(4,4)
            self.get_relmatrix_flag = True

            self.goal_matrix = self.relmatrix * self.Goal_relmatrix
            relrotation = R.from_matrix(self.goal_matrix[0:3,0:3])
            self.goal_rotation = relrotation.as_euler('zyx')
            self.goal_postion = self.goal_matrix[0:3,3]

        except Exception:
            print(traceback.format_exc())

    def robot_matrix_get_slot(self,list):
        self.robot_matrix = np.zeros(shape=(4,4))
        get_rotation = R.from_euler('zyx', list[3:6], degrees=False)
        rotation_matrix = get_rotation.as_matrix()
        get_position = np.array(list[0:3]).reshape(3,1)
        self.robot_matrix = np.insert(rotation_matrix,[3],get_position,axis=1)
        self.robot_matrix = np.insert(self.robot_matrix,[3],[0,0,0,1],axis=0)


    def prediction_data_send_slot(self,list,timestamp):
        try:
            robot_points = self.getCoordinate(    self.goal_relmatrix, list,
                                                X_RATIO, Y_RATIO, X_OFFSET, Y_OFFSET,PX,PY
                                            )

            # 将AI推论数据发送到配准程序
            sending_msg_map = self.make_sending_msg_map("11SN_N_HP")
            sending_msg_map["16Points"] = robot_points # TODO
            self.send2_registration_program(sending_msg_map)

        except Exception:
            print(traceback.format_exc())


    ########################################
    # 工具类函数群
    ########################################
    @staticmethod
    def make_sending_msg_map(tele_code):
        sending_msg_map = {}
        sending_msg_map["01TeleCode"] = tele_code
        sending_msg_map["02Timestamp"] = ""
        sending_msg_map["03Sequence"] = 0
        sending_msg_map["04ErrorCode"] = "0x00000000"
        return sending_msg_map

    def send2_mother_board(self, sending_msg_map):
        try:
            self.app_req2M_queue_lock.acquire()
            self.app_req2M_queue.put(sending_msg_map)
        except Exception:
            pass
        finally:
            self.app_req2M_queue_lock.release()

    def send2_robotic_arm(self, sending_msg_map):
        try:
            self.app_req2A_queue_lock.acquire()
            self.app_req2A_queue.put(sending_msg_map)
        except Exception:
            pass
        finally:
            self.app_req2A_queue_lock.release()

    def send2_registration_program(self, sending_msg_map):
        try:
            self.app_req2P_queue_lock.acquire()
            self.app_req2P_queue.put(sending_msg_map)
        except Exception:
            pass
        finally:
            self.app_req2P_queue_lock.release()


    def show_auto_trace_info(self, info_str):
        self.txtAutoTraceInfo.append(info_str)
        self.txtAutoTraceInfo.moveCursor(QTextCursor.End)


    # def is_float(self, str):
    #     try:
    #         float(str)
    #         return True
    #     except Exception:
    #         return False

    def makePointsByMatrix(self,roll,pitch,yaw,ps):

        r = math.radians(roll)
        p = math.radians(pitch)
        y = math.radians(yaw) 

        x = math.cos(y)*math.cos(p)*ps[0][0] + (math.cos(y)*math.sin(p)*math.sin(r) - math.sin(y)*math.cos(r))*ps[0][1] + (math.cos(y)*math.sin(p)*math.cos(r) + math.sin(y)*math.sin(r))*ps[0][2]
        y = math.sin(y)*math.cos(p)*ps[0][0] + (math.sin(y)*math.sin(p)*math.sin(r)+math.cos(y)*math.cos(r))*ps[0][1] + (math.sin(y)*math.sin(p)*math.cos(r) - math.cos(y)*math.sin(r))*ps[0][2]
        z = -math.sin(p)*ps[0][0] + math.cos(p)*math.sin(r)*ps[0][1] + math.cos(p)*math.cos(r)*ps[0][2]
        return (x,y,z)

    def getCoordinate(self, matrix, ts, X_RATIO, Y_RATIO, X_OFFSET, Y_OFFSET, PX, PY):

        points = np.matrix(ts)
        points = points.T
        point_num = points.shape
        ratio_mat = np.matrix([[X_RATIO, 0],[0, Y_RATIO]])
        points = ratio_mat * points
        points[0,:] = points[0,:] - X_OFFSET -PX
        points[1,:] = PY - (points[1,:] - Y_OFFSET)
        points = np.insert(points,0,0,axis=0)
        points = np.insert(points,3,1,axis=0)

        robot_points = matrix*points

        robot_points = robot_points[0:3,:]
        robot_points = robot_points.T.tolist()

        return robot_points

        # X1 = []
        # Y1 = []
        # Z1 = []
        # for i, e in enumerate(ts): 
        #     px = x
        #     py = y
        #     pz = z
        #     x1 = (e[0][0] * X_RATIO - X_OFFSET)
        #     y1 = (e[0][1] * Y_RATIO - Y_OFFSET) 
        #     ps = []
        #     ps.append([0,x1 - PX,PY - y1])  
        #     px,py,pz = makePointsByMatrix(roll,pitch,yaw,ps)
        #     px = x + px
        #     py = y + py
        #     pz = z + pz
        #     X1.append(px)
        #     Y1.append(py)
        #     Z1.append(pz)
        # return X1, Y1, Z1


if __name__ == '__main__':
    logger.info("[BelowScreenApp] Hello!")
    if len(sys.argv) > 1:
        conf.MQTT_HOST = sys.argv[1]
    else:
        conf.MQTT_HOST = "10.7.1.16"

    logger.info("[BelowScreenApp] 指定的MQTT代理是[{}:{}]".format(
        conf.MQTT_HOST, conf.MQTT_PORT))

    app = QApplication(sys.argv)
    main = BelowScreenApp()
    main.showFullScreen()
    sys.exit(app.exec_())
