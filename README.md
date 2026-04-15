# Smartsheet Webhook Pipeline

![CI](https://github.com/ting11222001/Smartsheet-Pipeline/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/ting11222001/Smartsheet-Pipeline/actions/workflows/cd.yml/badge.svg)

A Python AWS Lambda pipeline that processes row data and stores them in DynamoDB. When a row status is "Complete", it exports into a CSV to S3.

[Watch the Demo Video](https://www.youtube.com/watch?v=oYZsltt8m-Y) · [Architecture](#architecture)


## Demo

The video shows the webhook being triggered and the row written to DynamoDB. When the row status is "Complete", Lambda also exports it into a CSV to S3. 

The screenshot below shows the exported file:

![Exported CSV](demo/exported-csv.png)


## Table of Contents

- [What This Does](#what-this-does)
- [Tech Stack](#tech-stack)
- [Highlights](#highlights)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Local Testing](#local-testing)
- [What's Built](#whats-built)
- [In Progress](#in-progress)


## What This Does

Demonstrates the core integration pattern used by Smartsheet solution partners.

A POST request arrives with row data. Lambda validates and processes the payload. The row is written to DynamoDB. If the row status is "Complete", Lambda also exports a CSV summary to S3.

- Validates incoming JSON payload
- Writes every row to DynamoDB
- Exports completed rows to S3 as CSV


## Tech Stack

- Python 3.12
- AWS Lambda
- AWS API Gateway
- AWS DynamoDB
- AWS S3
- AWS SAM (deployment)


## Highlights

Data architecture decision:
- I matched the setup to the job description. DynamoDB holds live operational data. S3 holds reporting data in a format a non-technical person can open. From what I have learned, that is a common pattern in data pipelines.


AWS CLI:
- Configured credentials and ran AWS commands from the terminal, without using the AWS console.


AWS SAM (Serverless Application Model):
- SAM is a layer on top of CloudFormation with shorter syntax for serverless resources like Lambda, API Gateway, and DynamoDB. Less YAML, faster to set up and repeat deployments.


DynamoDB on-demand billing:
- Set `BillingMode: PAY_PER_REQUEST` on the DynamoDB table. I pay per read or write, with no minimum cost. Good for low-traffic or experimental projects where usage is hard to predict.

## Architecture

```
POST request API Endpoint
e.g. `https://<id>.execute-api.<region>.amazonaws.com/prod/webhook`
      |
      ▼
 API Gateway
      |
      ▼
   Lambda
      |
      ▼
  DynamoDB
      |  (if status = "Complete")
      ▼
     S3   (CSV export)
```


## Getting Started

1. Clone the repo
2. Install AWS SAM CLI and run `aws configure`
3. Run `sam build`
4. Run `sam local invoke` to test locally
5. Run `sam deploy --guided` to deploy to AWS


## Local Testing

The test event, `test_event.json`, is a simplified payload, not a real Smartsheet webhook shape:
```
{
  "body": "{\"row_id\": \"101\", \"status\": \"In Progress\", \"project_name\": \"Bridge Construction\"}",
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json"
  }
}
```
For the real Smartsheet webhook payload, see the Smartsheet webhook docs.


## What's Built

- SAM project with `template.yaml` and `lambda_function.py`
- API Gateway POST endpoint
- Lambda validates and processes incoming row data
- DynamoDB table defined in SAM template, written to via boto3
- S3 export triggered when `status == "Complete"`
- CI/CD with GitHub Actions (CI runs `sam build` on every push. CD deploys to AWS on merge to main)


## In Progress

- Real Smartsheet webhook signature verification (skipped, requires paid Smartsheet account)
- Unit tests
- Structured logging to CloudWatch (for logs errors and events)