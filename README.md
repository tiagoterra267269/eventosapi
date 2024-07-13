# EventosApi

Projeto de API que tem como objetivo fornecer apis para gerenciamento de eventos. A aplicação possúi um DockerFile associado para sua execução.

# Como executar

Instale as dependências: (env)$ pip install -r requirements.txt;


Crie as imagens dos projetos:

> Crie a imagem do docker referente ao projeto controle de acesso docker build -t eventosapi .

Crie a rede:

docker network create mvp_network

Execute os containers conforme abaixo:

> docker run -d --name controledeacessoapi --network mvp_network -p 5000:5000 controledeacessoapi

> docker run -d --name eventos-web --network mvp_network -p 8080:80 eventos-web

> docker run -d --name eventosapi --network mvp_network -p 5001:5001 eventosapi

