#!/usr/bin/env python3
"""最终检查 Dify 状态"""

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

        # 等待容器完全启动
        print("\n--- 等待容器启动 ---")
        time.sleep(10)

        # 1. 检查容器状态
        print("\n--- 容器状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'dify|NAME'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 检查 API 日志
        print("\n--- API 日志 (最新) ---")
        stdin, stdout, stderr = client.exec_command(
            "docker logs docker-api-1 --tail 15 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 测试 API
        print("\n--- 测试 API ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://localhost:5001/api/health --max-time 5 2>&1",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无响应")

        # 4. 测试 Web
        print("\n--- 测试 Web ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 --max-time 5",
            timeout=10
        )
        print(f"HTTP 状态码: {stdout.read().decode('utf-8', errors='ignore').strip()}")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
