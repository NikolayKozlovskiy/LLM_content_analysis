class WebScraping():
    def __init__(self, component_config) -> None:
        self.config = component_config
        self.print_statement = self.config.get("print_statement")

    def run(self):
        print(f"Printing the statement: {self.print_statement}")