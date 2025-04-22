# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Gerenciador de Colheira de Cana de Açucar

## Kalil

## 👨‍🎓 Integrantes

- <a href="https://github.com/kalilReis">Kalil Reis de Sisto</a>

## 👩‍🏫 Professores

### Tutor(a)

- <a href="https://www.linkedin.com/company/inova-fusca">Leonardo Ruiz Orabona</a>

### Coordenador(a)

- <a href="https://www.linkedin.com/company/inova-fusca"> André Godoy acho</a>

## 📜 Descrição

Este projeto consiste em uma aplicação de linha de comando (CLI) desenvolvida em Python para gerenciar dados de colheita de cana-de-açúcar. A aplicação permite registrar informações detalhadas sobre cada colheita, incluindo área colhida, identificação da colhedora, total de toneladas colhidas e toneladas perdidas.

Os dados são armazenados em um banco de dados Oracle, e a aplicação calcula automaticamente o percentual de perda para cada registro. Além disso, oferece a funcionalidade de visualizar estatísticas agregadas, como o total de toneladas perdidas e o percentual médio de perda em todas as colheitas registradas, listar todos os registros individuais e importar dados em lote a partir de um arquivo JSON.

O objetivo é fornecer uma ferramenta simples e flexível para monitorar a eficiência da colheita e identificar potenciais áreas de melhoria na operação. A configuração da conexão com o banco de dados é feita através de variáveis de ambiente para maior segurança e flexibilidade.

## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>assets</b>: aqui estão os arquivos relacionados a elementos não-estruturados deste repositório, como imagens.

- <b>document</b>: aqui estão todos os documentos do projeto que as atividades poderão pedir. Na subpasta "other", adicione documentos complementares e menos importantes.

- <b>src</b>: Todo o código fonte criado para o desenvolvimento do projeto ao longo das 7 fases.

- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).

## 🔧 Como executar o código

**Pré-requisitos:**

- Python 3.x
- Oracle Database (com um usuário e schema configurados)
- Acesso à linha de comando/terminal

**Passos para execução:**

1.  **Clone o repositório:**

    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DA_PASTA_DO_PROJETO>
    ```

2.  **Crie um ambiente virtual:**

    ```bash
    python3 -m venv .venv
    ```

3.  **Ative o ambiente virtual:**

    - No Linux/macOS:
      ```bash
      source .venv/bin/activate
      ```
    - No Windows (Git Bash ou similar):
      ```bash
      source .venv/Scripts/activate
      ```
    - No Windows (Command Prompt):
      ```cmd
      .\.venv\Scripts\activate.bat
      ```
    - No Windows (PowerShell):
      ```powershell
      .\.venv\Scripts\Activate.ps1
      ```

4.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

    _(Se estiver usando o pip do ambiente virtual diretamente, como fizemos nos passos anteriores, pode usar `.venv/bin/pip install -r requirements.txt` no Linux/macOS ou o caminho equivalente no Windows)_

5.  **Configure as variáveis de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto com o seguinte conteúdo, substituindo os valores pelos dados da sua conexão Oracle:

    ```dotenv
    DB_USER=seu_usuario_oracle
    DB_PASSWORD=sua_senha_oracle
    DB_DSN=seu_dsn_oracle # Ex: localhost/FREEPDB1 ou host:porta/service_name
    ```

6.  **Execute o script principal:**
    ```bash
    python src/main.py
    ```
    _(Se o ambiente virtual não estiver ativo no seu terminal atual, use o caminho completo: `.venv/bin/python src/main.py` no Linux/macOS ou o equivalente no Windows)_

## 🗃 Histórico de lançamentos

- ## 0.5.0 - XX/XX/2024

- ## 0.4.0 - XX/XX/2024

- ## 0.3.0 - XX/XX/2024

- ## 0.2.0 - XX/XX/2024

- ## 0.1.0 - XX/XX/2024

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
