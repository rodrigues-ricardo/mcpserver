import json
import os

from prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
from netmiko import ConnectHandler
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("CiscoRouterManager", SYSTEM_PROMPT)

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'devices.json')

# =====================================================
# CARREGAR RESOURCE JSON
# =====================================================
try:
    with open(file_path, "r") as f:
        inventory = json.load(f)
except FileNotFoundError:
    print("Error: Arquivo não encontrado.")

# =====================================================
# CREDENCIAIS
# =====================================================

USERNAME = os.getenv("ROUTER_USERNAME")
PASSWORD = os.getenv("ROUTER_PASSWORD")
ENABLE = os.getenv("ROUTER_ENABLE")
PORT = os.getenv("PORT")

# =====================================================
# FUNÇÃO AUXILIAR
# =====================================================

def get_device(device_name):

    for device in inventory["devices"]:
        if device["name"] == device_name:
            return device

    return None



# =====================================================
# RESOURCE MCP
# =====================================================

@mcp.resource("network://devices")
def devices_resource():
    return inventory


@mcp.tool()
def analisar_dados(query: str):
    return f"Analisando: {query}"

# =====================================================
# TOOL - CONTAR EQUIPAMENTOS
# =====================================================

@mcp.tool()
def count_devices():

    total_devices = len(inventory["devices"])

    device_names = []

    for device in inventory["devices"]:
        device_names.append(device["name"])

    return {
        "status": "success",
        "total_devices": total_devices,
        "devices": device_names
    }



# =====================================================
# TOOL - LISTAR INTERFACES
# =====================================================

@mcp.tool()
def list_interfaces(device: str):

    router = get_device(device)

    if not router:
        return {
            "status": "error",
            "message": "Equipamento não encontrado"
        }

    return {
        "device": device,
        "interfaces": router["interfaces"]
    }

# =====================================================
# FUNÇÃO AUXILIAR - ATUALIZAR STATUS
# =====================================================

def update_interface_status(device_name, interface_name, new_status):

    for device in inventory["devices"]:

        if device["name"] == device_name:

            for interface in device["interfaces"]:

                if interface["name"] == interface_name:
                    interface["status"] = new_status

    with open(file_path, "w") as f:
        json.dump(inventory, f, indent=2)

# =====================================================
# TOOL - SHUTDOWN INTERFACE
# =====================================================

@mcp.tool()
def shutdown_interface(device: str, interface: str):

    router = get_device(device)

    if not router:
        return {
            "status": "error",
            "message": "Equipamento não encontrado"
        }

    connection = ConnectHandler(
        device_type="cisco_ios",
        host=router["host"],
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        secret=ENABLE,
    )
    connection.enable()
    commands = [
        f"interface {interface}",
        "shutdown"
    ]

    output = connection.send_config_set(commands)

    connection.disconnect()

    # Atualiza o JSON local
    update_interface_status(device, interface, "down")

    return {
        "status": "success",
        "action": "shutdown",
        "device": device,
        "interface": interface,
        "new_status": "down",
        "commands": commands,
        "output": output
    }

# =====================================================
# TOOL - NO SHUTDOWN
# =====================================================

@mcp.tool()
def enable_interface(device: str, interface: str):

    router = get_device(device)

    if not router:
        return {
            "status": "error",
            "message": "Equipamento não encontrado"
        }

    connection = ConnectHandler(
        device_type="cisco_ios",
        host=router["host"],
        username=USERNAME,
        password=PASSWORD,
        secret=ENABLE,
    )
    connection.enable()
    commands = [
        f"interface {interface}",
        "no shutdown"
    ]

    output = connection.send_config_set(commands)

    connection.disconnect()

    # Atualiza o JSON local
    update_interface_status(device, interface, "up")

    return {
        "status": "success",
        "action": "no shutdown",
        "device": device,
        "interface": interface,
        "new_status": "up",
        "commands": commands,
        "output": output
    }

# =====================================================
# TOOL - CONFIGURAR IP NA INTERFACE
# =====================================================

@mcp.tool()
def configure_interface_ip(
    device: str,
    interface: str,
    ip_address: str,
    subnet_mask: str
):

    router = get_device(device)

    if not router:
        return {
            "status": "error",
            "message": "Equipamento não encontrado"
        }

    try:

        connection = ConnectHandler(
            device_type="cisco_ios",
            host=router["host"],
            username=USERNAME,
            password=PASSWORD,
            secret=ENABLE,
        )
        connection.enable()

        commands = [
            f"interface {interface}",
            f"ip address {ip_address} {subnet_mask}",
            "no shutdown"
        ]

        output = connection.send_config_set(commands)

        connection.disconnect()

        # Atualiza o devices.json
        for dev in inventory["devices"]:

            if dev["name"] == device:

                for intf in dev["interfaces"]:

                    if intf["name"] == interface:

                        intf["ip_address"] = ip_address
                        intf["subnet_mask"] = subnet_mask
                        intf["status"] = "up"

        with open(file_path, "w") as f:
            json.dump(inventory, f, indent=2)

        return {
            "status": "success",
            "device": device,
            "interface": interface,
            "ip_address": ip_address,
            "subnet_mask": subnet_mask,
            "commands": commands,
            "output": output
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
    
# =====================================================
# START SERVER
# =====================================================
print ("servidor iniciado com sucesso!!")

if __name__ == "__main__":
    mcp.run()
