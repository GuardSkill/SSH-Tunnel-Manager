# SSH Tunnel Manager 打包指南

## 📦 打包方式

本项目提供了多种打包方式，您可以根据需要选择：

### 方式一：使用自动化脚本（推荐）

#### Windows
1. 双击运行 `build_windows.bat`
2. 等待打包完成
3. 可执行文件位于：`dist\SSHTunnelManager.exe`

#### Linux/macOS
1. 在终端运行：
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```
2. 等待打包完成
3. 可执行文件位于：`dist/SSHTunnelManager`

### 方式二：使用 spec 配置文件

```bash
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 使用 spec 文件打包
pyinstaller --clean ssh_tunnel_manager.spec
```

### 方式三：手动命令行打包

#### Windows
```cmd
pyinstaller --name="SSHTunnelManager" ^
            --windowed ^
            --onefile ^
            --clean ^
            ssh_tunnel_manager.py
```

#### Linux/macOS
```bash
pyinstaller --name="SSHTunnelManager" \
            --windowed \
            --onefile \
            --clean \
            ssh_tunnel_manager.py
```

## 🎨 添加自定义图标

1. 准备图标文件：
   - Windows: `icon.ico` (推荐尺寸：256x256)
   - macOS: `icon.icns`
   - Linux: `icon.png`

2. 在打包命令中添加参数：
   ```bash
   --icon=icon.ico
   ```

3. 或修改 `ssh_tunnel_manager.spec` 文件：
   ```python
   icon='icon.ico'  # 取消此行注释并指定图标路径
   ```

## 📊 打包参数说明

| 参数 | 说明 |
|------|------|
| `--name` | 指定生成的可执行文件名称 |
| `--windowed` | 不显示控制台窗口（GUI必需） |
| `--onefile` | 打包成单个可执行文件 |
| `--onedir` | 打包成目录（文件更小，启动更快） |
| `--icon` | 指定应用图标 |
| `--clean` | 清理临时文件 |
| `--noconsole` | 隐藏控制台（同--windowed） |
| `--add-data` | 添加额外数据文件 |
| `--hidden-import` | 显式导入模块 |

## 🔧 常见问题

### 1. 打包后程序无法运行

**可能原因**：缺少依赖或路径问题

**解决方法**：
```bash
# 使用 --onedir 模式调试
pyinstaller --onedir --windowed ssh_tunnel_manager.py

# 查看错误日志（在 dist 目录中）
```

### 2. 打包文件过大

**问题**：单文件模式生成的 exe 可能达到 50-100MB

**解决方法**：
- 使用 `--onedir` 模式（文件分散但总大小相同）
- 使用 `--exclude-module` 排除不需要的模块
- 使用 UPX 压缩（已在spec中启用）

示例：
```bash
pyinstaller --onedir \
            --exclude-module numpy \
            --exclude-module matplotlib \
            ssh_tunnel_manager.py
```

### 3. 打包后提示缺少模块

**解决方法**：在 spec 文件中添加隐藏导入
```python
hiddenimports=[
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.sip',  # 如果需要
],
```

### 4. Windows Defender 误报

**原因**：PyInstaller 打包的程序可能被误报为病毒

**解决方法**：
1. 添加到白名单
2. 使用代码签名证书
3. 在打包时使用 `--key` 参数加密

### 5. macOS 无法打开应用

**问题**：提示"无法验证开发者"

**解决方法**：
```bash
# 方法一：移除隔离属性
xattr -cr dist/SSHTunnelManager.app

# 方法二：在"安全性与隐私"中允许
```

## 📋 打包前检查清单

- [ ] 已安装 Python 3.7+
- [ ] 已安装 PyQt5：`pip install PyQt5`
- [ ] 已安装 PyInstaller：`pip install pyinstaller`
- [ ] 代码中没有硬编码的绝对路径
- [ ] 已测试程序功能正常
- [ ] （可选）准备好应用图标
- [ ] （可选）准备好许可证文件

## 🚀 打包流程

```
1. 安装依赖
   pip install -r requirements.txt
   pip install pyinstaller

2. 清理旧文件
   rm -rf build dist *.spec

3. 执行打包
   ./build_linux.sh      # Linux/macOS
   build_windows.bat     # Windows

4. 测试程序
   运行 dist/ 目录中的可执行文件

5. 分发程序
   将 dist/ 目录中的文件分发给用户
```

## 📦 分发建议

### 单文件模式（onefile）
- ✅ 优点：只有一个文件，方便分发
- ❌ 缺点：启动较慢（需要解压），文件较大

### 目录模式（onedir）
- ✅ 优点：启动快，便于调试
- ❌ 缺点：需要分发整个目录

### 推荐方案
1. 开发测试：使用 `--onedir` 模式
2. 最终发布：使用 `--onefile` 模式
3. 企业部署：使用 `--onedir` 并配置安装程序

## 🔒 高级选项

### 加密打包
```bash
pyinstaller --key="your-secret-key" ssh_tunnel_manager.py
```

### 添加版本信息（Windows）
```bash
pyinstaller --version-file=version.txt ssh_tunnel_manager.py
```

### 指定 UPX 路径
```bash
pyinstaller --upx-dir=/path/to/upx ssh_tunnel_manager.py
```

## 📝 打包后测试

1. **功能测试**
   - [ ] 程序能正常启动
   - [ ] 界面显示正常
   - [ ] SSH连接功能正常
   - [ ] 配置保存/加载正常
   - [ ] 系统托盘功能正常

2. **兼容性测试**
   - [ ] 在不同版本的操作系统上测试
   - [ ] 测试没有Python环境的机器
   - [ ] 测试不同权限下的运行

3. **性能测试**
   - [ ] 启动速度
   - [ ] 内存占用
   - [ ] CPU使用率

## 💡 优化建议

1. **减小体积**
   - 使用虚拟环境打包（只包含必要依赖）
   - 排除不需要的模块
   - 启用 UPX 压缩

2. **提高启动速度**
   - 使用 `--onedir` 模式
   - 优化导入语句（延迟导入）
   - 减少启动时的初始化操作

3. **提升用户体验**
   - 添加启动画面
   - 提供安装程序
   - 包含完整的 README
   - 提供卸载方式

## 📚 相关资源

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [PyQt5 文档](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [UPX 压缩工具](https://upx.github.io/)

---

**提示**：首次打包建议使用 `--onedir` 模式进行测试，确认无误后再使用 `--onefile` 模式生成最终版本。
