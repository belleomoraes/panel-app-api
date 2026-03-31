# app/clients/panelapp_client.py
import requests
import time
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.config import PANEL_APP_BASE_URL, PANEL_APP_TOKEN

# arquivos de cache
NCBI_CACHE_FILE = "ncbi_cache.json"
PANELS_CACHE_FILE = "panels_with_genes_cache.json"
OUTPUT_FILE = "formatted_panels.json"


class PanelAppClient:
    def __init__(self):
        self.base_url = PANEL_APP_BASE_URL

        # 🔁 sessão com retry automático
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.headers = {"accept": "application/json"}

        if PANEL_APP_TOKEN:
            self.headers["X-CSRFTOKEN"] = PANEL_APP_TOKEN

        # 💾 caches
        self.ncbi_cache = self._load_json(NCBI_CACHE_FILE)
        self.panels_cache = self._load_json(PANELS_CACHE_FILE)

    # ========================
    # 💾 CACHE HELPERS
    # ========================

    def _load_json(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {}

    def _save_json(self, file_path, data):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    # ========================
    # 🌐 PAGINAÇÃO
    # ========================

    def _get_paginated(self, url):
        results = []
        page = 1

        while url:
            print(f"   🌐 Página {page}: {url}")

            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            data = response.json()
            results.extend(data.get("results", []))

            url = data.get("next")
            page += 1

            time.sleep(0.1)

        print(f"   📦 Total coletado: {len(results)} itens\n")
        return results

    # ========================
    # 📚 API METHODS
    # ========================

    def get_panel_genes(self, panel_id: int):
        url = f"{self.base_url}/panels/{panel_id}/genes/"
        return self._get_paginated(url)

    def get_all_panels(self):
        url = f"{self.base_url}/panels/"
        return self._get_paginated(url)

    # ========================
    # 🚀 PIPELINE COM CACHE
    # ========================

    def build_panels_with_genes(self):
        panels = self.get_all_panels()

        total = len(panels)
        print(f"\n🔍 Total de painéis encontrados: {total}\n")

        for i, panel in enumerate(panels, start=1):
            panel_id = str(panel["id"])  # string pra chave JSON
            panel_name = f"{panel['name']} - PanelApp v.{panel['version']}"
            number_of_genes = panel['stats']['number_of_genes']

            # 🔁 já está em cache?
            # if panel_id in self.panels_cache:
            #     print(f"⏭️ [{i}/{total}] Pulando (cache): {panel_name}")
            #     continue

            print(f"➡️ [{i}/{total}] Processando: {panel_name}")

            try:
                print("   🔄 Buscando genes...")
                print(f"✅ {number_of_genes} genes encontrados (GREEN + OTHERS)")
                genes_data = self.get_panel_genes(panel["id"])
                
                genes = [
                    g["gene_data"]["gene_symbol"]
                    for g in genes_data
                    if g["confidence_level"] == "3"
                ]

                print(f"   ✅{len(genes)} genes encontrados (GREEN)" )

            except Exception as e:
                print(f"   ❌ Erro no painel {panel_id}: {e}")
                genes = []

            # 💾 salva no cache incremental
            self.panels_cache[panel_id] = {
                "id": panel["id"],
                "name": panel_name,
                "visible": True,
                "genes": genes
            }

            self._save_json(PANELS_CACHE_FILE, self.panels_cache)

        print(f"\n🎯 Finalizado! {len(self.panels_cache)} painéis no cache.\n")

        return list(self.panels_cache.values())
    
    def get_cached_panels(self):
        return list(self.panels_cache.values())
    

        print("🔄 Coletando genes únicos...")

        all_genes = set()

        for panel in self.panels_cache.values():
            all_genes.update(panel["genes"])

        all_genes = list(all_genes)

        print(f"🧬 Total de genes únicos: {len(all_genes)}")

        # 🔁 batch em chunks (NCBI não gosta de queries gigantes)
        chunk_size = 200
        gene_map = {}

        for i in range(0, len(all_genes), chunk_size):
            chunk = all_genes[i:i + chunk_size]

            print(f"➡️ Buscando chunk {i} - {i + len(chunk)}")

            try:
                result = self.ncbi_client.get_gene_ids_batch(chunk)
                gene_map.update(result)
            except Exception as e:
                print(f"❌ Erro no chunk: {e}")

        print("🔧 Montando painéis formatados...")

        formatted_panels = []

        for panel in self.panels_cache.values():
            formatted_genes = []

            for gene_symbol in panel["genes"]:
                ncbi_id = gene_map.get(gene_symbol)

                formatted_genes.append({
                    "id": "",
                    "name": gene_symbol,
                    "ncbi_id": str(ncbi_id) if ncbi_id else ""
                })

            formatted_panels.append({
                "genes": formatted_genes,
                "id": panel["id"],
                "name": panel["name"],
                "visible": panel["visible"]
            })

        print("💾 Salvando JSON...")

        with open(OUTPUT_FILE, "w") as f:
            json.dump(formatted_panels, f, indent=2)

        print("🎯 Finalizado!")

        return {
            "message": "Formatted panels generated",
            "total_panels": len(formatted_panels),
            "total_genes": len(gene_map)
        }