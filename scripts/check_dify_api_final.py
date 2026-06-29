#!/usr/bin/env python3
"""最终检查 Dify API"""

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
        print("\n--- 等待 30 秒 ---")
        time.sleep(30)

        # 1. 检查容器状态
        print("\n--- 容器状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'api-1|web-1'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 检查 API 日志
        print("\n--- API 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker logs docker-api-1 --tail 20 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 测试 API
        print("\n--- 测试 API ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://localhost:5001/health --max-time 10 2>&1",
            timeout=15
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无响应")

        # 4. 测试外部 API
        print("\n--- 测试外部 API ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://47.86.26.185:5001/health --max-time 10 2>&1",
            timeout=15
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无响应")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
