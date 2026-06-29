#!/usr/bin/env python3
"""检查 Dify 服务状态"""

import paramiko
import sys
import io

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

        # 1. 检查容器状态
        print("\n--- Docker 容器状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'dify|NAME'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 检查 API 日志
        print("\n--- API 容器日志 (最后20行) ---")
        stdin, stdout, stderr = client.exec_command(
            "docker logs docker-api-1 --tail 20 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 检查 Web 日志
        print("\n--- Web 容器日志 (最后20行) ---")
        stdin, stdout, stderr = client.exec_command(
            "docker logs docker-web-1 --tail 20 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 检查 nginx 日志
        print("\n--- Nginx 容器日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker logs docker-nginx-1 --tail 10 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 测试 API 内部连接
        print("\n--- 测试 API 内部连接 ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://localhost:5001/api/health --max-time 5 2>&1 || echo 'API 不可达'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 6. 测试 Web 内部连接
        print("\n--- 测试 Web 内部连接 ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://localhost:3001 --max-time 5 2>&1 | head -20",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 7. 检查 .env 中的 API URL 配置
        print("\n--- .env API URL 配置 ---")
        stdin, stdout, stderr = client.exec_command(
            "grep -E 'CONSOLE_API_URL|APP_API_URL|NEXT_PUBLIC' /opt/dify/docker/.env | head -10",
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
