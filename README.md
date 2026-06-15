# Descrição

Este projeto regista os logs das máquinas do parque de máquinas.

# app.ini

O ficheiro app.ini é utilizado para definir diversas opções necessárias para o correto funcionamento do programa. No 
total, existem cinco opções: quatro de carácter obrigatório e uma opcional.

> Obrigatório:
- tool;
- workstation;
- url;
- logs_location.

> Opcional:
- line;
- allowed_workstations.

## tool

Deve ser a ferramenta que define qual o parser a ser utilizado para os logs. Uma das seguintes opções:

- AOI ALeader;
- AOI MEK;
- EOL STARK;
- EOL ZIV;
- BTF13;
- FCL0022: máquina "FCL0022" da linha ZIV.
 
## workstation: 

O posto de trabalho.

## url 

Url para pedidos api. Uma das seguintes opções (não é restritivo a estas opções e tenta enviar pedidos para qualquer 
url introduzido):
  - http://192.168.1.222:8600/ (Controlo de Produção);
  - http://192.168.1.222:7500/ (Uartracker).

## logs_location

Pasta onde estão os logs.

## date_start_logs

Data em que começaram a ser processados os logs. É automaticamente atribuído a esta variável o timestamp do primeiro 
arranque do programa.

## line

Utilizado somente para o Uartracker, ou seja, quando o url é http://192.168.1.222:7500/, e serve para
definir a respetiva linha. Atualmente existem três opções: PowerFlow; VersaFlow; e Vectra. Esta opção é de carácter 
opcional e pode permanecer vazia (para qualquer url utilizado) caso não seja necessária.

## allowed_workstations

Permite introduzir uma lista de vários postos. Quando esta variável está preenchida, ao fazer-se login, aparece um 
Dialog para o utilizador selecionar o posto que quer. Depois do utilizador selecionar o posto, a variável "workstation"
é atualizada com o valor escolhido (independetemente do que estava preenchido na mesma).

# Compilar

Depois de ser compilado com sucesso, o resultado final estará disponível na pasta "dist", presente no root do projeto.

## Numa máquina Windows para correr em Windows:

- Requisitos:
> N/A;

- Comandos (por ordem):
```bash
# assumindo que se está no root do projeto
pyinstaller main.spec
```

## Numa máquina Windows para correr em Linux/Raspberry Pi:

- Requisitos:
> Docker Desktop;

- Comandos (por ordem):
```bash
# assumindo que se está no root do projeto
cd compile_for_arm_architecture
# regista (ou re-regista) no host os intérpretes QEMU, o que permite executar binários/containers de 
# outras arquiteturas. Apenas é necessário executar este comando uma vez, caso ainda não o tenha feito ou tenha
# eliminado o container
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker-compose build
docker-compose up
```
# instalação

## Numa máquina Windows:

1. Copiar os conteúdos na pasta "dist" para o computador onde se deseja colocar a correr este programa;
2. Correr o programa uma primeira vez, isto irá gerar o ficheiro (app.ini), e fechar o programa;
3. Atualizar o ficheiro app.ini com as informações relevantes.

## Numa máquina Linux/Raspberry Pi:

1. Copiar os conteúdos na pasta "dist" para o computador onde se deseja colocar a correr este programa;
2. Configurar permissões dos ficheiros:
   1. Para permitir a execução do programa, é necessário para os ficheiros "Controlo de Produção" e 
   "Controlo de Produção.exe":
      1. Carregar com o lado direito do rato no ficheiro e escolher "properties";
      2. Aceder à aba "Permissions";
      3. Na seccão "Acess Control" alterar a opção "Execute" de "Nobody" para "Anyone"

3. Configurar o atalho do programa:
   1. Abrir o ficheiro "Controlo de Produção.exe" num editor de texto e atualizar as seguintes configurações:
      1. Exec: deve apontar para o ficheiro "Controlo de Produção" na pasta do programa. Deve estar entre aspas.
         Ex: "/home/USER1/Documents/Controlo de Produção/Controlo de Produção";
      2. Icon: deve ser o caminho para o icon logo-uartronica.png. Não deve estar entre aspas. O icon encontra-se no root da 
               pasta do programa então de acordo com exemplo acima o caminho seria: 
               /home/USER1/Documents/Controlo de Produção/logo-uartronica.png;
      3. Path: deve ser o caminho para a pasta do programa. Não deve estar entre aspas. Novamente de acordo com os exemplos 
                     acima, seria o seguinte caminho: /home/USER1/Documents/Controlo de Produção.

4. Mover o ficheiro "Controlo de Produção.exe" para o ambiente de trabalho do utilizador, para servir de atalho do 
programa.
5. Correr o programa uma primeira vez (duplo clique no atalho e selecionar execute), isto irá gerar o ficheiro (app.ini), 
e fechar o programa;
6. Atualizar o ficheiro app.ini com as informações relevantes.