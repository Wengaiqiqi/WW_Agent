#!/usr/bin/env python3
"""修复 Dify API 权限问题"""

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

        # 1. 检查 /home/dify 目录
        print("\n--- 检查 /home/dify 目录 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /home/dify 2>/dev/null || echo '目录不存在'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 创建 /home/dify 目录并设置权限
        print("\n--- 修复权限 ---")
        stdin, stdout, stderr = client.exec_command(
            "mkdir -p /home/dify && chmod 777 /home/dify && echo '权限已修复'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 重启 API 容器
        print("\n--- 重启 API 容器 ---")
        stdin, stdout, stderr = client.exec_command(
            "cd /opt/dify/docker && docker compose restart api worker worker_beat api_websocket",
            timeout=60
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "重启命令已执行")

        # 4. 等待容器启动
        print("\n--- 等待容器启动 ---")
        stdin, stdout, stderr = client.exec_command(
            "sleep 5 && docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'api|worker'",
            timeout=15
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 检查 API 日志
        print("\n--- API 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker logs docker-api-1 --tail 10 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 6. 测试 API
        print("\n--- 测试 API ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://localhost:5001/api/health --max-time 5 2>&1 || echo 'API 不可达'",
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
