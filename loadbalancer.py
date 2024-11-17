import requests
import time
import json

# Floodlight REST API base URL
BASE_URL = "http://127.0.0.1:8080/wm"

# Function to get the link statistics
def get_link_statistics():
    url = f"{BASE_URL}/statistics/packet/1/json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch link stats: {response.status_code}")
        return None

# Function to get host information
def get_host_info():
    url = f"{BASE_URL}/device/json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch host info: {response.status_code}")
        return None

# Function to get switch port information
def get_switch_ports(switch_id):
    url = f"{BASE_URL}/switches/{switch_id}/ports/json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch switch ports: {response.status_code}")
        return None

# Function to calculate the best path based on link statistics
def calculate_best_path(link_stats):
    # Assuming link_stats is a dictionary with switch link data
    # Sort by TX (transmission) rate to find the best link
    sorted_links = sorted(link_stats, key=lambda x: x['txbytes'], reverse=True)
    return sorted_links[0]  # Best link based on TX

# Function to install flow based on best path
def install_flow(src_ip, dst_ip, src_mac, dst_mac, in_port, out_port):
    flow = {
        "name": f"flow_{src_ip}_{dst_ip}",
        "cookie": "0",
        "priority": 32768,
        "in_port": in_port,
        "eth_src": src_mac,
        "eth_dst": dst_mac,
        "eth_type": 0x0800,
        "ip_src": src_ip,
        "ip_dst": dst_ip,
        "active": True,
        "actions": [
            {"type": "OUTPUT", "port": out_port}
        ]
    }
    url = f"{BASE_URL}/staticflowpusher/push"
    response = requests.post(url, data=json.dumps(flow), headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        print(f"Flow installed for {src_ip} -> {dst_ip}")
    else:
        print(f"Failed to install flow: {response.status_code}")

# Function to get neighbors of a given host
def get_host_neighbors(host_id):
    url = f"{BASE_URL}/device/{host_id}/json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch neighbors for {host_id}: {response.status_code}")
        return None

# Function to dynamically discover in-port and out-port based on topology
def discover_ports(src_ip, dst_ip, host_info):
    src_mac, dst_mac = None, None
    in_port, out_port = None, None

    for device_id, device_info in host_info.items():
        for host in device_info:
            if host["host"] == src_ip:  # Matching source host
                src_mac = host["mac"]
                in_port = host["port"]  # Example: get the port of source host
            if host["host"] == dst_ip:  # Matching destination host
                dst_mac = host["mac"]
                out_port = host["port"]  # Example: get the port of destination host

    return in_port, out_port, src_mac, dst_mac

# Main function for dynamic load balancing
def dynamic_load_balancing():
    # Get user input for source and destination hosts
    host1 = input("Enter source host (e.g., 1 for H1): ")
    host2 = input("Enter destination host (e.g., 4 for H4): ")

    # Get the IP addresses and MAC addresses of the selected hosts
    host_info = get_host_info()
    if not host_info:
        print("Unable to fetch host information.")
        return

    src_ip = f"10.0.0.{host1}"
    dst_ip = f"10.0.0.{host2}"

    # Discover ports dynamically
    in_port, out_port, src_mac, dst_mac = discover_ports(src_ip, dst_ip, host_info)

    if not in_port or not out_port:
        print("Unable to find matching ports.")
        return

    while True:
        print("Collecting link statistics...")
        link_stats = get_link_statistics()
        if link_stats:
            best_link = calculate_best_path(link_stats)
            print(f"Best path: {best_link}")

            # Install the flow based on the best path
            install_flow(src_ip, dst_ip, src_mac, dst_mac, in_port, out_port)
        
        time.sleep(60)  # Update every minute

if __name__ == "__main__":
    dynamic_load_balancing()
