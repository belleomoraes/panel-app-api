import json
import os
import time
import threading
import requests
from typing import List, Dict, Optional
from Bio import Entrez

from app.config import NCBI_BASE_URL, NCBI_API_KEY


class NcbiClient:
    def __init__(self):
        self.base_url = NCBI_BASE_URL
        self.api_key = NCBI_API_KEY

        # 📧 obrigatório pro NCBI
        Entrez.email = "seu_email@exemplo.com"

        self.cache_file = "gene_cache.json"
        self.cache = self._load_cache()

        self.lock = threading.Lock()
        self.last_call = 0

    # ======================
    # 🔧 CACHE
    # ======================
    def _load_cache(self) -> Dict:
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    # ======================
    # ⏱️ RATE LIMIT
    # ======================
    def _rate_limit(self):
        elapsed = time.time() - self.last_call
        if elapsed < 0.11:  # ~9 req/s
            time.sleep(0.11 - elapsed)
        self.last_call = time.time()

    # ======================
    # 🧬 SINGLE GENE (preciso)
    # ======================
    def get_gene_id(self, gene_symbol: str) -> Optional[str]:
        # 🔒 cache
        with self.lock:
            if gene_symbol in self.cache:
                return self.cache[gene_symbol]

        for attempt in range(3):
            try:
                self._rate_limit()

                url = f"{self.base_url}/esearch.fcgi"
                params = {
                    "db": "gene",
                    "term": f"{gene_symbol}[gene] AND Homo sapiens[orgn]",
                    "retmode": "json"
                }

                if self.api_key:
                    params["api_key"] = self.api_key

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()
                ids = data.get("esearchresult", {}).get("idlist", [])
                gene_id = ids[0] if ids else None

                with self.lock:
                    self.cache[gene_symbol] = gene_id
                    self._save_cache()

                return gene_id

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    time.sleep((attempt + 1) * 1)
                else:
                    raise

        return None

    # ======================
    # 🚀 BATCH GENE (rápido)
    # ======================
    def get_gene_ids_batch(self, gene_symbols: list[str]) -> dict:
        gene_map = {}

        print(f"🧬 Iniciando batch NCBI para {len(gene_symbols)} genes")

        # 🔒 separa cache vs missing
        missing_genes = []

        with self.lock:
            for gene in gene_symbols:
                if gene in self.cache:
                    gene_map[gene] = self.cache[gene]
                else:
                    missing_genes.append(gene)

        print(f"💾 Cache hit: {len(gene_map)} | Miss: {len(missing_genes)}")

        if not missing_genes:
            return gene_map

        chunk_size = 30  # mais seguro pro NCBI

        for i in range(0, len(missing_genes), chunk_size):
            chunk = missing_genes[i:i + chunk_size]

            print(f"\n➡️ Chunk {i} - {i + len(chunk)} ({len(chunk)} genes)")

            query = " OR ".join([
                f"{gene}[gene] AND Homo sapiens[orgn]"
                for gene in chunk
            ])

            try:
                start = time.time()

                url = f"{self.base_url}/esearch.fcgi"
                params = {
                    "db": "gene",
                    "term": query,
                    "retmode": "json",
                    "retmax": len(chunk)
                }

                if self.api_key:
                    params["api_key"] = self.api_key

                response = requests.post(url, data=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                ids = data.get("esearchresult", {}).get("idlist", [])

                print(f"   🔎 IDs encontrados: {len(ids)}")
                print(f"   ⏱️ Tempo request: {time.time() - start:.2f}s")

                # ⚠️ mapping imperfeito → fallback depois
                for gene, gene_id in zip(chunk, ids):
                    gene_map[gene] = gene_id

            except Exception as e:
                print(f"   ❌ Erro no chunk: {e}")

        # 🔁 fallback (garante cobertura total)
        print("\n🔁 Iniciando fallback para genes não encontrados...")

        for gene in missing_genes:
            if gene not in gene_map:
                print(f"   ⚠️ Fallback: {gene}")
                gene_map[gene] = self.get_gene_id(gene)

        # 💾 salva cache
        with self.lock:
            for gene, gene_id in gene_map.items():
                self.cache[gene] = gene_id
            self._save_cache()

        print("\n🎯 Batch finalizado!")

        return gene_map