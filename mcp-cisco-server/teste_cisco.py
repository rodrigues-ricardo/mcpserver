from netmiko import ConnectHandler

# Dicionário de configuração do dispositivo
cisco_router = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.155',  # IP do roteador
    'username': 'cisco',
    'password': 'password123',
    'port': 22,             # Porta SSH padrão
    'secret': 'password123', # Senha de 'enable' se necessário
}

try:
    # Estabelece a conexão
    print("Conectando ao dispositivo...")
    net_connect = ConnectHandler(**cisco_router)
    
    # Entra no modo enable (privilegiado)
    net_connect.enable()
    print("Conectando com sucesso!")
    # Envia um comando
    output1 = net_connect.send_command('show ver | i uptime')
    output2 = net_connect.send_command('show ip int brief')
    print(output1)
    print(output2)
    
    # Desconecta
    net_connect.disconnect()
    print("scrip finalizado....Conexão encerrada.")

except Exception as e:
    print(f"Erro ao conectar: {e}")