import requests
import json
import time

# Địa chỉ API của Floodlight
floodlight_url = "http://127.0.0.1:8080/stats/flow"
floodlight_add_url = "http://127.0.0.1:8080/wm/staticflowentrypusher/addentry/json"

def get_switch_stats():
    """Lấy thông tin về kết nối từ các switch"""
    response = requests.get(floodlight_url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Không thể lấy thông tin từ Floodlight.")
        return None

def least_connection_switch(stats):
    """Chọn switch có ít kết nối nhất"""
    min_connections = float('inf')
    chosen_switch = None
    for switch, flows in stats.items():
        active_connections = sum(flow['packetCount'] for flow in flows.values())
        if active_connections < min_connections:
            min_connections = active_connections
            chosen_switch = switch
    return chosen_switch

def add_flow_rule(switch, in_port, out_port, priority=100):
    """Thêm flow rule vào switch trong Floodlight"""
    flow_entry = {
        "switch": switch,  # Switch mà bạn muốn thêm flow rule
        "name": f"flow_rule_{switch}",
        "cookie": "0",
        "priority": priority,
        "in_port": in_port,
        "actions": f"output={out_port}"  # Đưa lưu lượng đến cổng output
    }
    
    response = requests.post(floodlight_add_url, data=json.dumps(flow_entry), headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        print(f"Flow rule đã được thêm vào switch {switch}.")
    else:
        print(f"Không thể thêm flow rule vào switch {switch}.")

def load_balancing():
    """Thuật toán cân bằng tải với Least Connection"""
    while True:
        stats = get_switch_stats()  # Lấy thông tin từ Floodlight
        if stats:
            # Xác định switch có ít kết nối nhất
            switch = least_connection_switch(stats)
            print(f"Switch có ít kết nối nhất là: {switch}")

            # Cập nhật flow rule để phân phối lưu lượng tới switch ít kết nối
            # Giả sử chúng ta đang thay đổi flow cho switch và chọn cổng đầu vào và cổng đầu ra.
            add_flow_rule(switch, in_port=1, out_port=2)  # Ví dụ cổng in_port=1, out_port=2

        time.sleep(5)

if __name__ == "__main__":
    load_balancing()
