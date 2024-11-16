import requests
import time

# URL của Floodlight REST API
BASE_URL = "http://127.0.0.1:8080"

# Hàm lấy danh sách các luồng từ switch
def get_flows():
    url = f"{BASE_URL}/wm/core/switch/all/flow/json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching flows:", response.status_code)
        return {}

# Hàm tính số kết nối hiện tại trên mỗi server
def get_least_connection_server(servers):
    server_connections = {server: 0 for server in servers}
    flows = get_flows()

    for switch_id, flow_data in flows.items():
        for flow in flow_data['flows']:
            if 'instructions' in flow:
                for instruction in flow['instructions']:
                    if instruction['type'] == 'OUTPUT':
                        out_port = instruction['port']
                        for server in servers:
                            if out_port == servers[server]:
                                server_connections[server] += 1

    # Chọn server có ít kết nối nhất
    return min(server_connections, key=server_connections.get)

# Hàm cài đặt rule cho switch
def install_rule(switch_id, in_port, out_port):
    url = f"{BASE_URL}/wm/staticflowpusher/json"
    data = {
        "switch": switch_id,
        "name": f"flow-{in_port}-{out_port}",
        "priority": 100,
        "in_port": str(in_port),
        "active": "true",
        "actions": f"output={out_port}"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"Installed rule: {data}")
    else:
        print("Error installing rule:", response.status_code, response.text)

# Danh sách server (địa chỉ IP: Cổng switch)
servers = {
    "10.0.0.1": 2,
    "10.0.0.2": 3
}

# Main loop
def main():
    while True:
        # Lấy server ít kết nối nhất
        selected_server = get_least_connection_server(servers)
        print("Selected server:", selected_server)

        # Cài đặt flow rule
        for switch_id in ["00:00:00:00:00:00:00:01"]:  # ID của switch
            install_rule(switch_id, in_port=1, out_port=servers[selected_server])

        # Chờ trước khi kiểm tra lại
        time.sleep(10)

if __name__ == "__main__":
    main()
