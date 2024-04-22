from aws import send_to_lambda
from util import util


def main():

    functions = get_functions()
    for function in functions:
        fn_data = util.parse_path_to_function_name(function)
        print("f", fn_data)
        if fn_data and fn_data != True:
            send_to_lambda(fn_data)
            print(fn_data)
        else:
            print(f"No changes for {function}")
            continue

    pass


def get_functions() -> list[str]:
    files = util.walk_all_dirs()
    return files


if __name__ == "__main__":
    main()
