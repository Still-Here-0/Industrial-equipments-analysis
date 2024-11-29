import inspect



class PrintableClass:

    def __str__(self) -> str:
        text =  f"Comp:"

        for attr_name, attr_value in inspect.getmembers(self):
            if not attr_name.endswith("__") and not inspect.ismethod(attr_value):
                text += f"\n\t{attr_name}: {attr_value}"

        return text