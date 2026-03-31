from fastapi import FastAPI
from app.services.gene_service import GeneService
from app.clients.panelapp_client import PanelAppClient
from app.clients.ncbi_client import NcbiClient

app = FastAPI()

# 🔧 dependências (singleton simples)
panel_client = PanelAppClient()
ncbi_client = NcbiClient()

service = GeneService(panel_client, ncbi_client)


# ⚡ pega do cache (rápido)
@app.get("/panels")
def get_panels():
    return service.get_cached_panels()


# 🔄 força rebuild (lento)
@app.post("/panels/build")
def build_panels():
    return service.build()

# 🔄 padroniza para cadastro de lista de genes no emedgene
@app.post("/panels/build-formatted")
def build_formatted_panels():
    return service.emedgene_formatted()