# SSH 隧道管理器 / SSH Tunnel Manager

一个免费、开源、方便的SSH隧道管理工具，支持图形化界面管理多个SSH端口转发隧道，一键启停，保存主机密钥和配置，缩小到系统盘，不影响其他界面操作。

<a href="#-支持开发者--support-the-developer"> 
  <img src="https://img.shields.io/badge/感谢支持-支付宝-ff69b4.svg?style=for-the-badge&logo=alipay&logoColor=white" alt="感谢支持支付宝">
</a>
<a href="#-支持开发者--support-the-developer">
  <img src="https://img.shields.io/badge/感谢支持-微信-1aad19.svg?style=for-the-badge&logo=wechat&logoColor=white" alt="感谢支持微信">
</a>

![UI](media/UI.png)

- 🌐 **多主机管理** - 支持保存和切换多个SSH服务器配置
- 🔌 **端口映射** - 轻松创建和管理多个本地到远程端口的映射
- 📊 **可视化状态** - 实时显示所有隧道的运行状态
- 🔄 **批量操作** - 一键启动/停止所有隧道
- 💾 **配置持久化** - 自动保存所有配置，下次启动自动加载
- 🌍 **多语言支持** - 支持中文和英文界面切换
- 🔒 **认证方式** - 支持密码和SSH密钥两种认证方式
- 📌 **系统托盘** - 最小化到系统托盘，后台运行
- 🎯 **智能检测** - 自动检测SSH路径，支持多种SSH客户端



## 📋 系统要求

- Python 3.7+
- PyQt5
- SSH客户端（OpenSSH或Git Bash）

### 支持的操作系统
- ✅ Windows 10/11
- ✅ Linux
- ✅ macOS

## 🚀 快速开始

### 安装依赖

```bash
pip install PyQt5
```

### 运行程序

```bash
python ssh_tunnel_manager.py
```

## 📦 打包成独立可执行文件

### 方法一：使用 PyInstaller（推荐）

1. **安装 PyInstaller**
```bash
pip install pyinstaller
```

2. **创建打包脚本** `build.spec`（已包含在项目中）

3. **执行打包**
```bash
# Windows
pyinstaller --clean ssh_tunnel_manager.spec

# Linux/macOS
pyinstaller --clean ssh_tunnel_manager.spec
```

4. **查找生成的可执行文件**
   - Windows: `dist/SSHTunnelManager.exe`
   - Linux: `dist/SSHTunnelManager`
   - macOS: `dist/SSHTunnelManager.app`

### 方法二：使用 PyInstaller 命令行

#### Windows
```bash
pyinstaller --name="SSHTunnelManager" ^
            --windowed ^
            --onefile ^
            --icon=icon.ico ^
            ssh_tunnel_manager.py
```

#### Linux/macOS
```bash
pyinstaller --name="SSHTunnelManager" \
            --windowed \
            --onefile \
            ssh_tunnel_manager.py
```

### 打包参数说明
- `--name`: 指定生成的可执行文件名称
- `--windowed`: 不显示控制台窗口（GUI应用必需）
- `--onefile`: 打包成单个可执行文件
- `--icon`: 指定应用图标（可选）
- `--clean`: 清理临时文件
- `--noconsole`: Windows下隐藏控制台（等同于--windowed）

## 📖 使用指南

### 1. 首次运行

首次运行时，程序会自动检测SSH客户端路径。如果未找到，请点击"设置SSH路径"按钮手动指定。

常见SSH路径：
- Windows: `C:\Windows\System32\OpenSSH\ssh.exe`
- Linux: `/usr/bin/ssh`
- macOS: `/usr/bin/ssh`
- Git Bash: `C:\Program Files\Git\usr\bin\ssh.exe`

### 2. 配置服务器

1. 填写服务器信息：
   - 主机名称：给服务器起一个便于识别的名字
   - 服务器IP：SSH服务器地址
   - SSH端口：默认22
   - 用户名：SSH登录用户名
   - 密码：可选，留空则使用SSH密钥认证

2. 点击"💾 保存主机"保存配置

### 3. 添加端口映射

1. 点击"➕ 添加"按钮
2. 填写远程端口和本地端口
3. 示例：
   - 远程端口：3306（MySQL）
   - 本地端口：13306
   
   访问 `localhost:13306` 即可连接到远程服务器的3306端口

