import os
import time
import sys
import configparser
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32serviceutil
import win32service
import win32event
import servicemanager
import logging
from threading import Timer

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(message)s',
                   datefmt='%Y-%m-%d %H:%M:%S')

class VideoHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.video_extensions = ('.wmv', '.avi', '.mkv', '.mov', '.mp4')
        self.timers = {}

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(self.video_extensions):
            self.schedule_conversion(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith(self.video_extensions):
            self.schedule_conversion(event.src_path)

    def schedule_conversion(self, video_path):
        if video_path in self.timers:
            self.timers[video_path].cancel()
        self.timers[video_path] = Timer(30, self.convert_video, [video_path])
        self.timers[video_path].start()

    def convert_video(self, video_path):
        output_path = os.path.join(
            self.config['Directories']['output_dir'],
            os.path.splitext(os.path.basename(video_path))[0] + '.mp4'
        )
        
        # 如果输出文件已存在，添加时间戳
        if os.path.exists(output_path):
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            timestamp = time.strftime("_%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.config['Directories']['output_dir'],
                f"{base_name}{timestamp}.mp4"
            )

        cmd = [
            self.config['HandBrake']['cli_path'],
            '-i', video_path,
            '-o', output_path,
            '--preset', self.config['HandBrake']['preset'],
            '-e', 'x264',  # 使用纯软件编码器
            '--encoder-preset', 'medium',  # 设置编码速度
            '--no-multi-pass',  # 单通道编码
            '--aencoder', 'av_aac'  # 音频编码器
        ]

        try:
            subprocess.run(cmd, check=True)
            logging.info(f"视频转换完成: {output_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"视频转换失败: {str(e)}")
        finally:
            if video_path in self.timers:
                del self.timers[video_path]

class HandBrakeService(win32serviceutil.ServiceFramework):
    _svc_name_ = "HandBrakeConverter"  # 更改服务名称
    _svc_display_name_ = "HandBrake Video Converter Service"  # 显示名称
    _svc_description_ = "自动监控并转换视频文件的服务"  # 添加服务描述
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.observer = None
        # 添加服务状态报告
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.observer:
            self.observer.stop()
        logging.info("服务停止中...")

    def SvcDoRun(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            logging.info("服务已启动")
            self.start_monitoring()
        except Exception as e:
            logging.error(f"服务运行错误: {str(e)}")
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def start_monitoring(self):
        try:
            config = self.load_config()
        except Exception as e:
            logging.error(f"配置加载失败: {str(e)}")
            return

        event_handler = VideoHandler(config)
        self.observer = Observer()
        self.observer.schedule(event_handler, config['Directories']['watch_dir'], recursive=False)
        self.observer.start()
        
        logging.info("监视服务已启动")
        try:
            while True:
                if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                    break
        except Exception as e:
            logging.error(f"服务错误: {str(e)}")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()

    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
        config.read(config_path)
        
        # 检查必要的目录是否存在
        watch_dir = config['Directories']['watch_dir']
        output_dir = config['Directories']['output_dir']
        
        if not os.path.exists(watch_dir):
            os.makedirs(watch_dir)
            logging.info(f"创建监视目录: {watch_dir}")
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"创建输出目录: {output_dir}")
            
        # 检查HandBrake路径
        if not os.path.exists(config['HandBrake']['cli_path']):
            raise FileNotFoundError(f"HandBrakeCLI.exe未找到: {config['HandBrake']['cli_path']}")
            
        return config

def start_monitoring():
    config = HandBrakeService.load_config()
    event_handler = VideoHandler(config)
    observer = Observer()
    observer.schedule(event_handler, config['Directories']['watch_dir'], recursive=False)
    observer.start()
    
    logging.info("监视服务已启动（前台模式）")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("监视服务已停止")
    observer.join()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            if sys.argv[1] == 'start':
                start_monitoring()
            else:
                win32serviceutil.HandleCommandLine(HandBrakeService)
        except Exception as e:
            logging.error(f"命令执行错误: {str(e)}")
            sys.exit(1)
    else:
        print("请使用参数: start, install, remove, 或 stop")
