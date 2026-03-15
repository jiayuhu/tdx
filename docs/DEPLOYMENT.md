# TDX 部署指南 (DEPLOYMENT.md)

## 目录
1. [环境准备](#1-环境准备)
2. [安装部署](#2-安装部署)
3. [配置说明](#3-配置说明)
4. [服务管理](#4-服务管理)
5. [监控维护](#5-监控维护)
6. [备份恢复](#6-备份恢复)
7. [故障处理](#7-故障处理)

---

## 1. 环境准备

### 1.1 硬件要求

**最小配置**:
- CPU: 2核
- 内存: 4GB
- 磁盘: 50GB SSD
- 网络: 10Mbps

**推荐配置**:
- CPU: 4核及以上
- 内存: 8GB及以上
- 磁盘: 100GB SSD
- 网络: 100Mbps

### 1.2 软件依赖

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Windows | 10/11 或 Server 2019+ | 操作系统 |
| Python | 3.14+ | 运行环境 |
| 通达信客户端 | 最新版 | 数据源 |
| uv | 最新版 | 依赖管理工具 |

### 1.3 端口要求

| 服务 | 端口 | 用途 |
|------|------|------|
| Web服务 | 5000 | HTTP接口 |
| TQ API | 动态 | 通达信通信 |
| SQLite | 无 | 本地数据库 |

---

## 2. 安装部署

### 2.1 全新安装流程

#### 步骤1: 克隆代码
```bash
git clone <repository-url>
cd tdx
```

#### 步骤2: 安装依赖
```bash
# 安装 uv (如果未安装)
pip install uv

# 安装项目依赖
uv sync
```

#### 步骤3: 配置环境
```bash
# 复制配置模板
copy config.yaml.example config.yaml

# 编辑配置文件
notepad config.yaml
```

#### 步骤4: 初始化数据库
```bash
# 首次运行会自动创建数据库
uv run python xg.py --list
```

#### 步骤5: 启动服务
```bash
# 启动 Web 服务（项目根目录）
.\start_web.bat
```

### 2.2 通达信客户端配置

1. **安装通达信**
   - 下载并安装最新版通达信客户端
   - 完成登录和初始化

2. **配置路径**
   ```yaml
   # config.yaml
   tdx_root: "D:\\通达信安装路径\\new_tdx64"
   ```

3. **创建选股公式**
   - 按照 [SKILLS.md](SKILLS.md) 中的说明创建所需公式
   - 确保公式名称与配置文件一致

### 2.3 Web服务部署

#### Web 服务启动（当前实现）
```bat
:: start_web.bat
@echo off
cd /d "%~dp0web"
echo 启动 TDX Web 服务...
dotnet run --urls "http://localhost:5000"
```

---

## 3. 配置说明

### 3.1 核心配置项

```yaml
# config.yaml

# 通达信安装路径
tdx_root: "D:\\App\\new_tdx64"

# TQ 操作延时(毫秒)
tq_delay_ms: 500

# 选股策略配置
xg_programs:
  # 策略定义...
```

### 3.2 环境变量配置

```env
# .env (可选)
TDX_ROOT=D:\App\new_tdx64
LOG_LEVEL=INFO
DATABASE_PATH=./data/quant.db  # 运行时自动创建；data/ 目录不提交到 Git
```

### 3.3 多环境配置

```bash
# 开发环境
cp config.dev.yaml config.yaml

# 生产环境
cp config.prod.yaml config.yaml
```

---

## 4. 服务管理

### 4.1 启动服务

```bash
# 启动选股服务
uv run python xg.py

# 启动 Web 服务（项目根目录）
.\start_web.bat

# 后台运行
Start-Process -FilePath "uv" -ArgumentList "run", "python", "xg.py" -WindowStyle Hidden
```

### 4.2 停止服务

```bash
# Windows 任务管理器中结束进程
# 或使用 PowerShell
Stop-Process -Name python -Force
```

### 4.3 服务状态检查

```bash
# 检查 TQ 连接
uv run python -c "from base import get_tq; print('TQ状态:', get_tq() is not None)"

# 检查数据库
uv run python dbview.py --tables

# 检查 Web 服务
curl http://localhost:5000/
```

### 4.4 Windows 服务注册 (可选)

```powershell
# 创建服务
New-Service -Name "TDXSelector" -BinaryPathName "C:\path\to\start_web.bat" -StartupType Automatic

# 启动服务
Start-Service TDXSelector

# 停止服务
Stop-Service TDXSelector
```

---

## 5. 监控维护

### 5.1 日志监控

```bash
# 实时查看日志
Get-Content xg.log -Wait

# 按级别过滤
Select-String -Path xg.log -Pattern "ERROR"

# 日志轮转配置
# logging.conf
{
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "xg.log",
            "maxBytes": 10485760,
            "backupCount": 5
        }
    }
}
```

### 5.2 性能监控

```python
# 性能监控脚本 monitor.py
import psutil
import time

def monitor_system():
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('.').percent
        
        print(f"CPU: {cpu}% | 内存: {memory}% | 磁盘: {disk}%")
        time.sleep(60)

if __name__ == "__main__":
    monitor_system()
```

### 5.3 健康检查脚本

```bash
#!/bin/bash
# health_check.sh

# 检查进程
if ! pgrep -f "python xg.py" > /dev/null; then
    echo "选股服务未运行"
    exit 1
fi

# 检查数据库
if ! sqlite3 data/quant.db "SELECT 1;" > /dev/null; then
    echo "数据库连接失败"
    exit 1
fi

# 检查磁盘空间
if [ $(df . | awk 'NR==2 {print $5}' | sed 's/%//') -gt 90 ]; then
    echo "磁盘空间不足"
    exit 1
fi

echo "系统健康"
exit 0
```

---

## 6. 备份恢复

### 6.1 数据备份

```bash
# 数据库备份脚本 backup.sh
#!/bin/bash

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/quant_$DATE.db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp ./data/quant.db $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 清理旧备份 (保留7天)
find $BACKUP_DIR -name "quant_*.db.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_FILE.gz"
```

### 6.2 配置备份

```bash
# 备份配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz config.yaml *.bat
```

### 6.3 数据恢复

```bash
# 恢复数据库
gunzip backup.db.gz
cp backup.db ./data/quant.db

# 验证恢复
uv run python dbview.py --tables
```

### 6.4 自动备份计划

```powershell
# Windows 计划任务
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\tdx\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
Register-ScheduledTask -TaskName "TDXBackup" -Action $action -Trigger $trigger
```

---

## 7. 故障处理

### 7.1 常见问题及解决方案

#### TQ 初始化失败
```bash
# 检查项
1. 通达信客户端是否运行
2. 配置路径是否正确
3. 是否有其他程序占用 TQ

# 解决方案
- 重启通达信客户端
- 检查 config.yaml 中的 tdx_root 路径
- 关闭其他 Python 脚本
```

#### 数据库锁定
```bash
# 检查占用进程
lsof ./data/quant.db

# 解决方案
- 等待其他操作完成
- 重启服务
- 检查是否有未关闭的数据库连接
```

#### 选股结果异常
```bash
# 排查步骤
1. 检查通达信公式是否存在
2. 验证公式名称是否匹配
3. 查看日志中的错误信息
4. 手动在通达信中测试公式

# 调试命令
uv run python xg.py --strategy problematic_strategy --debug
```

### 7.2 应急恢复流程

```bash
# 1. 停止服务
taskkill /f /im python.exe

# 2. 恢复备份
cp backups/quant_latest.db ./data/quant.db

# 3. 检查配置
diff config.yaml config.backup.yaml

# 4. 重启服务
.\start_web.bat
```

### 7.3 性能优化

```bash
# 清理数据库碎片
sqlite3 data/quant.db "VACUUM;"

# 优化索引
sqlite3 data/quant.db "ANALYZE;"

# 清理日志文件
Remove-Item *.log -Force
```

---

## 附录

### A. 部署检查清单

- [ ] 硬件资源配置完成
- [ ] 操作系统和依赖软件安装完成
- [ ] 通达信客户端安装并登录
- [ ] 项目代码部署完成
- [ ] 配置文件正确设置
- [ ] 选股公式创建完成
- [ ] 数据库初始化完成
- [ ] 服务启动测试通过
- [ ] 监控告警配置完成
- [ ] 备份策略制定并测试

### B. 版本升级流程

```bash
# 1. 备份当前版本
tar -czf tdx_backup_$(date +%Y%m%d).tar.gz .

# 2. 拉取新版本
git pull origin master

# 3. 更新依赖
uv sync

# 4. 验证配置兼容性
python validate_config.py

# 5. 重启服务
.\start_web.bat
```

### C. 安全加固建议

1. **文件权限**
   ```bash
   # 限制数据库文件访问
   chmod 600 data/quant.db
   ```

2. **网络隔离**
   - Web服务绑定内网IP
   - 配置防火墙规则

3. **日志审计**
   - 启用详细日志记录
   - 定期审查日志文件
