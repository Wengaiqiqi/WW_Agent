#!/usr/bin/env python3
"""最终检查 Gateway 状态"""

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

        # 等待更长时间
        print("\n--- 等待 10 秒 ---")
        time.sleep(10)

        # 1. 检查进程
        print("\n--- 检查进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep 'gateway.*feishu' | grep -v grep",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无相关进程")

        # 2. 检查日志
        print("\n--- Gateway 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -30 /root/feishu_gateway.log 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 检查所有运行的服务
        print("\n--- 所有运行的服务 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep -E 'python|gateway|hermes|uvicorn' | grep -v grep | head -15",
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