### 4. 启动隧道

- **单个隧道**：在隧道列表中点击"启动"按钮
- **全部隧道**：点击"▶️ 全部启动"按钮

### 5. 管理多个服务器

1. 点击"➕ 新建主机"清空当前配置
2. 输入新服务器信息并保存
3. 点击"📂 加载主机"切换不同服务器配置

### 6. 系统托盘功能

点击"🔽 最小化到托盘"后，程序会在后台运行：
- 📋 显示窗口：恢复主窗口
- ⚡ 快速隧道：查看当前活动的隧道
- ⛔ 关闭所有隧道：一键停止所有连接
- 🚪 退出：完全关闭程序

## 🔧 高级功能

### 多语言切换
在界面右上角选择语言：English / 中文

### 批量操作
- **全部启动**：启动所有已配置的端口映射
- **全部停止**：关闭所有活动隧道

### 配置文件位置
- 主配置：`~/.ssh_tunnel_config.json`
- SSH路径：`~/.ssh_tunnel_settings.json`

## 🛠️ 故障排除

### SSH未找到
**问题**：提示"SSH路径未配置"
**解决**：
1. 点击"设置SSH路径"按钮
2. 手动选择SSH可执行文件
3. 或安装OpenSSH：
   - Windows: 设置 → 应用 → 可选功能 → OpenSSH客户端
   - Linux: `sudo apt install openssh-client`
   - macOS: 系统自带

### 端口已被占用
**问题**：隧道无法启动
**解决**：
1. 更换本地端口号
2. 或关闭占用该端口的程序

### 隧道意外断开
**问题**：状态显示"已停止"
**解决**：
1. 检查网络连接
2. 验证服务器SSH服务是否正常
3. 重新启动隧道

### 密钥认证失败
**问题**：使用密钥时连接失败
**解决**：
1. 确保SSH密钥已添加：`ssh-add ~/.ssh/id_rsa`
2. 或在配置中填写密码

## 📝 使用场景

### 开发调试
```
远程数据库 → 本地访问
远程端口：3306 (MySQL)
本地端口：13306
连接：localhost:13306
```

### 内网穿透
```
远程服务 → 本地端口
远程端口：8080 (Web服务)
本地端口：18080
访问：http://localhost:18080
```

### 多服务管理
```
MySQL:    3306 → 13306
Redis:    6379 → 16379
MongoDB:  27017 → 127017
```

## ☕ 支持开发者 / Support the Developer

如果这个工具能提高你的工作效率或让你心情开心一点，请考虑请我喝杯咖啡，支持我继续开发和维护这个项目或其他开源项目。

If this tool has been helpful to you, please consider buying me a coffee to support my continued development and maintenance of this project!

![感谢支持 / Thank You for Your Support](media/coffe_thanks.jpg)

**你的支持意味着：**
- 🔥 激励我开发更多实用功能
- 🐛 更快地修复问题和漏洞  
- 📚 编写更完善的文档和教程
- 🆕 持续更新和维护项目

**Your support means:**
- 🔥 Motivation to develop more useful features
- 🐛 Faster bug fixes and issue resolution
- 📚 Better documentation and tutorials
- 🆕 Continuous updates and maintenance

## 📄 许可证

MIT License

## 👨‍💻 作者

GuardSkill

---

## 常见问题 FAQ

**Q: 程序关闭后隧道会断开吗？**
A: 不会。最小化到托盘后隧道继续运行，只有点击"退出"才会关闭所有隧道。

**Q: 可以同时连接多个服务器吗？**
A: 可以。保存多个主机配置后，可以同时启动不同服务器的隧道。

**Q: 支持动态端口转发吗？**
A: 当前版本仅支持本地端口转发（-L）。

**Q: 配置文件可以导出吗？**
A: 配置文件位于用户主目录，可以手动备份 `.ssh_tunnel_config.json` 文件。

**Q: 打包后的程序体积较大？**
A: 这是正常的，包含了Python运行时和所有依赖库。可以使用 `--onedir` 参数生成目录形式的发布包以减小单文件大小。

---

**提示**：如需更详细的SSH隧道使用教程，请参考SSH官方文档。