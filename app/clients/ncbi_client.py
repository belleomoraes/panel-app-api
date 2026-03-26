# app/clients/ncbi_client.py
import json
import os
import time
import threading
import requests
from app.config import NCBI_BASE_URL, NCBI_API_KEY


class NcbiClient:
    def __init__(self):
        self.base_url = NCBI_BASE_URL
        self.api_key = NCBI_API_KEY

        self.cache_file = "gene_cache.json"
        self.cache = self._load_cache()

        self.lock = threading.Lock()
        self.last_call = 0

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def _rate_limit(self):
        elapsed = time.time() - self.last_call
        if elapsed < 0.11:
            time.sleep(0.11 - elapsed)
        self.last_call = time.time()

    def get_gene_id(self, gene_symbol: str):
        # 🔒 cache thread-safe
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

                # 💾 salva cache
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