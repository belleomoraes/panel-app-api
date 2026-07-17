from fastapi import FastAPI
from app.services.gene_service import GeneService
from app.clients.panelapp_client import PanelAppClient
from app.clients.ncbi_client import NcbiClient
from app.clients.emedgene_client import EmedgeneClient

app = FastAPI()

# 🔧 dependências (singleton simples)
panel_client = PanelAppClient()
ncbi_client = NcbiClient()
emedgene_client = EmedgeneClient()  # Adicione o cliente Emedgene se necessário
service = GeneService(panel_client, ncbi_client, emedgene_client)  # Adicione o cliente Emedgene se necessário


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

# 🔄 cadastra as listas de genes no Emedgene
@app.post("/emedgene/gene-lists")
def upload_gene_lists():
    return service.upload_gene_lists()