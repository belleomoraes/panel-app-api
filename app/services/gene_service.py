class GeneService:
    def __init__(self, panel_client, ncbi_client):
        self.panel_client = panel_client
        self.ncbi_client = ncbi_client

    def get_cached_panels(self):
        return self.panel_client.get_cached_panels()

    def build(self):
        return self.panel_client.build_panels_with_genes()

    def emedgene_formatted(self):
        print("🔄 Coletando genes únicos...")

        panels = self.panel_client.get_cached_panels()

        all_genes = set()
        for panel in panels:
            all_genes.update(panel["genes"])

        all_genes = list(all_genes)

        print(f"🧬 Total de genes únicos: {len(all_genes)}")

        # 🚀 usa batch do NCBI
        gene_map = self.ncbi_client.get_gene_ids_batch(all_genes)

        print("🔧 Montando painéis formatados...")

        formatted_panels = []
        print(f"🧪 gene_map size: {len(gene_map)}")

        for panel in panels:
            formatted_genes = []

            for gene in panel["genes"]:
                formatted_genes.append({
                    "id": "",
                    "name": gene,
                    "ncbi_id": str(gene_map.get(gene) or "")
                })

            formatted_panels.append({
                "genes": formatted_genes,
                "id": panel["id"],
                "name": panel["name"],
                "visible": panel["visible"]
            })

        print(f"🧪 quantidade de paineis: {len(formatted_panels)}")
        print("🎯 Finalizado!")

        return formatted_panels