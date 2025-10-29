import sys
import json
import threading
import copy
import math
from pathlib import Path
from functools import partial
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QListWidget, QSystemTrayIcon, QMenu, QMessageBox,
                             QDialog, QFormLayout, QSpinBox, QCheckBox, 
                             QListWidgetItem, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QComboBox, 
                             QSplitter, QGroupBox, QRadioButton, QButtonGroup,
                             QFileDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, pyqtSlot,QPoint
from PyQt5.QtGui import QIcon, QColor, QPixmap, QPainter, QLinearGradient, QFont,QRadialGradient,QPen, QBrush,QPainterPath,QPolygon
import paramiko
import socket
import select
import time
import webbrowser

# 状态更新信号类
class StatusSignal(QObject):
    """用于从线程发送状态更新信号到主线程"""
    status_changed = pyqtSignal(str, str)  # (status, error_msg)

# 翻译字典
TRANSLATIONS = {
    'en': {
        'window_title': 'SSH Tunnel Manager',
        'hosts': 'Hosts',
        'tunnels': 'Tunnels',
        'tunnel_configs': 'Tunnel Configurations',
        'active_tunnels': 'All Active Tunnels',
        'add_host': '➕ Add Host',
        'edit_host': '✏️ Edit Host',
        'copy_host': '📋 Copy Host',
        'delete_host': '❌ Delete Host',
        'add_tunnel': '➕ Add Tunnel',
        'edit_tunnel': '✏️ Edit Tunnel',
        'delete_tunnel': '❌ Delete Tunnel',
        'start_all': '▶️ Start All',
        'stop_all': '⏹️ Stop All',
        'minimize': '🔽 Minimize to Tray',
        'host_name': 'Host Name:',
        'server_ip': 'Server IP:',
        'ssh_port': 'SSH Port:',
        'username': 'Username:',
        'password': 'Password:',
        'use_key': 'Use SSH Key',
        'key_file': 'Key File:',
        'browse': 'Browse...',
        'local_port': 'Local Port:',
        'remote_host': 'Remote Host:',
        'remote_port': 'Remote Port:',
        'status': 'Status',
        'actions': 'Actions',
        'running': 'Running',
        'stopped': 'Stopped',
        'starting': 'Starting...',
        'reconnecting': 'Reconnecting...',
        'start': 'Start',
        'stop': 'Stop',
        'open_local': 'Open Local Page',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'confirm': 'Confirm',
        'save': 'Save',
        'cancel': 'Cancel',
        'host_saved': 'Host configuration saved!',
        'host_copied': 'Host copied! Please modify the name.',
        'tunnel_saved': 'Tunnel configuration saved!',
        'delete_confirm': 'Are you sure you want to delete "{}"?',
        'tunnel_started': 'Tunnel started successfully',
        'tunnel_stopped': 'Tunnel stopped',
        'connection_failed': 'Failed to connect to server',
        'please_select_host': 'Please select a host first',
        'please_fill_all': 'Please fill in all required fields',
        'port_in_use': 'Local port {} is already in use',
        'show_window': '📋 Show Window',
        'exit': '🚪 Exit',
        'running_in_tray': 'SSH Tunnel Manager is running in the system tray',
        'language': 'Language',
        'auto_restart': 'Auto restart dropped tunnels',
        'auto_restart_hint': 'Periodically check and restart tunnels that were closed by the remote host',
        'auth_method': 'Authentication Method:',
        'select_key_file': 'Select SSH Key File',
        'default_key_hint': 'Optional - leave empty to auto-detect keys in %USERPROFILE%\\.ssh\\',
    },
    'zh': {
        'window_title': 'SSH 隧道管理器',
        'hosts': '主机列表',
        'tunnels': '隧道列表',
        'tunnel_configs': '隧道配置',
        'active_tunnels': '所有活动隧道',
        'add_host': '➕ 添加主机',
        'edit_host': '✏️ 编辑主机',
        'copy_host': '📋 复制主机',
        'delete_host': '❌ 删除主机',
        'add_tunnel': '➕ 添加隧道',
        'edit_tunnel': '✏️ 编辑隧道',
        'delete_tunnel': '❌ 删除隧道',
        'start_all': '▶️ 全部启动',
        'stop_all': '⏹️ 全部停止',
        'minimize': '🔽 最小化到托盘',
        'host_name': '主机名称:',
        'server_ip': '服务器IP:',
        'ssh_port': 'SSH端口:',
        'username': '用户名:',
        'password': '密码:',
        'use_key': '使用SSH密钥',
        'key_file': '密钥文件:',
        'browse': '浏览...',
        'local_port': '本地端口:',
        'remote_host': '远程主机:',
        'remote_port': '远程端口:',
        'status': '状态',
        'actions': '操作',
        'running': '运行中',
        'stopped': '已停止',
        'starting': '启动中...',
        'start': '启动',
        'stop': '停止',
        'open_local': '打开本地网页',
        'success': '成功',
        'error': '错误',
        'warning': '警告',
        'confirm': '确认',
        'save': '保存',
        'cancel': '取消',
        'host_saved': '主机配置已保存！',
        'host_copied': '主机已复制！请修改主机名称。',
        'tunnel_saved': '隧道配置已保存！',
        'delete_confirm': '确定要删除 "{}" 吗？',
        'tunnel_started': '隧道启动成功',
        'tunnel_stopped': '隧道已停止',
        'connection_failed': '连接服务器失败',
        'please_select_host': '请先选择一个主机',
        'please_fill_all': '请填写所有必填字段',
        'port_in_use': '本地端口 {} 已被占用',
        'show_window': '📋 显示窗口',
        'exit': '🚪 退出',
        'running_in_tray': 'SSH隧道管理器正在系统托盘运行',
        'language': '语言',
        'auth_method': '认证方式:',
        'select_key_file': '选择SSH密钥文件',
        'default_key_hint': '可选 - 留空则自动检测 %USERPROFILE%\\.ssh\\ 目录下的密钥',
        'reconnecting': '重新连接中...',
        'auto_restart': '隧道断线自动重连',
        'auto_restart_hint': '每隔几秒检测隧道状态，若断开则自动重启',
    }
}


