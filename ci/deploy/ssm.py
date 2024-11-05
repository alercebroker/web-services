import boto3
import sys

def main(parameter_name: str):
    try:
        client = boto3.client("ssm")
        response = client.get_parameter(Name=parameter_name)
        with open("values.yaml", "w") as f:
            f.write(response["Parameter"]["Value"])
    except Exception as e:
        print(f"Error in task: {e}")


if __name__ == "__main__":
    parameter_name = sys.argv[1]
    main(parameter_name)
