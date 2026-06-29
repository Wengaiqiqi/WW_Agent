#!/usr/bin/env python3
"""调试 Dify API 问题"""

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

        # 1. 检查 API 容器健康检查配置
        print("\n--- API 容器健康检查 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker inspect docker-api-1 --format '{{json .State.Health}}' | python3 -m json.tool",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 检查 API 容器内部的 /home/dify
        print("\n--- 容器内部 /home/dify ---")
        stdin, stdout, stderr = client.exec_command(
            "docker exec docker-api-1 ls -la /home/dify 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 检查 API 容器内部用户
        print("\n--- 容器内部用户 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker exec docker-api-1 id 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 测试 API 容器内部连接
        print("\n--- 容器内部 API 测试 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker exec docker-api-1 curl -s http://localhost:5001/api/health --max-time 5 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 检查 docker-compose 中的健康检查
        print("\n--- 健康检查配置 ---")
        stdin, stdout, stderr = client.exec_command(
            "grep -A5 'healthcheck' /opt/dify/docker/docker-compose.yaml | head -20",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 6. 检查端口映射
        print("\n--- API 端口映射 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker port docker-api-1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 7. 检查 docker-compose.override.yaml
        print("\n--- override.yaml ---")
        stdin, stdout, stderr = client.exec_command(
            "cat /opt/dify/docker/docker-compose.override.yaml",
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