class TunnelThread(threading.Thread):
    def __init__(self, host_config, tunnel_config):
        super().__init__(daemon=True)
        self.host_config = host_config
        self.tunnel_config = tunnel_config
        self.signal = StatusSignal()
        self.running = False
        self.ssh_client = None
        self.transport = None
        self.server_socket = None
        self.keepalive_interval = 30  # seconds
        self.reconnect_delay = 3  # seconds
        self._current_status = None
        self._has_connected = False
        self.last_error = ''

    def _emit_status(self, status, error=''):
        if self._current_status == status and not error:
            return
        self._current_status = status
        self.signal.status_changed.emit(status, error)

    def _create_server_socket(self):
        local_port = self.tunnel_config['local_port']
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1', local_port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1)

    def _close_server_socket(self):
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None

    def _close_transport(self):
        if self.transport:
            try:
                self.transport.close()
            except Exception:
                pass
            self.transport = None
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except Exception:
                pass
            self.ssh_client = None

    def _connect_ssh(self):
        self._close_transport()
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            'hostname': self.host_config['server_ip'],
            'port': self.host_config['ssh_port'],
            'username': self.host_config['username'],
            'timeout': 10,
            'banner_timeout': 10,
            'auth_timeout': 10,
        }

        if self.host_config.get('use_key', False):
            key_file = self.host_config.get('key_file', '').strip()
            if key_file:
                connect_kwargs['key_filename'] = key_file
            else:
                default_keys = []
                ssh_dir = Path.home() / '.ssh'
                key_names = ['id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519']
                for key_name in key_names:
                    key_path = ssh_dir / key_name
                    if key_path.exists():
                        default_keys.append(str(key_path))
                if default_keys:
                    connect_kwargs['key_filename'] = default_keys
        else:
            password = self.host_config.get('password', '')
            if password:
                connect_kwargs['password'] = password

        self.ssh_client.connect(**connect_kwargs)
        self.transport = self.ssh_client.get_transport()
        if self.transport:
            self.transport.set_keepalive(self.keepalive_interval)

    def _ensure_transport(self):
        if self.transport and self.transport.is_active():
            return True

        if not self.running:
            return False

        if self._has_connected:
            self._emit_status('reconnecting', '')
        else:
            self._emit_status('starting', '')

        try:
            self._connect_ssh()
            self._has_connected = True
            self._emit_status('running', '')
            return True
        except Exception as exc:
            self.last_error = str(exc)
            print(f'SSH connect error: {exc}')
            time.sleep(self.reconnect_delay)
            return False

    def _handle_channel_error(self, error):
        if not self.running:
            return
        error_msg = str(error)
        self.last_error = error_msg
        print(f'Channel open error: {error_msg}')

        reset_indicators = ('10054', '10053', '10060', '10061', 'connection reset', 'Connection reset')
        if isinstance(error, paramiko.SSHException) or any(indicator in error_msg for indicator in reset_indicators):
            self._close_transport()
        time.sleep(1)

    def run(self):
        remote_host = self.tunnel_config.get('remote_host', '127.0.0.1')
        remote_port = self.tunnel_config['remote_port']
        self.running = True
        self._emit_status('starting', '')

        try:
            try:
                self._create_server_socket()
            except Exception as exc:
                self.last_error = str(exc)
                print(f'Failed to create local listener: {exc}')
                self._emit_status('error', str(exc))
                return

            while self.running:
                if not self._ensure_transport():
                    continue

                try:
                    client_socket, _ = self.server_socket.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if not self.running:
                        break
                    time.sleep(1)
                    continue
                except Exception as exc:
                    if self.running:
                        print(f'Accept error: {exc}')
                    time.sleep(1)
                    continue

                if not self.running:
                    client_socket.close()
                    break

                if not self.transport or not self.transport.is_active():
                    client_socket.close()
                    self._close_transport()
                    continue

                try:
                    channel = self.transport.open_channel(
                        'direct-tcpip',
                        (remote_host, remote_port),
                        client_socket.getpeername()
                    )
                except Exception as exc:
                    client_socket.close()
                    self._handle_channel_error(exc)
                    continue

                if channel is None:
                    client_socket.close()
                    continue

                threading.Thread(
                    target=self._forward_tunnel,
                    args=(client_socket, channel),
                    daemon=True
                ).start()
        finally:
            self.running = False
            self._close_transport()
            self._close_server_socket()
            self._emit_status('stopped', '')

    def _forward_tunnel(self, client_socket, channel):
        try:
            while True:
                readable, _, _ = select.select([client_socket, channel], [], [], 1)
                if client_socket in readable:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    channel.send(data)
                if channel in readable:
                    data = channel.recv(4096)
                    if not data:
                        break
                    client_socket.send(data)
        except Exception:
            pass
        finally:
            try:
                client_socket.close()
            except Exception:
                pass
            try:
                channel.close()
            except Exception:
                pass

    def is_connected(self):
        return self.transport is not None and self.transport.is_active()

    def stop(self):
        self.running = False
        self._close_transport()
        self._close_server_socket()

