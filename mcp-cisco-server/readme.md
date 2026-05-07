# **Projeto MCP Server \- Cisco Interface Automation**

MCP Server usando Python para poder configurar  roteadores Cisco IOS através de linguagem natural usando **Claude IA**. Essa solução permite que um agente de IA, como o Claude, interprete solicitações operacionais feitas em português e execute automaticamente ações reais na infraestrutura de rede utilizando MCP Server \+ Netmiko.



 **Algumas funcionalidades implementadas:**

* Ativar e desativar interfaces;  
* Configurar endereço IP em interfaces;  
* Consultar interfaces e status operacional;  
* Verificar a quantidade de equipamentos no inventário da rede;  
* Atualização automática do inventário **devices.json** após mudanças.

Pontos importantes
* Instalação: Certifique-se de ter a biblioteca instalada: pip install netmiko.
* Configuração do Roteador: O roteador precisa ter ip domain-name,ip ssh version 2 ativo. Com chaves RSA geradas (crypto key generate rsa) e transport input ssh configurado nas VTY lines.
* Porta Alternativa: Se o SSH não estiver na porta 22, altere o valor do campo 'port' no dicionário.
* É essencial que, você altere o arquivo devices.json com as informações (hostname, IP de gerencia e interfaces) de acordo com seus roteadores.


Estrutura completa de um servidor MCP para automação de roteadores Cisco IOS utilizando:

·       MCP Python SDK
·       Netmiko
·       Resources em JSON
·       Interpretação de prompts
·       Tools para ativar/desativar interfaces

# **Estrutura do Projeto**

mcp-cisco-server/  
 │  
 ├── server.py  
 ├── devices.json  
 ├── requirements.txt  
 ├── prompts.py  
 ├── .env  
 └── README.md

# **requirements.txt**

 mcp  
 netmiko  
 python-dotenv

Componentes de Destaque

* Resources (@mcp.resource): A IA lê o devices.json para saber o estado atual antes de agir.  
* Prompts (@mcp.prompt): Define o comportamento de "Operador de Rede", restringindo o escopo e garantindo que o agente use as ferramentas corretamente.  
* Tools (@mcp.tool): são as função acionadas após a claude IA interpretar a linguagem natural ("ativar", "desativar", "down", "up") e traduz para ações.

- Arquivo responsável pelo contexto do agente de IA [**prompts.py**](http://prompts.py).  
- Arquivo resource **devices.json** é a base de dados, ele contém toda informação  estruturada  do inventário de equipamentos na rede , suas interfaces , o status e ip configurado nelas.  
- Arquivo [server.py](http://server.py) é o servidor MCP ele contem as tool , que são as funções contendo os comando do roteador que serão acionadas de acordo com a interpretação da claude IA.  
- Arquivo **.env** contem as variaveis de ambiente como usuários e senhas dos equipamentos

**Como Utilizar**

1.1- Você pode usar o teste_cisco.py para testar o funcionamento da biblioteca netmiko, é necessario apenas alterar o IP de gerencia do seu roteador e suas credenciais de acesso de acordo com seu ambiente.

1.2- Configurar no seu Cliente MCP (ex: Claude Desktop):  
Você precisa integrar seu server no cursor/claude. Para isso abra o arquivo de configuração **claude\_desktop\_config.json**  .  

Depois escolha a opção **desenvolvedor** e **Editar Config** Adicione a configuração abaixo :
Você deve arterar o caminho em "args": de acordo com o diretorio da sua máquina onde o projeto será salvo.

{  
  "mcpServers": {  
    "cisco-router": {  
      "command": "python",  
      "args": \["/caminho/para/cisco-mcp-server/server.py"\]  
    }  
  }  
}  

Após configurado o status do cursor configurado ficará **running**

**2- Rodar o servidor:**  
bash  
python [server.py](http://server.py)



**3 \- Fazer Pedido ao IA:**

Cenário em que o teste foi realizado.

"liste as interfaces do equipamento RT-DIST01."

“configure o ip 10.1.2.1 255.255.255.0 na interface fast0/0 do equipamento RT-DIST01”

“Quantos equipamentos eu tenho na rede?”



