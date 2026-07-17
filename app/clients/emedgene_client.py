# app/clients/emedgene_client.py

import requests
from app.config import EMEDGENE_BASE_URL, EMEDGENE_API_KEY

class EmedgeneClient:
    def __init__(self):
        self.base_url = EMEDGENE_BASE_URL.rstrip("/")

        self.headers = {
            "Authorization": f"Bearer {EMEDGENE_API_KEY}",
            "Content-Type": "application/json",
        }

    def create_gene_list(self, gene_list: dict):
        url = f"{self.base_url}/test_gene_list/create_new"

        response = requests.post(
            url,
            json=gene_list,
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()