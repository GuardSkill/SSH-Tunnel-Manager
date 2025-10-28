import sys
import json
import subprocess
import os
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QListWidget, QSystemTrayIcon, QMenu, QMessageBox,
                             QDialog, QFormLayout, QSpinBox, QFileDialog,
                             QCheckBox, QListWidgetItem, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor

# 翻译字典
TRANSLATIONS = {
    'en': {
        'window_title': 'SSH Tunnel Manager',
        'server_config': 'Server Configuration',
        'host_name': 'Host Name:',
        'server_ip': 'Server IP:',
        'ssh_port': 'SSH Port:',
        'username': 'Username:',
        'password': 'Password:',
        'password_hint': 'Optional - leave empty for key-based auth',
        'show': 'Show',
        'save_config': '💾 Save Host',
        'load_config': '📂 Load Host',
        'set_ssh_path': '🔧 Set SSH Path',
        'new_config': '➕ New Host',
        'tunnel_mappings': 'Tunnel Mappings',
        'add_mapping': '➕ Add',
        'edit_mapping': '✏️ Edit',
        'delete_mapping': '❌ Delete',
        'remote_port': 'Remote',
        'local_port': 'Local',
        'status': 'Status',
        'actions': 'Actions',
        'active_tunnels': 'Active Tunnels',
        'start': 'Start',
        'stop': 'Stop',
        'start_all': '▶️ Start All',
        'stop_all': '⏹️ Stop All',
        'minimize': '🔽 Minimize to Tray',
        'running': 'Running',
        'stopped': 'Stopped',
        'ssh_status': 'SSH:',
        'language': 'Language',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'confirm': 'Confirm',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'load': 'Load',
        'config_saved': 'Configuration saved!',
        'select_config': 'Select a configuration:',
        'delete_config_confirm': 'Are you sure you want to delete this configuration?',
        'tunnel_created': 'Tunnel Created',
        'tunnel_stopped': 'Tunnel Stopped',
        'all_tunnels_stopped': 'All tunnels have been terminated',
        'ssh_not_found': 'SSH Not Found',
        'ssh_not_configured': 'SSH path not configured!\nPlease click "Set SSH Path" button.',
        'still_running': 'Still Running',
        'running_in_tray': 'SSH Tunnel Manager is running in the system tray',
        'show_window': '📋 Show Window',
        'quick_tunnel': '⚡ Quick Tunnel',
        'close_all_tunnels': '⛔ Close All Tunnels',
        'exit': '🚪 Exit',
        'add_tunnel_mapping': 'Add Tunnel Mapping',
        'edit_tunnel_mapping': 'Edit Tunnel Mapping',
        'please_fill_name': 'Please fill in the host name',
        'mapping_exists': 'This port mapping already exists!',
    },
    'zh': {
        'window_title': 'SSH 隧道管理器',
        'server_config': '服务器配置',
        'host_name': '主机名称:',
        'server_ip': '服务器IP:',
        'ssh_port': 'SSH端口:',
        'username': '用户名:',
        'password': '密码:',
        'password_hint': '可选 - 留空则使用密钥认证',
        'show': '显示',
        'save_config': '💾 保存主机',
        'load_config': '📂 加载主机',
        'set_ssh_path': '🔧 设置SSH路径',
        'new_config': '➕ 新建主机',
        'tunnel_mappings': '隧道映射配置',
        'add_mapping': '➕ 添加',
        'edit_mapping': '✏️ 编辑',
        'delete_mapping': '❌ 删除',
        'remote_port': '远程端口',
        'local_port': '本地端口',
        'status': '状态',
        'actions': '操作',
        'active_tunnels': '活动隧道',
        'start': '启动',
        'stop': '停止',
        'start_all': '▶️ 全部启动',
        'stop_all': '⏹️ 全部停止',
        'minimize': '🔽 最小化到托盘',
        'running': '运行中',
        'stopped': '已停止',
        'ssh_status': 'SSH路径:',
        'language': '语言',
        'success': '成功',
        'error': '错误',
        'warning': '警告',
        'confirm': '确认',
        'cancel': '取消',
        'delete': '删除',
        'load': '加载',
        'config_saved': '配置已保存！',
        'select_config': '选择一个配置：',
        'delete_config_confirm': '确定要删除这个配置吗？',
        'tunnel_created': '隧道已创建',
        'tunnel_stopped': '隧道已停止',
        'all_tunnels_stopped': '所有隧道已关闭',
        'ssh_not_found': '未找到SSH',
        'ssh_not_configured': 'SSH路径未配置！\n请点击"设置SSH路径"按钮。',
        'still_running': '仍在运行',
        'running_in_tray': 'SSH隧道管理器正在系统托盘运行',
        'show_window': '📋 显示窗口',
        'quick_tunnel': '⚡ 快速隧道',
        'close_all_tunnels': '⛔ 关闭所有隧道',
        'exit': '🚪 退出',
        'add_tunnel_mapping': '添加隧道映射',
        'edit_tunnel_mapping': '编辑隧道映射',
        'please_fill_name': '请填写主机名称',
        'mapping_exists': '此端口映射已存在！',
    }
}

class SSHTunnelManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file = Path.home() / '.ssh_tunnel_config.json'
        self.tunnels = {}  # {key: {config, remote, local, running, process}}
        self.configs = self.load_configs()
        self.current_config = self.configs[0] if self.configs else self.default_config()
        self.ssh_path = self.find_ssh_path()
        self.lang = 'en'  # 默认英文
        
        if not self.ssh_path:
            self.prompt_ssh_path()
        
        self.init_ui()
        self.init_tray()
        self.start_monitor()
        self.load_all_mappings()
        
    def tr(self, key):
        """翻译函数"""
        return TRANSLATIONS[self.lang].get(key, key)
    
    def change_language(self, lang):
        """切换语言"""
        self.lang = lang
        self.refresh_ui()
    
    def refresh_ui(self):
        """刷新界面文字"""
        self.setWindowTitle(self.tr('window_title'))
        # 重新初始化UI
        central = self.centralWidget()
        if central:
            central.deleteLater()
        self.init_ui()
        self.update_tunnel_table()
        
    def default_config(self):
        return {
            'name': 'Default Server',
            'server_ip': '117.50.222.222',
            'server_port': 3300,
            'server_user': 'root',
            'password': '',
            'mappings': []
        }
    
    def find_ssh_path(self):
        """智能查找 SSH 可执行文件路径"""
        settings_file = Path.home() / '.ssh_tunnel_settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    if 'ssh_path' in settings and Path(settings['ssh_path']).exists():
                        return settings['ssh_path']
            except:
                pass
        
        ssh = shutil.which('ssh')
        if ssh:
            return ssh
        
        if sys.platform == 'win32':
            common_paths = [
                r'C:\Windows\Sysnative\OpenSSH\ssh.exe',
                r'C:\Windows\System32\OpenSSH\ssh.exe',
                r'C:\Program Files\Git\usr\bin\ssh.exe',
                r'C:\Program Files (x86)\Git\usr\bin\ssh.exe',
                Path.home() / 'scoop' / 'apps' / 'openssh' / 'current' / 'ssh.exe',
                Path.home() / 'scoop' / 'shims' / 'ssh.exe',
            ]
            for path in common_paths:
                if Path(path).exists():
                    return str(path)
        else:
            common_paths = ['/usr/bin/ssh', '/usr/local/bin/ssh', '/bin/ssh']
            for path in common_paths:
                if Path(path).exists():
                    return path
        
        return None
    
    def prompt_ssh_path(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(self.tr('ssh_not_found'))
        msg.setText('Cannot find SSH executable automatically.')
        msg.setInformativeText('Would you like to specify the SSH path manually?')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec_() == QMessageBox.Yes:
            self.select_ssh_path()
    
    def select_ssh_path(self):
        if sys.platform == 'win32':
            file_filter = 'SSH Executable (ssh.exe);;All Files (*.*)'
            default_dir = r'C:\Windows\System32\OpenSSH'
        else:
            file_filter = 'SSH Executable (ssh);;All Files (*)'
            default_dir = '/usr/bin'
        
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Select SSH Executable',
            default_dir,
            file_filter
        )
        
        if path:
            try:
                result = subprocess.run([path, '-V'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=3)
                if 'OpenSSH' in result.stderr or 'OpenSSH' in result.stdout:
                    self.ssh_path = path
                    self.save_ssh_path(path)
                    QMessageBox.information(self, self.tr('success'), f'SSH path set to:\n{path}')
                    if hasattr(self, 'ssh_status_label'):
                        self.ssh_status_label.setText(f"{self.tr('ssh_status')} {self.ssh_path}")
                        self.ssh_status_label.setStyleSheet('color: green')
                else:
                    QMessageBox.warning(self, 'Invalid', 'The selected file does not appear to be SSH.')
            except Exception as e:
                QMessageBox.critical(self, self.tr('error'), f'Failed to verify SSH:\n{str(e)}')
    
    def save_ssh_path(self, path):
        settings_file = Path.home() / '.ssh_tunnel_settings.json'
        settings = {'ssh_path': path}
        with open(settings_file, 'w') as f:
            json.dump(settings, f)
    
    def init_ui(self):
        self.setWindowTitle(self.tr('window_title'))
        self.setGeometry(100, 100, 900, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # 语言切换
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(self.tr('language') + ':'))
        lang_combo = QComboBox()
        lang_combo.addItems(['English', '中文'])
        lang_combo.setCurrentIndex(0 if self.lang == 'en' else 1)
        lang_combo.currentIndexChanged.connect(
            lambda idx: self.change_language('en' if idx == 0 else 'zh')
        )
        lang_layout.addWidget(lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # 服务器配置区域
        layout.addWidget(QLabel(f'<b>{self.tr("server_config")}</b>'))
        config_group = QWidget()
        config_layout = QFormLayout(config_group)
        
        self.host_name = QLineEdit(self.current_config.get('name', 'Default Server'))
        self.server_ip = QLineEdit(self.current_config['server_ip'])
        self.server_port = QSpinBox()
        self.server_port.setRange(1, 65535)
        self.server_port.setValue(self.current_config['server_port'])
        self.server_user = QLineEdit(self.current_config['server_user'])
        self.server_password = QLineEdit(self.current_config.get('password', ''))
        self.server_password.setEchoMode(QLineEdit.Password)
        self.server_password.setPlaceholderText(self.tr('password_hint'))
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.server_password)
        show_password = QCheckBox(self.tr('show'))
        show_password.toggled.connect(
            lambda checked: self.server_password.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        password_layout.addWidget(show_password)
        password_widget = QWidget()
        password_widget.setLayout(password_layout)
        
        config_layout.addRow(self.tr('host_name'), self.host_name)
        config_layout.addRow(self.tr('server_ip'), self.server_ip)
        config_layout.addRow(self.tr('ssh_port'), self.server_port)
        config_layout.addRow(self.tr('username'), self.server_user)
        config_layout.addRow(self.tr('password'), password_widget)
        
        layout.addWidget(config_group)
        
        # 配置管理按钮
        config_btn_layout = QHBoxLayout()
        save_btn = QPushButton(self.tr('save_config'))
        save_btn.clicked.connect(self.save_current_config)
        load_btn = QPushButton(self.tr('load_config'))
        load_btn.clicked.connect(self.show_config_selector)
        new_btn = QPushButton(self.tr('new_config'))
        new_btn.clicked.connect(self.new_config)
        ssh_path_btn = QPushButton(self.tr('set_ssh_path'))
        ssh_path_btn.clicked.connect(self.select_ssh_path)
        config_btn_layout.addWidget(save_btn)
        config_btn_layout.addWidget(load_btn)
        config_btn_layout.addWidget(new_btn)
        config_btn_layout.addWidget(ssh_path_btn)
        layout.addLayout(config_btn_layout)
        
        # SSH状态
        ssh_status = QLabel(f"{self.tr('ssh_status')} {self.ssh_path or 'Not Found'}")
        ssh_status.setStyleSheet('color: ' + ('green' if self.ssh_path else 'red'))
        layout.addWidget(ssh_status)
        self.ssh_status_label = ssh_status
        
        # 隧道映射配置
        layout.addWidget(QLabel(f'<b>{self.tr("tunnel_mappings")}</b>'))
        
        mapping_btn_layout = QHBoxLayout()
        add_map_btn = QPushButton(self.tr('add_mapping'))
        add_map_btn.clicked.connect(self.add_mapping)
        edit_map_btn = QPushButton(self.tr('edit_mapping'))
        edit_map_btn.clicked.connect(self.edit_mapping)
        del_map_btn = QPushButton(self.tr('delete_mapping'))
        del_map_btn.clicked.connect(self.delete_mapping)
        mapping_btn_layout.addWidget(add_map_btn)
        mapping_btn_layout.addWidget(edit_map_btn)
        mapping_btn_layout.addWidget(del_map_btn)
        mapping_btn_layout.addStretch()
        layout.addLayout(mapping_btn_layout)
        
        # 活动隧道表格
        layout.addWidget(QLabel(f'<b>{self.tr("active_tunnels")}</b>'))
        self.tunnel_table = QTableWidget()
        self.tunnel_table.setColumnCount(6)
        self.tunnel_table.setHorizontalHeaderLabels([
            self.tr('host_name').replace(':', ''),
            self.tr('remote_port'),
            self.tr('local_port'),
            'SSH Port',
            self.tr('status'),
            self.tr('actions')
        ])
        self.tunnel_table.horizontalHeader().setStretchLastSection(True)
        self.tunnel_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tunnel_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tunnel_table)
        
        # 批量操作按钮
        batch_btn_layout = QHBoxLayout()
        start_all_btn = QPushButton(self.tr('start_all'))
        start_all_btn.clicked.connect(self.start_all_tunnels)
        stop_all_btn = QPushButton(self.tr('stop_all'))
        stop_all_btn.clicked.connect(self.stop_all_tunnels)
        minimize_btn = QPushButton(self.tr('minimize'))
        minimize_btn.clicked.connect(self.hide)
        batch_btn_layout.addWidget(start_all_btn)
        batch_btn_layout.addWidget(stop_all_btn)
        batch_btn_layout.addWidget(minimize_btn)
        layout.addLayout(batch_btn_layout)
    
    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        self.tray.setToolTip(self.tr('window_title'))
        
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction(self.tr('show_window'))
        show_action.triggered.connect(self.show)
        
        tray_menu.addSeparator()
        
        close_all_action = tray_menu.addAction(self.tr('close_all_tunnels'))
        close_all_action.triggered.connect(self.stop_all_tunnels)
        
        tray_menu.addSeparator()
        
        exit_action = tray_menu.addAction(self.tr('exit'))
        exit_action.triggered.connect(self.quit_app)
        
        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()
    
    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
    
    def new_config(self):
        """创建新配置"""
        self.host_name.clear()
        self.server_ip.clear()
        self.server_port.setValue(22)
        self.server_user.clear()
        self.server_password.clear()
        self.current_config = self.default_config()
        self.update_tunnel_table()
    
    def add_mapping(self):
        """添加映射"""
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr('add_tunnel_mapping'))
        layout = QFormLayout(dialog)
        
        remote_port = QSpinBox()
        remote_port.setRange(1, 65535)
        remote_port.setValue(8188)
        
        local_port = QSpinBox()
        local_port.setRange(1, 65535)
        local_port.setValue(8188)
        
        layout.addRow(self.tr('remote_port') + ':', remote_port)
        layout.addRow(self.tr('local_port') + ':', local_port)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(self.tr('confirm'))
        cancel_btn = QPushButton(self.tr('cancel'))
        
        def add():
            if not self.host_name.text().strip():
                QMessageBox.warning(self, self.tr('warning'), self.tr('please_fill_name'))
                return
            
            # 检查是否已存在
            for mapping in self.current_config.get('mappings', []):
                if mapping['remote'] == remote_port.value() and mapping['local'] == local_port.value():
                    QMessageBox.warning(self, self.tr('warning'), self.tr('mapping_exists'))
                    return
            
            if 'mappings' not in self.current_config:
                self.current_config['mappings'] = []
            
            self.current_config['mappings'].append({
                'remote': remote_port.value(),
                'local': local_port.value()
            })
            self.update_tunnel_table()
            dialog.accept()
        
        ok_btn.clicked.connect(add)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        dialog.exec_()
    
    def edit_mapping(self):
        """编辑选中的映射"""
        row = self.tunnel_table.currentRow()
        if row < 0:
            return
        
        host_name = self.tunnel_table.item(row, 0).text()
        config = next((c for c in self.configs if c['name'] == host_name), None)
        if not config:
            return
        
        remote = int(self.tunnel_table.item(row, 1).text())
        local = int(self.tunnel_table.item(row, 2).text())
        
        mapping_idx = None
        for idx, m in enumerate(config['mappings']):
            if m['remote'] == remote and m['local'] == local:
                mapping_idx = idx
                break
        
        if mapping_idx is None:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr('edit_tunnel_mapping'))
        layout = QFormLayout(dialog)
        
        remote_port = QSpinBox()
        remote_port.setRange(1, 65535)
        remote_port.setValue(remote)
        
        local_port = QSpinBox()
        local_port.setRange(1, 65535)
        local_port.setValue(local)
        
        layout.addRow(self.tr('remote_port') + ':', remote_port)
        layout.addRow(self.tr('local_port') + ':', local_port)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(self.tr('confirm'))
        cancel_btn = QPushButton(self.tr('cancel'))
        
        def save():
            config['mappings'][mapping_idx] = {
                'remote': remote_port.value(),
                'local': local_port.value()
            }
            self.save_configs()
            self.update_tunnel_table()
            dialog.accept()
        
        ok_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        dialog.exec_()
    
    def delete_mapping(self):
        """删除选中的映射"""
        row = self.tunnel_table.currentRow()
        if row < 0:
            return
        
        reply = QMessageBox.question(
            self, 
            self.tr('confirm'),
            self.tr('delete_config_confirm'),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            host_name = self.tunnel_table.item(row, 0).text()
            config = next((c for c in self.configs if c['name'] == host_name), None)
            if config:
                remote = int(self.tunnel_table.item(row, 1).text())
                local = int(self.tunnel_table.item(row, 2).text())
                
                config['mappings'] = [
                    m for m in config['mappings'] 
                    if not (m['remote'] == remote and m['local'] == local)
                ]
                
                # 如果隧道正在运行，先停止
                key = f"{host_name}:{remote}:{local}"
                if key in self.tunnels:
                    self.stop_tunnel(host_name, remote, local)
                
                self.save_configs()
                self.update_tunnel_table()
    
    def load_all_mappings(self):
        """加载所有配置的映射到表格"""
        self.update_tunnel_table()
    
    def update_tunnel_table(self):
        """更新隧道表格"""
        self.tunnel_table.setRowCount(0)
        
        for config in self.configs:
            for mapping in config.get('mappings', []):
                row = self.tunnel_table.rowCount()
                self.tunnel_table.insertRow(row)
                
                # 主机名
                self.tunnel_table.setItem(row, 0, QTableWidgetItem(config['name']))
                
                # 远程端口
                self.tunnel_table.setItem(row, 1, QTableWidgetItem(str(mapping['remote'])))
                
                # 本地端口
                self.tunnel_table.setItem(row, 2, QTableWidgetItem(str(mapping['local'])))
                
                # SSH端口
                self.tunnel_table.setItem(row, 3, QTableWidgetItem(str(config['server_port'])))
                
                # 状态
                key = f"{config['name']}:{mapping['remote']}:{mapping['local']}"
                is_running = key in self.tunnels and self.tunnels[key].get('running', False)
                status_item = QTableWidgetItem(self.tr('running') if is_running else self.tr('stopped'))
                status_item.setForeground(QColor('green' if is_running else 'red'))
                self.tunnel_table.setItem(row, 4, status_item)
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(2, 2, 2, 2)
                
                if is_running:
                    stop_btn = QPushButton(self.tr('stop'))
                    stop_btn.clicked.connect(
                        lambda checked, c=config, r=mapping['remote'], l=mapping['local']: 
                        self.stop_tunnel(c['name'], r, l)
                    )
                    btn_layout.addWidget(stop_btn)
                else:
                    start_btn = QPushButton(self.tr('start'))
                    start_btn.clicked.connect(
                        lambda checked, c=config, r=mapping['remote'], l=mapping['local']: 
                        self.start_tunnel(c, r, l)
                    )
                    btn_layout.addWidget(start_btn)
                
                self.tunnel_table.setCellWidget(row, 5, btn_widget)
        
        # 调整列宽
        self.tunnel_table.resizeColumnsToContents()
    
    def start_tunnel(self, config, remote, local):
        """启动单个隧道"""
        if not self.ssh_path:
            QMessageBox.critical(self, self.tr('error'), self.tr('ssh_not_configured'))
            return
        
        server = f"{config['server_user']}@{config['server_ip']}"
        port = config['server_port']
        password = config.get('password', '')
        ssh_options = [
        '-o', 'StrictHostKeyChecking=no',
        # '-o', 'UserKnownHostsFile=/dev/null',  # 可选:不保存到 known_hosts
        # '-o', 'LogLevel=ERROR'  # 减少警告信息
    ]
        # Windows下不使用-f参数，使用隐藏窗口方式
        # ssh -p 4000 -CNg -L 8677:127.0.0.1:8675 root@115.190.75.243  -o StrictHostKeyChecking=no
        if sys.platform == 'win32':
            cmd = [
                self.ssh_path, '-N',
                 *ssh_options,  # 添加 SSH 选项
                '-L', f'{local}:localhost:{remote}',
                '-p', str(port),
                server
            ]
        else:
            cmd = [
                self.ssh_path, '-N', '-f',
                 *ssh_options,  # 添加 SSH 选项
                '-L', f'{local}:localhost:{remote}',
                '-p', str(port),
                server
            ]
        
        if password:
            if sys.platform == 'win32':
                QMessageBox.warning(self, self.tr('warning'), 
                    'Password authentication via command line is not recommended on Windows.\n'
                    'Please use SSH key authentication instead.')
            else:
                if shutil.which('sshpass'):
                    cmd = ['sshpass', '-p', password] + cmd
        
        try:
            # Windows下使用隐藏窗口方式启动
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # 等待一下看是否立即失败
                import time
                time.sleep(1)
                if process.poll() is not None:
                    _, stderr = process.communicate()
                    QMessageBox.warning(self, self.tr('error'), f'Failed to create tunnel:\n{stderr.decode()}')
                    return
                
                key = f"{config['name']}:{remote}:{local}"
                self.tunnels[key] = {
                    'config': config,
                    'remote': remote,
                    'local': local,
                    'running': True,
                    'process': process
                }
            else:
                # Linux/Mac使用-f后台模式
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    QMessageBox.warning(self, self.tr('error'), f'Failed to create tunnel:\n{result.stderr}')
                    return
                
                key = f"{config['name']}:{remote}:{local}"
                self.tunnels[key] = {
                    'config': config,
                    'remote': remote,
                    'local': local,
                    'running': True,
                    'process': None
                }
            
            self.update_tunnel_table()
            self.tray.showMessage(
                self.tr('tunnel_created'),
                f"[{config['name']}] {remote} → {local}",
                QSystemTrayIcon.Information,
                2000
            )
        
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, self.tr('error'), 'SSH connection timed out')
        except Exception as e:
            QMessageBox.critical(self, self.tr('error'), f'Unexpected error: {str(e)}')
    
    def stop_tunnel(self, host_name, remote, local):
        """停止单个隧道"""
        key = f"{host_name}:{remote}:{local}"
        
        if key in self.tunnels:
            # 如果有进程对象，直接终止
            if self.tunnels[key].get('process'):
                try:
                    process = self.tunnels[key]['process']
                    process.terminate()
                    process.wait(timeout=3)
                except:
                    try:
                        process.kill()
                    except:
                        pass
            
            # 通过端口杀死进程
            self.kill_tunnel_by_port(local)
            
            self.tunnels[key]['running'] = False
            del self.tunnels[key]
            
            self.update_tunnel_table()
            self.tray.showMessage(
                self.tr('tunnel_stopped'),
                f"[{host_name}] {remote} → {local}",
                QSystemTrayIcon.Information,
                2000
            )
    
    def kill_tunnel_by_port(self, local_port):
        """通过本地端口杀死SSH隧道进程"""
        if sys.platform == 'win32':
            # 找到监听该端口的进程PID
            cmd = f'netstat -ano | findstr ":{local_port}" | findstr "LISTENING"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            pids = set()
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) > 4:
                    # 确认是127.0.0.1或0.0.0.0上监听的端口
                    if '127.0.0.1' in parts[1] or '0.0.0.0' in parts[1]:
                        pid = parts[-1]
                        pids.add(pid)
            
            # 杀死所有相关进程
            for pid in pids:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', pid], 
                                 capture_output=True, 
                                 timeout=5)
                except:
                    pass
        else:
            # Linux/Mac
            try:
                # 使用lsof找到监听该端口的进程
                result = subprocess.run(
                    ['lsof', '-ti', f':{local_port}'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid], capture_output=True)
            except:
                pass
    
    def start_all_tunnels(self):
        """启动所有隧道"""
        for config in self.configs:
            for mapping in config.get('mappings', []):
                key = f"{config['name']}:{mapping['remote']}:{mapping['local']}"
                if key not in self.tunnels or not self.tunnels[key].get('running', False):
                    self.start_tunnel(config, mapping['remote'], mapping['local'])
    
    def stop_all_tunnels(self):
        """停止所有隧道"""
        # 先终止所有记录的进程
        for key in list(self.tunnels.keys()):
            if self.tunnels[key].get('process'):
                try:
                    process = self.tunnels[key]['process']
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    try:
                        process.kill()
                    except:
                        pass
        
        # 然后杀死所有SSH进程
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/IM', 'ssh.exe'], 
                         capture_output=True)
        else:
            subprocess.run(['pkill', '-9', '-f', 'ssh.*-L'], 
                         capture_output=True)
        
        self.tunnels.clear()
        
        self.update_tunnel_table()
        self.tray.showMessage(
            self.tr('close_all_tunnels'),
            self.tr('all_tunnels_stopped'),
            QSystemTrayIcon.Information,
            2000
        )
    
    def kill_tunnel(self, local_port):
        """终止特定端口的隧道（已废弃，使用kill_tunnel_by_port）"""
        self.kill_tunnel_by_port(local_port)
    
    def start_monitor(self):
        """启动隧道状态监控"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_tunnels)
        self.monitor_timer.start(5000)
    
    def check_tunnels(self):
        """检查隧道状态"""
        for key in list(self.tunnels.keys()):
            if self.tunnels[key].get('process'):
                # 检查进程是否还在运行
                if self.tunnels[key]['process'].poll() is not None:
                    self.tunnels[key]['running'] = False
            else:
                # 通过端口检查是否还在监听
                local_port = self.tunnels[key]['local']
                if not self.is_port_listening(local_port):
                    self.tunnels[key]['running'] = False
        
        self.update_tunnel_table()
    
    def is_port_listening(self, port):
        """检查端口是否在监听"""
        if sys.platform == 'win32':
            cmd = f'netstat -ano | findstr ":{port}" | findstr "LISTENING"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return f':{port}' in result.stdout and 'LISTENING' in result.stdout
        else:
            try:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}', '-sTCP:LISTEN'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                return result.returncode == 0
            except:
                return False
    
    def save_current_config(self):
        """保存当前配置"""
        if not self.host_name.text().strip():
            QMessageBox.warning(self, self.tr('warning'), self.tr('please_fill_name'))
            return
        
        config = {
            'name': self.host_name.text(),
            'server_ip': self.server_ip.text(),
            'server_port': self.server_port.value(),
            'server_user': self.server_user.text(),
            'password': self.server_password.text(),
            'mappings': self.current_config.get('mappings', [])
        }
        
        existing = next((c for c in self.configs if c['name'] == config['name']), None)
        if existing:
            idx = self.configs.index(existing)
            self.configs[idx] = config
        else:
            self.configs.append(config)
        
        self.current_config = config
        self.save_configs()
        self.update_tunnel_table()
        QMessageBox.information(self, self.tr('success'), self.tr('config_saved'))
    
    def show_config_selector(self):
        """显示配置选择器"""
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr('load_config'))
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        config_list = QListWidget()
        for config in self.configs:
            config_list.addItem(f"{config['name']} ({config['server_ip']}:{config['server_port']})")
        
        layout.addWidget(QLabel(self.tr('select_config')))
        layout.addWidget(config_list)
        
        btn_layout = QHBoxLayout()
        load_btn = QPushButton(self.tr('load'))
        delete_btn = QPushButton(self.tr('delete'))
        cancel_btn = QPushButton(self.tr('cancel'))
        
        def load_config():
            row = config_list.currentRow()
            if row >= 0:
                self.current_config = self.configs[row]
                self.host_name.setText(self.current_config.get('name', 'Default Server'))
                self.server_ip.setText(self.current_config['server_ip'])
                self.server_port.setValue(self.current_config['server_port'])
                self.server_user.setText(self.current_config['server_user'])
                self.server_password.setText(self.current_config.get('password', ''))
                # 加载主机后自动刷新表格，显示该主机的所有映射
                self.update_tunnel_table()
                dialog.accept()
        
        def delete_config():
            row = config_list.currentRow()
            if row >= 0:
                reply = QMessageBox.question(
                    dialog,
                    self.tr('confirm'),
                    self.tr('delete_config_confirm'),
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    # 删除配置前，停止该主机的所有隧道
                    config_name = self.configs[row]['name']
                    keys_to_remove = [k for k in self.tunnels.keys() if k.startswith(f"{config_name}:")]
                    for key in keys_to_remove:
                        local_port = self.tunnels[key]['local']
                        self.kill_tunnel_by_port(local_port)
                        del self.tunnels[key]
                    
                    del self.configs[row]
                    self.save_configs()
                    config_list.takeItem(row)
                    self.update_tunnel_table()
        
        load_btn.clicked.connect(load_config)
        delete_btn.clicked.connect(delete_config)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def load_configs(self):
        """从文件加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_configs(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.configs, f, indent=2, ensure_ascii=False)
    
    def quit_app(self):
        """退出应用"""
        self.stop_all_tunnels()
        QApplication.quit()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        event.ignore()
        self.hide()
        self.tray.showMessage(
            self.tr('still_running'),
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