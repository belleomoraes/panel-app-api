# app/routes/panels.py

from fastapi import APIRouter, Depends
from app.clients.panelapp_client import PanelAppClient
from app.services.gene_service import GeneService

router = APIRouter()


def get_gene_service():
    panel_client = PanelAppClient()
    return GeneService(panel_client)

# 📚 pega do cache (rápido)
@router.get("/panels")
def get_panels(service: GeneService = Depends(get_gene_service)):
    return service.get_cached_panels()

# 🔄 força rebuild (lento)
@router.post("/panels/build")
def build_panels(service: GeneService = Depends(get_gene_service)):
    return service.build()

# 🔄 padroniza para cadastro de lista de genes no emedgene
@router.post("/panels/build-formatted")
def build_formatted_panels(service: GeneService = Depends(get_gene_service)):
    return service.emedgene_formatted()