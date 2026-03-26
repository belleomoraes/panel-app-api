class GeneService:
    def __init__(self, panel_client, ncbi_client):
        self.panel_client = panel_client
        self.ncbi_client = ncbi_client

    def get_cached_panels(self):
        return self.panel_client.get_cached_panels()

    def build(self):
        return self.panel_client.build_panels_with_genes()