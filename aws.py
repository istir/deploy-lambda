import os
import boto3
from boto3.session import Session
from botocore.exceptions import ClientError
from my_types import ApiGatewayResponse, Function
from config import CONFIG
from util import util

lambda_client = Session().client("lambda")  # type:ignore
api_client = boto3.client("apigateway")  # type:ignore


def send_to_lambda(function: Function):
    

    # return
    if not function:
        print("Critical error sending function")
        exit(0)
    zip = util.zip_file(function["binary_path"])

    try:
        update_function(zip, function["name"])
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":  # type: ignore
            print("Function doesn't exist")
            create_function(zip, function["name"])
            create_api_gateway_resources(function)
        else:
            print("Unexpected error: %s" % e)
    


def update_function(zip: str, name: str):
    lambda_client.update_function_code(
        Architectures=["arm64"],
        DryRun=False,
        FunctionName=name,
        ZipFile=read_zip_code(zip),
    )


def create_function(zip: str, name: str):
    print(zip)
    lambda_client.create_function(
        Architectures=["arm64"],
        FunctionName=name,
        Runtime="provided.al2023",
        Handler="bootstrap",
        Code={"ZipFile": read_zip_code(zip)},
        Publish=False,
        Role=f"arn:aws:iam::{CONFIG["account_id"]}:role/service-role/{CONFIG['lambda_role']}",
    )
    lambda_client.add_permission(
        FunctionName=name,
        StatementId="ApiGatewayPermission",
        Action="lambda:InvokeFunction",
        Principal="apigateway.amazonaws.com",
        SourceArn=f"arn:aws:execute-api:{CONFIG["region"]}:{CONFIG["account_id"]}:{CONFIG['api_id']}/*/*"
    )


def read_zip_code(zip: str) -> bytes:
    with open(zip, "rb") as f:
        return f.read()


def create_api_gateway_resources(function: Function) -> str:
    api_id = CONFIG["api_id"]
    if not api_id:
        print("No api id, skipping")
        return ""
    id, path_to_create = get_parent_id(function, api_id)

    path_parts = path_to_create.split("/")
    for i in range(len(path_parts)):
        path_part = path_parts[i]
        if not path_part:
            print("No path", i)
            continue
        print("part", path_part)
        creation = api_client.create_resource(
            restApiId=api_id, parentId=id, pathPart=path_part
        )
        if not creation["id"]:
            print("No creation id")
            break
        id = creation["id"]
        print(creation)

    create_api_gateway_method(function, id, api_id)
    return id


def create_api_gateway_method(function: Function, id: str, api_id: str):
    api_client.put_method(
        restApiId=api_id,
        operationName=function["name"],
        authorizationType="NONE",
        resourceId=id,
        httpMethod=function["method"],
    )

    api_client.put_integration(
        integrationHttpMethod="POST",
        httpMethod=function["method"],
        resourceId=id,
        restApiId=api_id,
        type="AWS_PROXY",
        uri=f"arn:aws:apigateway:{CONFIG['region']}:lambda:path/2015-03-31/functions/{util.create_arn(function['name'])}/invocations",
    )


def get_parent_id(function: Function, api_id: str) -> tuple[str, str]:

    res = api_client.get_resources(restApiId=api_id)

    items: list[ApiGatewayResponse] = res.get("items")  # type:ignore
    print(items)
    id, path_to_create = find_best_parent_id(function["api_path"], items)
    if not id:
        print("No id = no api configured", function)
        exit(0)
    print(id)
    return id, path_to_create
    # api_client.get_resource(restApiId=api_id,resourceId=)


"""Returns (id, path_to_create)"""


def find_best_parent_id(
    fn_path: str, items: list[ApiGatewayResponse]
) -> tuple[str, str]:
    path = fn_path
    iter = 0
    while path:
        iter = iter + 1
        print("p", path)
        for item in items:
            if item["path"] == path:
                return item["id"], get_rest_path(fn_path, path)
        path_parts = os.path.split(path)
        if len(path_parts):
            new_path: str = os.path.join(*path_parts[:-1])  # type: ignore
            path = new_path

            # new_rest_parts = os.path.split(fn_path)
            # if len(new_rest_parts) and new_rest_parts[iter:]:
            #     print(new_rest_parts[iter:], iter)
            #     os.path.join(*new_rest_parts[iter:])
        else:
            for item in items:
                if item["path"] == "/":
                    return item["id"], get_rest_path(fn_path, path)
    return "", ""


def get_rest_path(fn_path: str, result_path: str) -> str:
    if result_path and fn_path.startswith(result_path):
        fn_path = fn_path[len(result_path) :]
    return fn_path
