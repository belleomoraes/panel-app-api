# 🧬 Gene Panel API

API desenvolvida para consumo e processamento de painéis de genes a partir do PanelApp, com integração a serviços externos como NCBI.

## 🚀 Objetivo

Fornecer uma API que permita:
- Buscar painéis de genes do PanelApp
- Processar e estruturar os dados
- Integrar informações adicionais de fontes externas (ex: NCBI)
- Servir como base para aplicações em genômica e doenças raras

---

## 🏗️ Arquitetura

O projeto segue uma separação em camadas:
```bash
app/

├── clients/ # Integração com APIs externas (PanelApp, NCBI)

├── services/ # Regras de negócio

├── routes/ (ou main.py) # Endpoints da API
```

### 🔌 Clients
Responsáveis por consumir APIs externas:
- `PanelAppClient`
- `NcbiClient`

### 🧠 Services
Contêm a lógica principal da aplicação:
- `GeneService`: orquestra chamadas entre clients e processa os dados

---

## ⚙️ Tecnologias utilizadas

- Python 3.10+
- FastAPI
- Uvicorn
- Requests / HTTPX (dependendo do que você estiver usando)

---

## ▶️ Como rodar o projeto

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS

# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação
```bash
uvicorn main:app --reload
```

---

## 📡 Endpoints
### 🔹 GET /panels

Retorna os painéis de genes obtidos do PanelApp, em cache

Exemplo de resposta:
```bash
[
  {
    "id": 1,
    "name": "Breast cancer panel",
    "genes": ["BRCA1", "BRCA2"]
  }
]
```

### 🔹 GET /panels/build

Retorna os painéis de genes obtidos do PanelApp, após processamento. *Tempo de processamento: ~45min*

Exemplo de resposta:
```bash
[
  {
    "id": 1,
    "name": "Breast cancer panel",
    "genes": ["BRCA1", "BRCA2"]
  }
]
```
---

## 🔄 Integrações
### 🧬 PanelApp
- Fonte principal de painéis de genes

### 🧪 NCBI
- Enriquecimento de dados genômicos
- Informações adicionais sobre genes

---

## 🧠 Próximos passos (Roadmap)
 - Implementar cache de requisições
 - Adicionar paginação nos endpoints
 - Criar endpoint para busca de genes específicos
 - Normalização e validação de dados
 - Integração com banco de dados
 - Autenticação e controle de acesso
 - Separação em painel GREEN e OTHERS
