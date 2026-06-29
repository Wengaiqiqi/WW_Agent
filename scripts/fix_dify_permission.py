#!/usr/bin/env python3
"""修复 Dify 权限问题"""

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

        # 1. 检查所有容器状态
        print("\n--- 所有容器状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 检查 /home/dify 权限
        print("\n--- /home/dify 权限 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /home/ | grep dify",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 修复权限 - 递归设置
        print("\n--- 修复权限 ---")
        stdin, stdout, stderr = client.exec_command(
            "chmod -R 777 /home/dify && chown -R 1000:1000 /home/dify && echo '权限已修复'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 重启所有 Dify 容器
        print("\n--- 重启所有 Dify 容器 ---")
        stdin, stdout, stderr = client.exec_command(
            "cd /opt/dify/docker && docker compose restart",
            timeout=120
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output[-500:] if len(output) > 500 else output)

        # 5. 等待容器启动
        print("\n--- 等待容器启动 ---")
        stdin, stdout, stderr = client.exec_command(
            "sleep 15",
            timeout=20
        )
        stdout.read()

        # 6. 检查容器状态
        print("\n--- 容器状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | head -15",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 7. 检查 API 日志
        print("\n--- API 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker logs docker-api-1 --tail 10 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 8. 测试 API
        print("\n--- 测试 API ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://localhost:5001/api/health --max-time 5 2>&1 || echo 'API 不可达'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 9. 测试 Web
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
