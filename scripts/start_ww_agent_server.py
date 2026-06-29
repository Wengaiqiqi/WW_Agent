#!/usr/bin/env python3
"""在服务器上启动 WW Agent 和飞书 Gateway"""

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

        # 1. 查找 WW Agent
        print("\n--- 查找 WW Agent ---")
        stdin, stdout, stderr = client.exec_command(
            "find /opt -name 'cli.py' -path '*agent*' 2>/dev/null | head -5",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "未找到 WW Agent")

        # 2. 查找 gateway
        print("\n--- 查找 gateway ---")
        stdin, stdout, stderr = client.exec_command(
            "find /opt -name '*.py' -path '*gateway*' 2>/dev/null | head -10",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "未找到 gateway")

        # 3. 检查 hermes-agent 目录
        print("\n--- 检查 hermes-agent 目录 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /opt/hermes-agent/gateway/ 2>/dev/null",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "目录不存在")

        # 4. 检查 WW Agent 是否在 hermes-agent 中
        print("\n--- 检查 WW Agent ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /opt/hermes-agent/*.py 2>/dev/null | head -10",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "未找到 Python 文件")

        # 5. 检查当前运行的进程
        print("\n--- 当前运行的进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep -E 'python|gateway|feishu' | grep -v grep | head -10",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无相关进程")

        # 6. 检查配置文件
        print("\n--- 检查配置文件 ---")
        stdin, stdout, stderr = client.exec_command(
            "cat /opt/hermes-agent/cli-config.yaml 2>/dev/null",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "配置文件不存在")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
