from pathlib import Path
import json

class GeneService:
    def __init__(self, panel_client, ncbi_client, emedgene_client):
        self.panel_client = panel_client
        self.ncbi_client = ncbi_client
        self.emedgene_client = emedgene_client

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

    def upload_gene_lists(self):
            file = Path("formatted_gene_list.json")

            with file.open(encoding="utf-8") as f:
                gene_lists = json.load(f)

            total = len(gene_lists)

            print("=" * 80)
            print(f"🚀 Iniciando cadastro de {total} listas de genes no Emedgene")
            print("=" * 80)

            created = []
            failed = []

            for i, gene_list in enumerate(gene_lists, start=1):
                print(f"\n[{i}/{total}] Criando lista: {gene_list['name']}")

                try:
                    result = self.emedgene_client.create_gene_list(gene_list)
                    created.append(gene_list["name"])

                    print(f"✅ Lista criada com sucesso!")

                except Exception as e:
                    failed.append({
                        "index": i,
                        "name": gene_list["name"],
                        "error": str(e)
                    })

                    print(f"❌ Erro ao criar a lista!")
                    print(f"   Nome : {gene_list['name']}")
                    print(f"   Erro : {e}")

            print("\n" + "=" * 80)
            print("🏁 Cadastro finalizado")
            print(f"Total de listas : {total}")
            print(f"Criadas         : {len(created)}")
            print(f"Falharam        : {len(failed)}")

            if failed:
                print("\nListas que falharam:")
                for item in failed:
                    print(f"- [{item['index']}/{total}] {item['name']}")
                    print(f"  Erro: {item['error']}")

            print("=" * 80)

            return {
                "total": total,
                "created": len(created),
                "failed": len(failed),
                "failed_lists": failed
            }