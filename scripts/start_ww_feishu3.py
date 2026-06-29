#!/usr/bin/env python3
"""启动 W&W Agent 飞书 Gateway"""

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

        # 1. 检查 gateway 帮助
        print("\n--- Gateway 帮助 ---")
        stdin, stdout, stderr = client.exec_command(
            "cd '/root/W&W Agent' && python3 -m gateway feishu --help 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 检查配置文件
        print("\n--- 检查配置文件 ---")
        stdin, stdout, stderr = client.exec_command(
            "cat '/root/W&W Agent/.langchain-agent/settings.json' 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 检查 gateway 配置
        print("\n--- 检查 gateway 配置 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la '/root/W&W Agent/config/' 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 停止旧进程
        print("\n--- 停止旧进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "pkill -f 'gateway.*feishu' 2>/dev/null; pkill -f 'python.*gateway' 2>/dev/null; echo '已清理'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 启动飞书 Gateway
        print("\n--- 启动飞书 Gateway ---")
        cmd = """cd '/root/W&W Agent' && nohup python3 -m gateway feishu > /root/feishu_gateway.log 2>&1 &"""
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        print("启动命令已执行")

        # 6. 等待启动
        print("\n--- 等待启动 ---")
        time.sleep(5)

        # 7. 检查进程
        print("\n--- 检查进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep 'gateway.*feishu' | grep -v grep",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无相关进程")

        # 8. 检查日志
        print("\n--- Gateway 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -30 /root/feishu_gateway.log 2>/dev/null",
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
