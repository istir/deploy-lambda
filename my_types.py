from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Function(TypedDict):
    method: str
    api_path: str
    name: str
    binary_path: str


@dataclass
class ApiGatewayResponse(TypedDict):
    id: str
    parentId: str
    pathPart: str
    path: str
