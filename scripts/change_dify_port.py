#!/usr/bin/env python3
"""修改 Dify 端口配置"""

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

        # 1. 检查当前端口使用情况
        print("\n--- 当前端口使用 ---")
        stdin, stdout, stderr = client.exec_command(
            "netstat -tlnp | grep -E '3000|5001|5003' 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 查找 Dify docker-compose 文件
        print("\n--- 查找 Dify docker-compose ---")
        stdin, stdout, stderr = client.exec_command(
            "find /opt/dify -name 'docker-compose*.yml' -o -name '.env' 2>/dev/null | head -10",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 检查 Dify docker 目录
        print("\n--- Dify docker 目录 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /opt/dify/docker/ 2>/dev/null | head -20",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 检查 .env 文件
        print("\n--- Dify .env 配置 ---")
        stdin, stdout, stderr = client.exec_command(
            "cat /opt/dify/docker/.env 2>/dev/null | grep -E 'PORT|WEB|API' | head -20",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 检查 docker-compose.yml 中的端口配置
        print("\n--- docker-compose.yml 端口配置 ---")
        stdin, stdout, stderr = client.exec_command(
            "grep -A2 -B2 'ports:' /opt/dify/docker/docker-compose.yml 2>/dev/null | head -40",
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
