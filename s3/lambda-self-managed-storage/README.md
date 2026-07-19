# Lambda Self-Managed Code Storage

Demo de `S3ObjectStorageMode=REFERENCE` vs `COPY` — feature lanzada el 17 de julio de 2026.

> Disponible en todas las regiones estándar (non-opt-in). Validado en **us-east-1**.

## Estructura

```
lambda/
  app.py                  # handler compartido
terraform/
  main.tf                 # bucket S3 + versioning + bucket policy + zip upload
cloudformation/
  template.yaml           # IAM role + Lambda REFERENCE + Lambda COPY
```

El flujo es: **Terraform** provisiona el bucket S3 → **CloudFormation** despliega las Lambdas usando los outputs de Terraform como parámetros.

> ⚠️ `s3_object_storage_mode` aún no está implementado en el provider `hashicorp/aws` de Terraform (pendiente de actualización al momento del lanzamiento). Por eso las Lambdas se despliegan con CloudFormation que sí lo soporta nativamente vía `AWS::Lambda::Function`.

---

## Deploy

### Paso 1 — Bucket S3 con Terraform (Docker)

```bash
cd terraform
cp -r ../lambda ./lambda

docker run --rm \
  -v $(pwd):/workspace \
  -v ~/.aws:/root/.aws:ro \
  -e AWS_PROFILE=<your-profile> \
  -w /workspace \
  hashicorp/terraform:1.10.5 \
  init

docker run --rm \
  -v $(pwd):/workspace \
  -v ~/.aws:/root/.aws:ro \
  -e AWS_PROFILE=<your-profile> \
  -w /workspace \
  hashicorp/terraform:1.10.5 \
  apply -var="region=us-east-1" -auto-approve
```

Outputs esperados:
```
bucket_name       = "lambda-self-managed-storage-<account_id>"
s3_key            = "deployments/app.zip"
s3_object_version = "<version_id>"
```

### Paso 2 — Capturar outputs

```bash
BUCKET="lambda-self-managed-storage-<account_id>"
S3_KEY="deployments/app.zip"
S3_VERSION="<version_id>"
```

### Paso 3 — Lambdas con CloudFormation

```bash
cd ../cloudformation

aws cloudformation deploy \
  --stack-name lambda-self-managed-storage \
  --template-file template.yaml \
  --region us-east-1 \
  --profile <your-profile> \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    CodeBucket=$BUCKET \
    CodeS3Key=$S3_KEY \
    CodeS3Version=$S3_VERSION
```

---

## Test

```bash
# REFERENCE mode — Lambda referencia el código directo desde S3
aws lambda invoke \
  --function-name lambda-self-managed-storage-reference \
  --region us-east-1 \
  --profile <your-profile> \
  --cli-binary-format raw-in-base64-out \
  /dev/stdout

# COPY mode — comportamiento tradicional
aws lambda invoke \
  --function-name lambda-self-managed-storage-copy \
  --region us-east-1 \
  --profile <your-profile> \
  --cli-binary-format raw-in-base64-out \
  /dev/stdout
```

Respuesta esperada:
```json
{
  "message": "Lambda Self-Managed Code Storage working!",
  "storage_mode": "REFERENCE",
  "function_name": "lambda-self-managed-storage-reference",
  "code_bucket": "lambda-self-managed-storage-<account_id>"
}
```

---

## Cleanup

```bash
# 1. Eliminar stack CloudFormation
aws cloudformation delete-stack \
  --stack-name lambda-self-managed-storage \
  --region us-east-1 \
  --profile <your-profile>

# 2. Destruir bucket con Terraform
cd terraform && \
docker run --rm \
  -v $(pwd):/workspace \
  -v ~/.aws:/root/.aws:ro \
  -e AWS_PROFILE=<your-profile> \
  -w /workspace \
  hashicorp/terraform:1.10.5 \
  destroy -var="region=us-east-1" -auto-approve
```

---

## REFERENCE vs COPY

| Aspecto | `COPY` | `REFERENCE` |
|---------|--------|-------------|
| Cuenta contra cuota Lambda | Sí (límite 300GB) | No |
| Fuente de verdad del código | Lambda-managed | Tu bucket S3 |
| Versionado requerido | No | **Sí (obligatorio)** |
| Control cifrado/compliance | No | Sí |
| Si el objeto S3 se elimina | Sin efecto | Función → `Inactive` |
| Tiempo de activación (~200MB) | Mayor | ~5s menos |
| Soporte en Terraform provider | ✅ | ⏳ Pendiente |
| Soporte en CloudFormation | ✅ | ✅ |
| Soporte en CLI | ✅ | ✅ |

## Referencias

- [AWS Lambda - Self-managed code storage](https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-zip.html)
- [AWS Compute Blog](https://aws.amazon.com/blogs/compute/introducing-self-managed-amazon-s3-buckets-for-aws-lambda-function-code/)
- [Artículo relacionado](../../post-article-backup/articles/lambda_self_managed_code_storage.md)
