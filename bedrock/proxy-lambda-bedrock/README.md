# bedrock Access Proxy

SAM infrastructure for PR review via Bedrock Claude, exposed through an API Gateway authenticated with Cognito.

## Architecture

![Architecture](architecture.png)

```
External backend (issue tracker)
  └── sanitizer.py  ← strips sensitive data before leaving the environment
  └── _get_cognito_token()  ← USER_PASSWORD_AUTH (cached 1h in memory)
        │
        └── API Gateway (Cognito Authorizer + Usage Plan)
              └── Lambda pr-review-bedrock
                    └── Bedrock Claude (inference profile us-east-1)
```

## Stack

- **SAM** — infrastructure as code
- **API Gateway** — REST API with Cognito Authorizer + Usage Plan
- **Lambda** — Python 3.12, 25s timeout (below API GW hard limit of 29s)
- **Cognito** — User Pool with USER_PASSWORD_AUTH, 1h tokens
- **Bedrock** — Claude Haiku via inference profile `us.*`

## Project structure

```
bedrock-pr-review/
├── src/
│   └── handler.py       # Lambda handler
├── template.yaml        # SAM template
├── samconfig.toml.example
└── README.md
```

## Deploy

### Requirements

- AWS CLI configured with permissions on Lambda, API GW, Cognito, Bedrock, IAM, CloudFormation, S3
- SAM CLI installed
- Model access enabled in Bedrock console (us-east-1)

### First deploy

```bash
cp samconfig.toml.example samconfig.toml
sam build
sam deploy --guided --region us-east-1
```

Recommended values during `--guided`:

| Prompt | Value |
|--------|-------|
| Stack Name | `pr-review-bedrock` |
| AWS Region | `us-east-1` |
| Parameter BedrockModelId | Enter (uses default) |
| Confirm changes before deploy | `y` |
| Allow SAM CLI IAM role creation | `y` |
| Disable rollback | `n` |
| Save arguments to samconfig.toml | `y` |

### Redeploy with a specific model

New Claude models require an **inference profile** (prefix `us.`):

```bash
sam build && sam deploy --region us-east-1 \
  --parameter-overrides BedrockModelId=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

> **Note:** if `samconfig.toml` has a `parameter_overrides` saved from a previous deploy,
> it must be passed explicitly on each deploy or edited in the file.

### Deploy outputs

```
UserPoolId        us-east-1_XXXXXXXXX
UserPoolClientId  XXXXXXXXXXXXXXXXXXXXXXXXXX
ApiUrl            https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod/review
```

## Create Cognito user

After the first deploy, manually create the user that the issue tracker backend will use:

```bash
# Create user
aws cognito-idp admin-create-user \
  --region us-east-1 \
  --user-pool-id <UserPoolId> \
  --username <email> \
  --temporary-password <TempPass1!> \
  --message-action SUPPRESS

# Set permanent password (without this step auth fails with FORCE_CHANGE_PASSWORD)
aws cognito-idp admin-set-user-password \
  --region us-east-1 \
  --user-pool-id <UserPoolId> \
  --username <email> \
  --password <FinalPass1!> \
  --permanent
```

## Verify the endpoint

```bash
# 1. Get token
TOKEN=$(aws cognito-idp initiate-auth \
  --region us-east-1 \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id <UserPoolClientId> \
  --auth-parameters USERNAME=<email>,PASSWORD=<password> \
  --query 'AuthenticationResult.IdToken' \
  --output text)

# 2. Call the endpoint
curl -s -X POST \
  <ApiUrl> \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello in one line"}' | jq .
```

Expected response:
```json
{
  "result": "Hello!",
  "model": "us.anthropic.claude-haiku-4-5-20251001-v1:0"
}
```

## Issue tracker configuration

Add to the backend `.env` (`gitlab-issue-tracker/.env`):

```env
BEDROCK_API_URL=https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod/review
BEDROCK_COGNITO_CLIENT_ID=<UserPoolClientId>
BEDROCK_COGNITO_USERNAME=<email>
BEDROCK_COGNITO_PASSWORD=<password>
BEDROCK_COGNITO_REGION=us-east-1
```

## Rate limits

Configured in the API Gateway Usage Plan:

| Parameter | Value |
|-----------|-------|
| RateLimit | 2 req/s sustained |
| BurstLimit | 5 req/s burst |
| Quota | 200 req/month |

For a larger team, adjust in `template.yaml` before redeploying.

## Design decisions

### 25s Lambda timeout
API Gateway has a hard limit of 29s that cannot be changed. The Lambda is set to 25s so it fails cleanly with a controlled error before API GW cuts the connection with a generic 504 with no body.

### Cognito token cached in memory
`_get_cognito_token()` in the backend caches the IdToken for 55 minutes (token lasts 1h). Avoids a Cognito call on every request. If a 401 arrives from API GW, the cache is invalidated and re-authentication happens automatically.

### Inference profile (`us.*`) and IAM permissions
New-generation Claude models (Haiku 4.5+, Sonnet 4+) do not support direct on-demand throughput — they require the `us.` region prefix pointing to the AWS cross-region inference profile. Without the prefix the deploy succeeds but invocations fail with `ValidationException`.

The inference profile ARN differs from the `foundation-model` ARN, so the Lambda policy uses `Resource: "*"` scoped only to `bedrock:InvokeModel`. The Lambda has no other permissions, so the actual risk is minimal.

### Sanitizer before leaving the environment
The MR diff goes through `sanitizer.py` before building the prompt. It strips AWS tokens, internal IPs, private domains, JWTs, keys, and other sensitive data that should not leave the environment toward an external LLM.

## Available models in us-east-1

```bash
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'claude')].{id:modelId,status:modelLifecycle.status}" \
  --output table
```

Always use models with `status: ACTIVE` and the `us.` prefix when deploying.
