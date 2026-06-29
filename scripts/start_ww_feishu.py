#!/usr/bin/env python3
"""启动 W&W Agent 和飞书 Gateway"""

import paramiko
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    hostname = "47.86.26.185"
    username = "root"
    password = "Ydmy5247."

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接到 {hostname}...")
        client.connect(hostname, 22, username, password, timeout=15, banner_timeout=30)
        print("[OK] SSH 连接成功")

        # 1. 检查 W&W Agent 目录
        print("\n--- W&W Agent 目录 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la '/root/W&W Agent/' | head -20",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 检查 gateway 目录
        print("\n--- Gateway 目录 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la '/root/W&W Agent/gateway/' 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 检查是否有 venv
        print("\n--- 检查 venv ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la '/root/W&W Agent/.venv/bin/' 2>/dev/null | head -10",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 检查 gateway 启动命令
        print("\n--- 检查 gateway 启动方式 ---")
        stdin, stdout, stderr = client.exec_command(
            "grep -r 'feishu' '/root/W&W Agent/gateway/' 2>/dev/null | head -5",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 检查配置文件
        print("\n--- 检查配置文件 ---")
        stdin, stdout, stderr = client.exec_command(
            "cat '/root/W&W Agent/.langchain-agent/settings.json' 2>/dev/null | head -30",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 6. 停止旧的 gateway 进程
        print("\n--- 停止旧的 gateway 进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "pkill -f 'gateway.*feishu' 2>/dev/null; echo '旧进程已清理'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 7. 启动飞书 Gateway (并发数 4)
        print("\n--- 启动飞书 Gateway (并发数 4) ---")
        cmd = """cd '/root/W&W Agent' && nohup .venv/bin/python -m gateway feishu --concurrency 4 > /root/feishu_gateway.log 2>&1 &"""
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        print("启动命令已执行")

        # 8. 等待启动
        print("\n--- 等待启动 ---")
        time.sleep(3)

        # 9. 检查进程
        print("\n--- 检查进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep -E 'gateway.*feishu|ww.*agent' | grep -v grep",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无相关进程")

        # 10. 检查日志
        print("\n--- Gateway 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -20 /root/feishu_gateway.log 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
