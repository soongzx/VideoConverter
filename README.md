# 功能说明
该脚本监控指定目录中的视频文件，当检测到新视频文件创建或修改时，自动将其转换为 MP4 格式。适用于需要自动转换视频格式的场景。

# HandBrake 视频转码服务

## 依赖项
请先安装以下Python包：
```bash
pip install watchdog pywin32
```

## 使用方式

1. 确保已正确配置 `config.ini` 文件
2. 确保 HandBrakeCLI.exe 已正确安装

### 命令行参数

- `python video_converter.py start` - 在前台启动监视服务
- `python video_converter.py install` - 安装为Windows服务
- `python video_converter.py remove` - 移除Windows服务
- `python video_converter.py stop` - 停止服务

### 配置文件说明

config.ini 包含以下配置项：

- watch_dir: 监视目录路径
- output_dir: 输出目录路径
- cli_path: HandBrakeCLI.exe 路径
- preset: HandBrake预设配置
- python_path: Python解释器路径

## 注意事项

1. 请确保所有目录路径都存在并且有正确的读写权限
2. 服务安装需要管理员权限
3. 日志信息会在命令行窗口显示

### 使用方式

使用 start_service.bat 来运行服务：
- `start_service.bat start` - 在前台启动监视服务
- `start_service.bat install` - 安装为Windows服务
- `start_service.bat remove` - 移除Windows服务
- `start_service.bat stop` - 停止服务

### 服务管理说明

1. 以管理员身份运行命令提示符
2. 进入程序目录
3. 使用以下命令：

```bash
# 安装服务
start_service.bat install

# 启动服务（前台模式）
start_service.bat start

# 移除服务
start_service.bat remove

# 停止服务
start_service.bat stop
```

注意：安装和移除服务时必须以管理员身份运行命令提示符。

## 常见问题解决

1. 如果遇到权限问题：
   - 右键点击 start_service.bat
   - 选择"以管理员身份运行"

2. 如果服务安装失败：
   - 确保以管理员身份运行
   - 检查 Python 路径是否正确
   - 检查所有依赖包是否已安装
# VideoConverter
