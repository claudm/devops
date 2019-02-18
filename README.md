Este é um pipeline de demonstração usando o docker
## Executar

antes de executar execute a instalação do docker

 curl -fsSL https://get.docker.com | sh;

 adicione o seu usuario ao grupo docker e faça logout login para usar o docker sem sudo ou use todos os comandos do docker com sudo

 sudo usermod -aG docker $USER

`` `
$ docker-compose up -d zalenium 
`` `
## aguardar terminar a instalação 

O zalenium demora um pouco para terminar a instalação acompanhe com

`` `$ docker logs -f zalenium`` `


`` `
$ docker-compose up -d
`` `

## O que esse pipeline contém?

- Jenkins 2.x
  - Inicialmente existe um usuário `admin / admin` criado
  - Os plug-ins são instalados e as dependências do plug-in são gerenciadas automaticamente pelo script `install-plugins.sh` fornecido no contêiner jenkins
  - O Maven 3.3.9 é instalado como uma ferramenta jenkins e recebe o nome `` M3``
  - Inicialmente, dois pipelines de demonstração são gerados usando scripts dinâmicos que são carregados na inicialização
- Registry do Docker para armazenar imagens do Docker
- Nexus 2.x para armazenar aplicativos java
- Zalenium com dois nodes para teste de  navegadores
  - Chrome
  - Firefox
- SonarQube para fazer análise estática no código


### Pipelines do Jenkins 2.x como código

A maneira preferida de construir pipelines no Jenkins 2.x é usar o `pipeline-plugin` que oferece aos usuários uma DSL semi-amigável para trabalhar. Jenkins 2.x oferece "Pipeline" como um novo tipo de trabalho.

Scripts de pipeline também podem ser recuperados do seu repositório git. Usar um `Jenkinsfile` em sua raiz git com a descrição do pipeline permite um pipeline multibranch.



### acessar o jenkins

localhost:8080


## acessar o sonar 

localhost:9000

## acessar o nexus

localhost:8081/nexus

### acessar o zalenium

localhost:4444/dashborad

### acessar a aplicação 

localhost:9966/petclinic

## acessar a api de contagem de tempo
##formato json
http://localhost/api/steps

##formato excel
http://localhost/api/steps?format=excel

##exportar para excel
http://localhost/api/steps?format=export


