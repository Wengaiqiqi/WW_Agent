#!/usr/bin/env python3
"""等待 Dify 启动并测试"""

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

        # 等待 API 容器健康
        print("\n--- 等待 API 容器健康 ---")
        for i in range(6):
            stdin, stdout, stderr = client.exec_command(  # nosec B601
                "docker ps --format '{{.Names}} {{.Status}}' | grep api-1",
                timeout=10
            )
            status = stdout.read().decode('utf-8', errors='ignore').strip()
            print(f"  [{i*5}s] {status}")
            if "healthy" in status:
                break
            time.sleep(5)

        # 检查 API 日志
        print("\n--- API 日志 ---")
        stdin, stdout, stderr = client.exec_command(  # nosec B601
            "docker logs docker-api-1 --tail 15 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 测试 API
        print("\n--- 测试 API ---")
        stdin, stdout, stderr = client.exec_command(  # nosec B601
            "curl -s http://localhost:5001/api/health --max-time 10 2>&1",
            timeout=15
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无响应")

        # 测试 Web
        print("\n--- 测试 Web ---")
        stdin, stdout, stderr = client.exec_command(  # nosec B601
            "curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 --max-time 5",
            timeout=10
        )
        print(f"HTTP 状态码: {stdout.read().decode('utf-8', errors='ignore').strip()}")

        # 测试外部访问
        print("\n--- 测试外部访问 ---")
        stdin, stdout, stderr = client.exec_command(  # nosec B601
            "curl -s -o /dev/null -w '%{http_code}' http://47.86.26.185:3001 --max-time 5",
            timeout=10
        )
        print(f"外部 HTTP 状态码: {stdout.read().decode('utf-8', errors='ignore').strip()}")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
