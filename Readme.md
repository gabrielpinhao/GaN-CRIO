interface+controle é o programa "completo"
fonteobjeto esta a classe da fonte e suas funcoes

poderiamos fazer esse arquivo como explicação das funcionalidades de cada arquivo no repositorio

1. Codigo_Controle_Fonte: Priemiro arquivo que fez conexão e controlou a fonte 6680A

2. Conexaofonte: Testar somente a conexão (podemos remover do Git)

3. Correntevi: Codigo em LabView de controle (colocar em uma pasta de VIs)

4. fonteobjeto: Tem todos os comandos e conexao com a classe da fonte 6680A

5. interface_gp: primeira interface

6. interface_manual: prototipo da interface(deletar)

7. interface+controle: programa completo
observaçoes: mudar variaveis para tk.StringVar() para acessa mais facil dos valores

8. main: verificar

Canal de Comunicação
# (use este espaço para ideias e atualizaçoes e problemas) 
# (use este espaço para ideias e atualizaçoes e problemas) 
# (use este espaço para ideias e atualizaçoes e problemas) 

Documentação

1. interface+controle, se encontra o projeto completo, de certa forma, sendo baseado sua interface visual na biblioteca nativa do python tkinter. Para poder operar a interface em conjunto com os comandos que desejam operar simultaneamente a fonte, utilizase a biblioteca threading, tambem nativa a liguagem python, permitindo que a interface não “congele” enquanto os comandos sao executados, desde controles a medidores. ja as seguintes bibliotecas serao responsáveis por importar codigos como os responsáveis pelo controle da fonte e o controle para os medidores.