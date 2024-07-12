# EventosApi

Serviço responsável para criação e manutenção de eventos: essa aplicação foi construída para ser consumida pelo [projeto eventosweb](https://github.com/TiagoTerra/eventosweb/tree/master).

# Pré-requisitos

1. Baixe e instale o [Python](https://www.python.org/downloads/)

2. Instalar os pacotes que a aplicação precisa (esses pacotes estão no arquivo [Requiements.txt](https://github.com/TiagoTerra/eventosapi/blob/master/Aplicacao/requirements.txt).
   Execute em um prompt a instrução abaixo:

       pip install -r requirements.txt

3. A aplicação usa o [sqlite](https://www.sqlite.org/download.html) como banco de dados. Já existe um banco de dados criado, mas caso queira criar um banco novo siga o passo a passo abaixo após instalação do sqlite
  3.1 - Crie um banco com o nome que vc desejar;
  3.2 -  Execute em um prompt ocomando abaixo para criar as tabelas da base de ddos e a carga básica de dados para  aplicação funcionar:

   sqlite3 (NOME DO BANCO QUE VOCÊ CRIOU)

   .read ScriptCriacaoBanco.sql

   clique [aqui](https://github.com/TiagoTerra/eventosapi/blob/master/Aplicacao/scripts/ScriptCriacaoBanco.txt) para visualizar o  ScriptCriacaoBanco.sql

5. Renomeie o nome do banco de dados [no arquivo init](https://github.com/TiagoTerra/eventosapi/blob/master/Aplicacao/model/__init__.py) para o nome do banco que você criou:

![image](https://github.com/TiagoTerra/eventosapi/assets/7558795/b728a93d-8fa6-43c2-86f4-f3aae9ce4aa6)

# Execução
   Execute o comando abaixo para rodar a aplicação:

  > flask run

# Construído com
   
   Aplicação desenvolvida usando o [vscode](https://code.visualstudio.com/) 

# Autores
Tiago Terra

# Apoio e agradecimentos

   Corpo docente e estudantil do curso de Especialização em Engenharia de Software e Especialização em Desenvolvimento FullStack, PUC-Rio 2024;

