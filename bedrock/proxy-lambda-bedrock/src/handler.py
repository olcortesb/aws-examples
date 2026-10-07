import boto3
import json
import os

bedrock = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])
MODEL   = os.environ["BEDROCK_MODEL_ID"]


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        prompt = body.get("prompt", "").strip()
        if not prompt:
            return _response(400, {"error": "prompt is required"})

        result = _invoke(prompt)
        return _response(200, {"result": result, "model": MODEL})

    except bedrock.exceptions.ValidationException as e:
        return _response(400, {"error": str(e)})
    except bedrock.exceptions.ModelTimeoutException:
        return _response(504, {"error": "Model timed out — try with fewer files"})
    except Exception as e:
        return _response(500, {"error": str(e)})


def _invoke(prompt: str) -> str:
    response = bedrock.invoke_model(
        modelId=MODEL,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }),
    )
    data = json.loads(response["body"].read())
    return data["content"][0]["text"]


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
