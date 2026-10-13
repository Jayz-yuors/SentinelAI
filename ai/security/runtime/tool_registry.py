from ai.security.runtime.base_tool import BaseSecurityTool


class SecurityToolRegistry:

    def __init__(self):
        self._tools: dict[str, BaseSecurityTool] = {}

    def register(
        self,
        tool: BaseSecurityTool
    ):
        self._tools[tool.name] = tool

    def get(
        self,
        name: str
    ):
        return self._tools.get(name)

    def all(self):
        return list(self._tools.values())

    def available(self):
        return [
            tool
            for tool in self._tools.values()
            if tool.is_available()
        ]