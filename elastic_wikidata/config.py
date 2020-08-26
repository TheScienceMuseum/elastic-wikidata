class RuntimeConfig:
    def __init__(self):
        self.items = {}

    def add_item(self, item: dict):
        """
        Add an item to the runtime config
        """

        self.items.update(item)

    def get(self, key: str):
        """
        Get specific item from config. Returns None if key doesn't exist.
        """

        return self.items.get(key, None)

    def get_all(self) -> dict:
        """
        Return all items from runtime config
        """

        return self.items


runtime_config = RuntimeConfig()
