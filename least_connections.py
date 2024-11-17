import requests
import time

# URL của Floodlight REST API
BASE_URL = "http://127.0.0.1:8080"

# Hàm lấy danh sách các switch từ Floodlight
def get_switches():
    url = f"{BASE_URL}/wm/core/switch/all/json"
    response = requests.get(url)
    if response.status_code == 200:
        return [switch['switchDPID'] for switch in response.json()]
    else:
        print("Error fetching switches:", response.status_code)
        return []

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
                for instructions in flow['instructions']:
                    if isinstance(instructions, dict) and 'instruction_apply_actions' in instructions:
                        actions = instructions['instruction_apply_actions']['actions']
                        for action in actions.split(','):
                            if action.startswith("output="):
                                out_port = action.split('=')[1]
                                for server, server_port in servers.items():
                                    if str(server_port) == out_port:
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
        print(f"Installed rule on {switch_id}: {data}")
    else:
        print("Error installing rule:", response.status_code, response.text)

# Danh sách server (địa chỉ IP: Cổng switch)
servers = {
    "10.0.0.1": 2,
    "10.0.0.2": 3,
    "10.0.0.3": 4,
    "10.0.0.4": 5,
    "10.0.0.5": 6
}

# Main loop
def main():
    while True:
        # Lấy server ít kết nối nhất
        selected_server = get_least_connection_server(servers)
        print("Selected server:", selected_server)

        # Lấy danh sách các switch từ Floodlight
        switches = get_switches()

        # Cài đặt flow rule cho mỗi switch
        for switch_id in switches:
            print(f"Installing rule on switch: {switch_id}")
            install_rule(switch_id, in_port=1, out_port=servers[selected_server])

        # Chờ trước khi kiểm tra lại
        time.sleep(10)

if __name__ == "__main__":
    main()