class HostDialog(QDialog):
    """主机配置对话框"""
    def __init__(self, parent, lang='zh', host_data=None):
        super().__init__(parent)
        self.lang = lang
        self.host_data = host_data or {}
        self.init_ui()
        
    def tr(self, key):
        return TRANSLATIONS[self.lang].get(key, key)
    
    def init_ui(self):
        self.setWindowTitle(self.tr('add_host') if not self.host_data else self.tr('edit_host'))
        self.setMinimumWidth(500)
        
        layout = QFormLayout(self)
        
        # 主机名称
        self.name_input = QLineEdit(self.host_data.get('name', ''))
        layout.addRow(self.tr('host_name'), self.name_input)
        
        # 服务器IP
        self.ip_input = QLineEdit(self.host_data.get('server_ip', ''))
        layout.addRow(self.tr('server_ip'), self.ip_input)
        
        # SSH端口
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self.host_data.get('ssh_port', 22))
        layout.addRow(self.tr('ssh_port'), self.port_input)
        
        # 用户名
        self.username_input = QLineEdit(self.host_data.get('username', ''))
        layout.addRow(self.tr('username'), self.username_input)
        
        # 认证方式
        auth_layout = QHBoxLayout()
        self.auth_group = QButtonGroup()
        self.password_radio = QRadioButton(self.tr('password'))
        self.key_radio = QRadioButton(self.tr('use_key'))
        self.auth_group.addButton(self.password_radio, 0)
        self.auth_group.addButton(self.key_radio, 1)
        auth_layout.addWidget(self.password_radio)
        auth_layout.addWidget(self.key_radio)
        auth_layout.addStretch()
        layout.addRow(self.tr('auth_method'), auth_layout)
        
        # 密码
        self.password_input = QLineEdit(self.host_data.get('password', ''))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow(self.tr('password'), self.password_input)
        
        # SSH密钥
        key_layout = QHBoxLayout()
        self.key_input = QLineEdit(self.host_data.get('key_file', ''))
        self.key_input.setPlaceholderText(self.tr('default_key_hint'))
        self.key_browse_btn = QPushButton(self.tr('browse'))
        self.key_browse_btn.clicked.connect(self.browse_key_file)
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(self.key_browse_btn)
        layout.addRow(self.tr('key_file'), key_layout)
        
        # 根据保存的认证方式设置默认选择
        use_key = self.host_data.get('use_key', False)
        if use_key:
            self.key_radio.setChecked(True)
        else:
            self.password_radio.setChecked(True)
        
        # 认证方式切换
        self.password_radio.toggled.connect(self.update_auth_fields)
        self.update_auth_fields()
        
        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(self.tr('save'))
        cancel_btn = QPushButton(self.tr('cancel'))
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
    
    def update_auth_fields(self):
        """更新认证字段的启用状态"""
        use_password = self.password_radio.isChecked()
        self.password_input.setEnabled(use_password)
        self.key_input.setEnabled(not use_password)
        self.key_browse_btn.setEnabled(not use_password)
    
    def browse_key_file(self):
        """浏览选择密钥文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('select_key_file'),
            str(Path.home() / '.ssh'),
            "All Files (*)"
        )
        if file_path:
            self.key_input.setText(file_path)
    
    def get_data(self):
        """获取输入数据"""
        key_file = self.key_input.text().strip()
        return {
            'name': self.name_input.text().strip(),
            'server_ip': self.ip_input.text().strip(),
            'ssh_port': self.port_input.value(),
            'username': self.username_input.text().strip(),
            'use_key': self.key_radio.isChecked(),
            'password': self.password_input.text() if self.password_radio.isChecked() else '',
            'key_file': key_file if self.key_radio.isChecked() else '',
        }


class TunnelDialog(QDialog):
    """隧道配置对话框"""
    def __init__(self, parent, lang='zh', tunnel_data=None):
        super().__init__(parent)
        self.lang = lang
        self.tunnel_data = tunnel_data or {}
        self.init_ui()
        
    def tr(self, key):
        return TRANSLATIONS[self.lang].get(key, key)
    
    def init_ui(self):
        self.setWindowTitle(self.tr('add_tunnel') if not self.tunnel_data else self.tr('edit_tunnel'))
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # 本地端口
        self.local_port_input = QSpinBox()
        self.local_port_input.setRange(1, 65535)
        self.local_port_input.setValue(self.tunnel_data.get('local_port', 8080))
        layout.addRow(self.tr('local_port'), self.local_port_input)
        
        # 远程主机
        self.remote_host_input = QLineEdit(self.tunnel_data.get('remote_host', '127.0.0.1'))
        layout.addRow(self.tr('remote_host'), self.remote_host_input)
        
        # 远程端口
        self.remote_port_input = QSpinBox()
        self.remote_port_input.setRange(1, 65535)
        self.remote_port_input.setValue(self.tunnel_data.get('remote_port', 80))
        layout.addRow(self.tr('remote_port'), self.remote_port_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(self.tr('save'))
        cancel_btn = QPushButton(self.tr('cancel'))
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
    
    def get_data(self):
        """获取输入数据"""
        return {
            'local_port': self.local_port_input.value(),
            'remote_host': self.remote_host_input.text().strip(),
            'remote_port': self.remote_port_input.value(),
        }


class SSHTunnelManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file = Path.home() / '.ssh_tunnel_manager_v2.json'
        self.hosts = []
        self.current_host = None
        self.tunnels = {}  # {tunnel_id: {'config': {}, 'thread': TunnelThread, 'status': 'running/stopped'}}
        self.lang = 'zh'  # 默认中文
        self.auto_restart_enabled = True
        self.monitor_interval_ms = 3000
        self.monitor_timer = None
        self.tray_start_action = None
        self.tray_stop_action = None
        
        self.load_config()
        self.init_ui()
        self.init_tray()
        self.start_monitor()
        
    def tr(self, key):
        """翻译函数"""
        return TRANSLATIONS[self.lang].get(key, key)
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(self.tr('window_title'))
        self.setGeometry(100, 100, 1200, 700)
        
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        # 语言选择
        lang_label = QLabel(self.tr('language') + ':')
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['中文', 'English'])
        self.lang_combo.setCurrentIndex(0 if self.lang == 'zh' else 1)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        
        toolbar.addWidget(lang_label)
        toolbar.addWidget(self.lang_combo)
        toolbar.addStretch()
        
        main_layout.addLayout(toolbar)
        
        # 上部分：主机列表和隧道配置（使用分割器）
        top_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：主机列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        host_group = QGroupBox(self.tr('hosts'))
        host_layout = QVBoxLayout(host_group)
        
        self.host_list = QListWidget()
        self.host_list.itemSelectionChanged.connect(self.on_host_selected)
        host_layout.addWidget(self.host_list)
        
        # 主机操作按钮
        host_btn_layout = QHBoxLayout()
        self.add_host_btn = QPushButton(self.tr('add_host'))
        self.edit_host_btn = QPushButton(self.tr('edit_host'))
        self.copy_host_btn = QPushButton(self.tr('copy_host'))
        self.delete_host_btn = QPushButton(self.tr('delete_host'))
        
        self.add_host_btn.clicked.connect(self.add_host)
        self.edit_host_btn.clicked.connect(self.edit_host)
        self.copy_host_btn.clicked.connect(self.copy_host)
        self.delete_host_btn.clicked.connect(self.delete_host)
        
        host_btn_layout.addWidget(self.add_host_btn)
        host_btn_layout.addWidget(self.edit_host_btn)
        host_btn_layout.addWidget(self.copy_host_btn)
        host_btn_layout.addWidget(self.delete_host_btn)
        host_layout.addLayout(host_btn_layout)
        
        left_layout.addWidget(host_group)
        
        # 右侧：当前主机的隧道配置
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        config_group = QGroupBox(self.tr('tunnel_configs'))
        config_layout = QVBoxLayout(config_group)
        
        # 隧道配置列表
        self.config_list = QListWidget()
        self.config_list.itemSelectionChanged.connect(self.on_tunnel_config_selected)
        config_layout.addWidget(self.config_list)
        
        # 隧道配置操作按钮
        config_btn_layout = QHBoxLayout()
        self.add_tunnel_btn = QPushButton(self.tr('add_tunnel'))
        self.edit_tunnel_btn = QPushButton(self.tr('edit_tunnel'))
        self.delete_tunnel_btn = QPushButton(self.tr('delete_tunnel'))
        
        self.add_tunnel_btn.clicked.connect(self.add_tunnel)
        self.edit_tunnel_btn.clicked.connect(self.edit_tunnel)
        self.delete_tunnel_btn.clicked.connect(self.delete_tunnel)
        
        # 初始禁用隧道操作按钮
        self.add_tunnel_btn.setEnabled(False)
        self.edit_tunnel_btn.setEnabled(False)
        self.delete_tunnel_btn.setEnabled(False)
        
        config_btn_layout.addWidget(self.add_tunnel_btn)
        config_btn_layout.addWidget(self.edit_tunnel_btn)
        config_btn_layout.addWidget(self.delete_tunnel_btn)
        config_layout.addLayout(config_btn_layout)
        
        right_layout.addWidget(config_group)
        
        # 添加到上部分割器
        top_splitter.addWidget(left_widget)
        top_splitter.addWidget(right_widget)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(top_splitter, stretch=1)
        
        # 下部分：活动隧道表格（全局视图）
        active_group = QGroupBox(self.tr('active_tunnels'))
        active_layout = QVBoxLayout(active_group)
        
        # 全局操作按钮
        global_btn_layout = QHBoxLayout()
        self.start_all_btn = QPushButton(self.tr('start_all'))
        self.stop_all_btn = QPushButton(self.tr('stop_all'))
        self.auto_restart_checkbox = QCheckBox(self.tr('auto_restart'))
        self.auto_restart_checkbox.setToolTip(self.tr('auto_restart_hint'))
        self.auto_restart_checkbox.setChecked(self.auto_restart_enabled)
        self.auto_restart_checkbox.stateChanged.connect(self.on_auto_restart_changed)
        self.minimize_btn = QPushButton(self.tr('minimize'))

        self.start_all_btn.clicked.connect(self.start_all_tunnels)
        self.stop_all_btn.clicked.connect(self.stop_all_tunnels)
        self.minimize_btn.clicked.connect(self.hide)

        global_btn_layout.addWidget(self.start_all_btn)
        global_btn_layout.addWidget(self.stop_all_btn)
        global_btn_layout.addWidget(self.auto_restart_checkbox)
        global_btn_layout.addStretch()
        global_btn_layout.addWidget(self.minimize_btn)
        active_layout.addLayout(global_btn_layout)

        # 活动隧道表格
        self.tunnel_table = QTableWidget()
        self.tunnel_table.setColumnCount(6)
        self.tunnel_table.setHorizontalHeaderLabels([
            self.tr('host_name'),
            self.tr('local_port'),
            self.tr('remote_host'),
            self.tr('remote_port'),
            self.tr('status'),
            self.tr('actions')
        ])
        self.tunnel_table.horizontalHeader().setStretchLastSection(True)
        self.tunnel_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tunnel_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        active_layout.addWidget(self.tunnel_table)
        
        main_layout.addWidget(active_group, stretch=1)
        
        # 加载主机列表和隧道表格
        self.refresh_host_list()
        self.refresh_tunnel_table()  # 立即加载所有隧道配置
    
    def init_tray(self):
        """初始化系统托盘"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.generate_tray_icon())

        tray_menu = QMenu()
        self.tray_start_action = tray_menu.addAction(self.tr('start_all'))
        self.tray_start_action.triggered.connect(self.tray_start_all)
        self.tray_stop_action = tray_menu.addAction(self.tr('stop_all'))
        self.tray_stop_action.triggered.connect(self.tray_stop_all)
        tray_menu.addSeparator()
        show_action = tray_menu.addAction(self.tr('show_window'))
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction(self.tr('exit'))
        exit_action.triggered.connect(self.quit_app)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()
        self.update_tray_actions()

    def generate_tray_icon(self):
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 简约深色背景
        painter.setBrush(QColor(20, 30, 50))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(2, 2, size - 4, size - 4, 12, 12)
        
        # 绘制连接线 - 从左侧到右侧的流动线条
        center_y = size // 2
        painter.setPen(QPen(QColor(0, 200, 255), 3))
        
        # 左侧起点（圆点）
        painter.setBrush(QColor(0, 200, 255))
        painter.drawEllipse(8, center_y - 3, 6, 6)
        
        # 右侧终点（圆点）
        painter.drawEllipse(size - 14, center_y - 3, 6, 6)
        
        # 连接线 - 带有流动感的曲线
        path = QPainterPath()
        path.moveTo(14, center_y)
        
        # 创建平滑的S形曲线，象征数据流动
        control1_x, control1_y = size // 3, center_y - 10
        control2_x, control2_y = 2 * size // 3, center_y + 10
        path.cubicTo(control1_x, control1_y, control2_x, control2_y, size - 20, center_y)
        
        painter.drawPath(path)
        
        # 在线条上添加几个小圆点表示数据传输
        dot_positions = [
            (size // 4, center_y - 5),
            (size // 2, center_y),
            (3 * size // 4, center_y + 5)
        ]
        
        painter.setBrush(QColor(100, 255, 255))
        for pos in dot_positions:
            painter.drawEllipse(int(pos[0]) - 2, int(pos[1]) - 2, 4, 4)
        
        painter.end()
        return QIcon(pixmap)
    def tray_start_all(self):
        if hasattr(self, 'auto_restart_checkbox') and self.auto_restart_checkbox is not None:
            self.auto_restart_enabled = self.auto_restart_checkbox.isChecked()
        self.start_all_tunnels()

    def tray_stop_all(self):
        self.stop_all_tunnels()

    def update_tray_actions(self):
        if not self.tray_start_action or not self.tray_stop_action:
            return
        has_tunnels = any(host.get('tunnels') for host in self.hosts)
        running_exists = any(info.get('status') == 'running' for info in self.tunnels.values())
        self.tray_start_action.setEnabled(has_tunnels)
        self.tray_stop_action.setEnabled(running_exists)


    def show_main_window(self):
        self.show()
        if self.isMinimized():
            self.showNormal()
        self.raise_()
        self.activateWindow()
        self.setWindowState((self.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)

    def on_tray_activated(self, reason):
        """托盘图标激活"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window()
    
    def change_language(self, index):
        """切换语言"""
        self.lang = 'zh' if index == 0 else 'en'
        self.save_config()
        self.refresh_ui()
    
    def refresh_ui(self):
        """刷新界面"""
        central = self.centralWidget()
        if central:
            central.deleteLater()
        self.init_ui()
        self.refresh_tunnel_table()
    
    def refresh_host_list(self):
        """刷新主机列表"""
        # 保存当前选中的主机信息
        current_name = None
        current_ip = None
        if self.current_host:
            current_name = self.current_host.get('name')
            current_ip = self.current_host.get('server_ip')
        
        self.host_list.clear()
        for host in self.hosts:
            item = QListWidgetItem(f"{host['name']} ({host['server_ip']})")
            # 只存储标识信息，不存储完整对象
            item.setData(Qt.UserRole, {
                'name': host['name'],
                'server_ip': host['server_ip']
            })
            self.host_list.addItem(item)
            
            # 如果是之前选中的主机，重新选中它
            if current_name and current_ip and \
               host['name'] == current_name and host['server_ip'] == current_ip:
                self.host_list.setCurrentItem(item)
    
    def on_host_selected(self):
        """主机被选中"""
        items = self.host_list.selectedItems()
        if items:
            selected_item = items[0]
            # 从item中获取主机的名称和IP，用于在hosts列表中查找
            temp_host = selected_item.data(Qt.UserRole)
            
            # 在hosts列表中查找对应的主机（获取最新数据）
            self.current_host = None
            for host in self.hosts:
                if host.get('name') == temp_host.get('name') and \
                   host.get('server_ip') == temp_host.get('server_ip'):
                    self.current_host = host
                    break
            
            if self.current_host:
                self.add_tunnel_btn.setEnabled(True)
                self.refresh_config_list()
            else:
                # 如果找不到，使用item中的数据（兼容性）
                self.current_host = temp_host
                self.add_tunnel_btn.setEnabled(True)
                self.refresh_config_list()
        else:
            self.current_host = None
            self.add_tunnel_btn.setEnabled(False)
            self.edit_tunnel_btn.setEnabled(False)
            self.delete_tunnel_btn.setEnabled(False)
            self.refresh_config_list()
    
    def on_tunnel_config_selected(self):
        """隧道配置被选中"""
        selected_items = self.config_list.selectedItems()
        has_selection = len(selected_items) > 0
        self.edit_tunnel_btn.setEnabled(has_selection)
        self.delete_tunnel_btn.setEnabled(has_selection)
    
    def refresh_config_list(self):
        """刷新当前主机的隧道配置列表"""
        self.config_list.clear()
        
        if not self.current_host:
            return
        
        tunnels = self.current_host.get('tunnels', [])
        for tunnel in tunnels:
            item_text = f"{tunnel['local_port']} → {tunnel.get('remote_host', '127.0.0.1')}:{tunnel['remote_port']}"
            self.config_list.addItem(item_text)
    
    def refresh_tunnel_table(self):
        """刷新活动隧道表格（显示所有主机的所有隧道）"""
        # 禁用更新以提高性能
        self.tunnel_table.setUpdatesEnabled(False)
        
        # 清空表格
        self.tunnel_table.setRowCount(0)
        
        # 计算总行数
        total_rows = sum(len(host.get('tunnels', [])) for host in self.hosts)
        
        # 一次性设置行数
        self.tunnel_table.setRowCount(total_rows)
        
        row = 0
        # 遍历所有主机的所有隧道配置
        for host in self.hosts:
            tunnels = host.get('tunnels', [])
            for tunnel in tunnels:
                tunnel_id = self.get_tunnel_id(host, tunnel)
                info = self.tunnels.get(tunnel_id)
                current_status = info.get('status', 'stopped') if info else 'stopped'
                
                # 主机名
                self.tunnel_table.setItem(row, 0, QTableWidgetItem(host['name']))
                
                # 本地端口按钮/标签
                self.tunnel_table.setCellWidget(
                    row, 1, self._build_local_port_widget(tunnel['local_port'], current_status)
                )

                
                # 远程主机
                self.tunnel_table.setItem(row, 2, QTableWidgetItem(tunnel.get('remote_host', '127.0.0.1')))
                
                # 远程端口
                self.tunnel_table.setItem(row, 3, QTableWidgetItem(str(tunnel['remote_port'])))
                
                # 状态
                status = self.tr('stopped')
                color = QColor(200, 200, 200)

                if current_status == 'running':
                    status = self.tr('running')
                    color = QColor(144, 238, 144)
                elif current_status == 'starting':
                    status = self.tr('starting')
                    color = QColor(255, 255, 200)
                elif current_status == 'reconnecting':
                    status = self.tr('reconnecting')
                    color = QColor(255, 215, 0)
                elif current_status == 'error':
                    status = self.tr('error')
                    color = QColor(255, 160, 160)
                elif current_status == 'stopped':
                    status = self.tr('stopped')
                    color = QColor(200, 200, 200)
                else:
                    status = current_status

                status_item = QTableWidgetItem(status)
                status_item.setBackground(color)
                self.tunnel_table.setItem(row, 4, status_item)
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(2, 2, 2, 2)
                
                if current_status in ('running', 'starting', 'reconnecting'):
                    stop_btn = QPushButton(self.tr('stop'))
                    stop_btn.clicked.connect(lambda checked, h=host, t=tunnel: self.stop_single_tunnel(h, t))
                    btn_layout.addWidget(stop_btn)
                else:
                    start_btn = QPushButton(self.tr('start'))
                    start_btn.clicked.connect(lambda checked, h=host, t=tunnel: self.start_single_tunnel(h, t))
                    btn_layout.addWidget(start_btn)
                
                self.tunnel_table.setCellWidget(row, 5, btn_widget)
                row += 1
        
        # 重新启用更新
        self.tunnel_table.setUpdatesEnabled(True)
        self.update_tray_actions()
    
    def _build_local_port_widget(self, port, status):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setAlignment(Qt.AlignCenter)

        button = QPushButton(str(port))
        button.setMinimumWidth(72)
        button.setFixedHeight(26)
        button.setCursor(Qt.PointingHandCursor if status == 'running' else Qt.ArrowCursor)
        button.setEnabled(status == 'running')
        button.setStyleSheet(
            "QPushButton {"
            " background-color: #e8f0ff;"
            " color: #1d4ed8;"
            " border: 1px solid #93c5fd;"
            " border-radius: 6px;"
            " padding: 2px 12px;"
            "}"
            "QPushButton:hover:enabled {"
            " background-color: #dbeafe;"
            " border-color: #60a5fa;"
            "}"
            "QPushButton:pressed:enabled {"
            " background-color: #bfdbfe;"
            " border-color: #3b82f6;"
            "}"
            "QPushButton:disabled {"
            " background-color: #f3f4f6;"
            " color: #9ca3af;"
            " border: 1px dashed #d1d5db;"
            "}"
        )

        if status == 'running':
            button.setToolTip(f"{self.tr('open_local')}: http://127.0.0.1:{port}/")
            button.clicked.connect(lambda checked, p=port: self.open_local_page(p))
        else:
            button.setToolTip(self.tr('open_local'))

        layout.addWidget(button, alignment=Qt.AlignCenter)
        return container

    def get_tunnel_id(self, host, tunnel):
        """生成隧道唯一ID"""
        return f"{host['name']}:{tunnel['local_port']}:{tunnel.get('remote_host', '127.0.0.1')}:{tunnel['remote_port']}"
    
    def add_host(self):
        """添加主机"""
        dialog = HostDialog(self, self.lang)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name'] or not data['server_ip'] or not data['username']:
                QMessageBox.warning(self, self.tr('warning'), self.tr('please_fill_all'))
                return
            
            data['tunnels'] = []
            self.hosts.append(data)
            self.save_config()
            self.refresh_host_list()
            QMessageBox.information(self, self.tr('success'), self.tr('host_saved'))
    
    def edit_host(self):
        """编辑主机"""
        if not self.current_host:
            QMessageBox.warning(self, self.tr('warning'), self.tr('please_select_host'))
            return
        
        dialog = HostDialog(self, self.lang, self.current_host)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name'] or not data['server_ip'] or not data['username']:
                QMessageBox.warning(self, self.tr('warning'), self.tr('please_fill_all'))
                return
            
            # 保留原有隧道配置
            data['tunnels'] = self.current_host.get('tunnels', [])
            
            # 找到在hosts列表中的索引并更新
            for i, host in enumerate(self.hosts):
                if host.get('name') == self.current_host.get('name') and \
                   host.get('server_ip') == self.current_host.get('server_ip'):
                    self.hosts[i] = data
                    break
            
            # 更新当前主机引用
            self.current_host = data
            
            self.save_config()
            self.refresh_host_list()  # 这里会自动重新选中
            QMessageBox.information(self, self.tr('success'), self.tr('host_saved'))
    
    def copy_host(self):
        """复制主机"""
        if not self.current_host:
            QMessageBox.warning(self, self.tr('warning'), self.tr('please_select_host'))
            return
        
        # 深拷贝当前主机配置
        copied_host = copy.deepcopy(self.current_host)
        
        # 修改名称以示区分
        copied_host['name'] = copied_host['name'] + ' (Copy)'
        
        # 打开编辑对话框，让用户修改
        dialog = HostDialog(self, self.lang, copied_host)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name'] or not data['server_ip'] or not data['username']:
                QMessageBox.warning(self, self.tr('warning'), self.tr('please_fill_all'))
                return
            
            # 保留复制的隧道配置
            # data['tunnels'] = copied_host.get('tunnels', [])
            
            # 添加到主机列表
            self.hosts.append(data)
            self.current_host = data
            self.save_config()
            self.refresh_host_list()  # 这里会自动选中新主机
            
            QMessageBox.information(self, self.tr('success'), self.tr('host_copied'))
    
    def delete_host(self):
        """删除主机"""
        if not self.current_host:
            QMessageBox.warning(self, self.tr('warning'), self.tr('please_select_host'))
            return
        
        reply = QMessageBox.question(
            self,
            self.tr('confirm'),
            self.tr('delete_confirm').format(self.current_host['name']),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 停止该主机的所有隧道
            tunnels = self.current_host.get('tunnels', [])
            for tunnel in tunnels:
                tunnel_id = self.get_tunnel_id(self.current_host, tunnel)
                if tunnel_id in self.tunnels:
                    self.tunnels[tunnel_id]['thread'].stop()
                    del self.tunnels[tunnel_id]
            
            # 删除主机
            self.hosts.remove(self.current_host)
            self.current_host = None
            self.save_config()
            self.refresh_host_list()
            self.refresh_config_list()
            self.refresh_tunnel_table()
    
    def add_tunnel(self):
        """添加隧道"""
        if not self.current_host:
            QMessageBox.warning(self, self.tr('warning'), self.tr('please_select_host'))
            return
        
        dialog = TunnelDialog(self, self.lang)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # 检查端口是否已被使用
            if self.is_port_in_use(data['local_port']):
                QMessageBox.warning(
                    self,
                    self.tr('warning'),
                    self.tr('port_in_use').format(data['local_port'])
                )
                return
            
            if 'tunnels' not in self.current_host:
                self.current_host['tunnels'] = []
            
            self.current_host['tunnels'].append(data)
            
            # 同步更新hosts列表中的数据
            for i, host in enumerate(self.hosts):
                if host.get('name') == self.current_host.get('name') and \
                   host.get('server_ip') == self.current_host.get('server_ip'):
                    self.hosts[i] = self.current_host
                    break
            
            self.save_config()
            self.refresh_config_list()
            self.refresh_tunnel_table()
            QMessageBox.information(self, self.tr('success'), self.tr('tunnel_saved'))
    
    def edit_tunnel(self):
        """编辑隧道"""
        if not self.current_host:
            QMessageBox.warning(self, self.tr('warning'), self.tr('please_select_host'))
            return
        
        row = self.config_list.currentRow()
        if row < 0:
            return
        
        tunnels = self.current_host.get('tunnels', [])
        if row >= len(tunnels):
            return
        
        tunnel = tunnels[row]
        dialog = TunnelDialog(self, self.lang, tunnel)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # 如果端口改变，检查新端口是否可用
            if data['local_port'] != tunnel['local_port']:
                if self.is_port_in_use(data['local_port']):
                    QMessageBox.warning(
                        self,
                        self.tr('warning'),
                        self.tr('port_in_use').format(data['local_port'])
                    )
                    return
            
            # 如果隧道正在运行，先停止
            tunnel_id = self.get_tunnel_id(self.current_host, tunnel)
            if tunnel_id in self.tunnels:
                self.tunnels[tunnel_id]['thread'].stop()
                del self.tunnels[tunnel_id]
            
            # 更新隧道配置
            tunnels[row] = data
            
            # 同步更新hosts列表中的数据
            for i, host in enumerate(self.hosts):
                if host.get('name') == self.current_host.get('name') and \
                   host.get('server_ip') == self.current_host.get('server_ip'):
                    self.hosts[i] = self.current_host
                    break
            
            self.save_config()
            self.refresh_config_list()
            self.refresh_tunnel_table()
            QMessageBox.information(self, self.tr('success'), self.tr('tunnel_saved'))
    
    def delete_tunnel(self):
        """删除隧道"""
        if not self.current_host:
            QMessageBox.warning(self, self.tr('warning'), self.tr('please_select_host'))
            return
        
        row = self.config_list.currentRow()
        if row < 0:
            return
        
        tunnels = self.current_host.get('tunnels', [])
        if row >= len(tunnels):
            return
        
        tunnel = tunnels[row]
        
        reply = QMessageBox.question(
            self,
            self.tr('confirm'),
            self.tr('delete_confirm').format(f"{tunnel['local_port']} -> {tunnel['remote_port']}"),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 停止隧道
            tunnel_id = self.get_tunnel_id(self.current_host, tunnel)
            if tunnel_id in self.tunnels:
                self.tunnels[tunnel_id]['thread'].stop()
                del self.tunnels[tunnel_id]
            
            # 删除配置
            tunnels.pop(row)
            
            # 同步更新hosts列表中的数据
            for i, host in enumerate(self.hosts):
                if host.get('name') == self.current_host.get('name') and \
                   host.get('server_ip') == self.current_host.get('server_ip'):
                    self.hosts[i] = self.current_host
                    break
            
            self.save_config()
            self.refresh_config_list()
            self.refresh_tunnel_table()
    
    def start_single_tunnel(self, host, tunnel):
        """从表格启动单个隧道"""
        tunnel_id = self.get_tunnel_id(host, tunnel)

        if self.is_port_in_use(tunnel['local_port']):
            QMessageBox.warning(
                self,
                self.tr('warning'),
                self.tr('port_in_use').format(tunnel['local_port'])
            )
            return

        host_copy = copy.deepcopy(host)
        tunnel_copy = copy.deepcopy(tunnel)

        thread = TunnelThread(host_copy, tunnel_copy)

        handler = partial(self.on_tunnel_status_changed, tunnel_id)
        thread.signal.status_changed.connect(handler)

        self.tunnels[tunnel_id] = {
            'config': tunnel_copy,
            'host_config': host_copy,
            'host_key': {
                'name': host.get('name'),
                'server_ip': host.get('server_ip')
            },
            'thread': thread,
            'status': 'starting',
            'last_error': '',
            'allow_auto_restart': True
        }

        thread.start()
        self.refresh_tunnel_table()

    def stop_single_tunnel(self, host, tunnel):
        """从表格停止单个隧道"""
        tunnel_id = self.get_tunnel_id(host, tunnel)

        if tunnel_id in self.tunnels:
            info = self.tunnels[tunnel_id]
            info['thread'].stop()
            if info['thread'].is_alive():
                info['thread'].join(timeout=2)
            info['status'] = 'stopped'
            info['allow_auto_restart'] = False
            self.refresh_tunnel_table()

    def open_local_page(self, port):
        """在默认浏览器中打开本地隧道地址"""
        url = f'http://127.0.0.1:{port}/'
        try:
            opened = webbrowser.open(url)
            if not opened:
                QMessageBox.warning(self, self.tr('warning'), f'Cannot open {url}')
        except Exception as exc:
            QMessageBox.warning(self, self.tr('warning'), f'Cannot open {url}: {exc}')

    @pyqtSlot(str, str)
    def on_tunnel_status_changed(self, tunnel_id, status, error):
        """处理隧道状态变化（在主线程中）"""
        if tunnel_id in self.tunnels:
            info = self.tunnels[tunnel_id]
            info['status'] = status
            if status == 'error':
                info['last_error'] = error
                info['allow_auto_restart'] = False
            else:
                info['last_error'] = error or ''
                if status in ('running', 'starting', 'reconnecting'):
                    info['allow_auto_restart'] = True

        if status == 'error' and error:
            QMessageBox.critical(
                self,
                self.tr('error'),
                f"{self.tr('connection_failed')}: {error}"
            )

        self.refresh_tunnel_table()

    def start_all_tunnels(self):
        """启动所有隧道"""
        for host in self.hosts:
            for tunnel in host.get('tunnels', []):
                tunnel_id = self.get_tunnel_id(host, tunnel)
                if tunnel_id not in self.tunnels or self.tunnels[tunnel_id]['status'] != 'running':
                    self.start_single_tunnel(host, tunnel)
    
    def stop_all_tunnels(self):
        """停止所有隧道"""
        for tunnel_id, info in list(self.tunnels.items()):
            info['allow_auto_restart'] = False
            thread = info.get('thread')
            if thread:
                thread.stop()
                if thread.is_alive():
                    thread.join(timeout=2)
            del self.tunnels[tunnel_id]

        self.refresh_tunnel_table()

    def is_port_in_use(self, port):
        """检查端口是否被占用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def on_auto_restart_changed(self, state):
        self.auto_restart_enabled = (state == Qt.Checked)
        self.save_config()

    def start_monitor(self):
        """启动监控定时器"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_tunnels)
        interval = max(1000, int(self.monitor_interval_ms))
        self.monitor_timer.start(interval)

    def check_tunnels(self):
        """检查隧道状态"""
        to_restart = []
        for tunnel_id, info in list(self.tunnels.items()):
            thread = info.get('thread')
            if thread is None:
                continue
            if not thread.is_alive():
                info['status'] = 'stopped'
                if self.auto_restart_enabled and info.get('allow_auto_restart', True):
                    to_restart.append((tunnel_id, info))

        self.refresh_tunnel_table()

        for tunnel_id, info in to_restart:
            self._restart_tunnel(tunnel_id, info)

    def _resolve_host_for_tunnel(self, info):
        host_key = info.get('host_key', {})
        for host in self.hosts:
            if host.get('name') == host_key.get('name') and host.get('server_ip') == host_key.get('server_ip'):
                return host
        return info.get('host_config')

    def _resolve_tunnel_config(self, host, info):
        config = info.get('config')
        if config is None:
            return None
        if not host:
            return config
        target = (
            config.get('local_port'),
            config.get('remote_host', '127.0.0.1'),
            config.get('remote_port')
        )
        for tunnel in host.get('tunnels', []):
            candidate = (
                tunnel.get('local_port'),
                tunnel.get('remote_host', '127.0.0.1'),
                tunnel.get('remote_port')
            )
            if candidate == target:
                return tunnel
        return config

    def _restart_tunnel(self, tunnel_id, info):
        host = self._resolve_host_for_tunnel(info)
        if host is None:
            host = info.get('host_config')
        tunnel_config = self._resolve_tunnel_config(host, info)
        if not host or not tunnel_config:
            return

        thread = info.get('thread')
        if thread:
            thread.stop()
            if thread.is_alive():
                thread.join(timeout=2)

        self.tunnels.pop(tunnel_id, None)
        self.start_single_tunnel(host, tunnel_config)

    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.hosts = data.get('hosts', [])
                    self.lang = data.get('lang', 'zh')
                    self.auto_restart_enabled = data.get('auto_restart', True)
                    interval = data.get('monitor_interval_ms', 3000)
                    if isinstance(interval, int) and interval > 0:
                        self.monitor_interval_ms = interval
            except Exception:
                self.hosts = []
                self.auto_restart_enabled = True
                self.monitor_interval_ms = 3000

    def save_config(self):
        """保存配置"""
        data = {
            'hosts': self.hosts,
            'lang': self.lang,
            'auto_restart': self.auto_restart_enabled,
            'monitor_interval_ms': int(self.monitor_interval_ms)
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def quit_app(self):
        """退出应用"""
        self.stop_all_tunnels()
        QApplication.quit()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        event.ignore()
        self.hide()
        self.tray.showMessage(
            self.tr('window_title'),
            self.tr('running_in_tray'),
            QSystemTrayIcon.Information,
            2000
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = SSHTunnelManager()
    window.show()
    
    sys.exit(app.exec_())