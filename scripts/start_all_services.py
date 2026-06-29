#!/usr/bin/env python3
"""启动所有服务：hermes, A2A, W&W Agent 飞书 Gateway"""

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
        client.connect(hostname, 22, username, password, timeout=20, banner_timeout=30)
        print("[OK] SSH 连接成功")

        # 1. 启动 hermes-gateway
        print("\n--- 启动 hermes-gateway ---")
        stdin, stdout, stderr = client.exec_command(
            "cd /opt/hermes-agent && nohup /opt/hermes-agent/.venv/bin/python scripts/hermes-gateway > /tmp/hermes-gateway.log 2>&1 &",
            timeout=10
        )
        print("hermes-gateway 启动命令已执行")

        # 2. 启动 A2A 桥接
        print("\n--- 启动 A2A 桥接 ---")
        bridge_cmd = (
            "cd /root/.hermes-a2a/ww-agent && "
            "export HERMES_A2A_HMAC=6dba09d0abedddd61aa2f6efe6401386fca342204e4bbfbdf71c347f008bcf03 && "
            "export HERMES_A2A_MY_PEER_ID=hermes-home && "
            "export HERMES_A2A_ALLOWED_PEER=ww-agent && "
            "export HERMES_A2A_PORT=8080 && "
            "export HERMES_A2A_PUBLIC_HOST=47.86.26.185 && "
            "export HERMES_A2A_PUBLIC_PORT=8080 && "
            "export HERMES_ACP_CMD='/opt/hermes-agent/.venv/bin/python -m hermes_cli.main acp' && "
            "nohup python3 -c 'import uvicorn; from bridge.hermes_a2a import __main__; uvicorn.run(__main__.build(), host=\"0.0.0.0\", port=8080)' > /tmp/hermes-a2a.log 2>&1 &"
        )
        stdin, stdout, stderr = client.exec_command(bridge_cmd, timeout=10)
        print("A2A 桥接启动命令已执行")

        # 3. 启动 W&W Agent 飞书 Gateway (并发数 4)
        print("\n--- 启动 W&W Agent 飞书 Gateway (并发数 4) ---")
        gateway_cmd = """cd '/root/W&W Agent' && nohup env GATEWAY_MAX_CONCURRENCY=4 python3 -m gateway feishu > /root/feishu_gateway.log 2>&1 &"""
        stdin, stdout, stderr = client.exec_command(gateway_cmd, timeout=10)
        print("飞书 Gateway 启动命令已执行")

        # 4. 等待服务启动
        print("\n--- 等待服务启动 ---")
        time.sleep(8)

        # 5. 检查所有服务状态
        print("\n--- 服务状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep -E 'hermes-gateway|hermes_a2a|gateway.*feishu|uvicorn' | grep -v grep",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无相关进程")

        # 6. 检查端口
        print("\n--- 端口状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "netstat -tlnp 2>/dev/null | grep -E ':8080|:3001|:5001|:5678'",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "无端口监听")

        # 7. 检查日志
        print("\n--- hermes-gateway 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -5 /tmp/hermes-gateway.log 2>/dev/null || echo '日志不存在'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        print("\n--- hermes-a2a 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -5 /tmp/hermes-a2a.log 2>/dev/null || echo '日志不存在'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        print("\n--- 飞书 Gateway 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -10 /root/feishu_gateway.log 2>/dev/null || echo '日志不存在'",
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
