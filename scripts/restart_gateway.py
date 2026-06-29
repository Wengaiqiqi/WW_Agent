#!/usr/bin/env python3
"""重启飞书 Gateway (并发数 4)"""

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

        # 1. 停止旧进程
        print("\n--- 停止旧进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "pkill -f 'gateway.*feishu' 2>/dev/null; sleep 1; echo '已清理'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 启动 Gateway (并发数 4)
        print("\n--- 启动 Gateway (GATEWAY_MAX_CONCURRENCY=4) ---")
        cmd = """cd '/root/W&W Agent' && nohup env GATEWAY_MAX_CONCURRENCY=4 python3 -m gateway feishu > /root/feishu_gateway.log 2>&1 &"""
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        print("启动命令已执行")

        # 3. 等待启动
        print("\n--- 等待启动 ---")
        time.sleep(5)

        # 4. 检查进程
        print("\n--- 检查进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep 'gateway.*feishu' | grep -v grep",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无相关进程")

        # 5. 检查日志
        print("\n--- Gateway 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -20 /root/feishu_gateway.log 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 6. 验证并发数
        print("\n--- 验证并发数 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep 'GATEWAY_MAX_CONCURRENCY' | grep -v grep",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "未找到并发数配置")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
