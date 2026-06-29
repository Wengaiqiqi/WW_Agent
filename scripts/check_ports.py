#!/usr/bin/env python3
"""检查服务器端口冲突"""

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

        # 1. 检查所有监听端口
        print("\n--- 所有监听端口 ---")
        stdin, stdout, stderr = client.exec_command(
            "netstat -tlnp 2>/dev/null | sort -t: -k2 -n",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 检查关键端口
        print("\n--- 关键端口检查 ---")
        ports = [22, 3000, 3001, 5001, 5003, 5678, 8080, 8443]
        for port in ports:
            stdin, stdout, stderr = client.exec_command(
                f"netstat -tlnp 2>/dev/null | grep ':{port} ' || echo '端口 {port} 未使用'",
                timeout=5
            )
            output = stdout.read().decode('utf-8', errors='ignore').strip()
            if output and '未使用' not in output:
                print(f"  端口 {port}: {output}")
            else:
                print(f"  端口 {port}: 空闲")

        # 3. 检查 Docker 端口映射
        print("\n--- Docker 端口映射 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps --format '{{.Names}}: {{.Ports}}' 2>/dev/null | grep -v '^$'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 检查进程占用
        print("\n--- 进程占用端口 ---")
        stdin, stdout, stderr = client.exec_command(
            "netstat -tlnp 2>/dev/null | awk '{print $4, $7}' | grep -E ':(3000|3001|5001|5003|5678|8080|8443) ' | sort",
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
