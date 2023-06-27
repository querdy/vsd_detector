from zeep.exceptions import IncompleteOperation
from zeep.wsdl.definitions import Binding


def resolve(self, definitions) -> None:
    search_port_name = self.port_name.text.replace("MercuryVUServicePortType",
                                                   "MercuryG2BServicePortType") if "MercuryVUServicePortType" in self.port_name.text else self.port_name.text
    self.port_type = definitions.get("port_types", search_port_name)

    for name, operation in list(self._operations.items()):
        try:
            operation.resolve(definitions)
        except IncompleteOperation as exc:
            del self._operations[name]


Binding.resolve = resolve
