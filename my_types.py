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


CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "prefix": {"type": "string"},
        "region": {"type": "string"},
        "account_id": {"type": "string"},
        "api_id": {"type": "string"},
        "lambda_role": {"type": "string"},
        "should_compare_hashes": {"type": "boolean"},
    },
}


@dataclass
class ConfigSchema(TypedDict):
    prefix: str
    region: str
    account_id: str
    api_id: str
    lambda_role: str
