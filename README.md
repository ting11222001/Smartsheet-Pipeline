# Smartsheet Webhook Pipeline

A Python AWS pipeline that receives a Smartsheet-style webhook, processes the row data, and stores it in DynamoDB. When a row status is "Complete", it exports a CSV summary to S3.

[Watch the Demo Video](https://www.youtube.com/watch?v=oYZsltt8m-Y) · [Architecture](#architecture)


## Table of Contents

- [What This Does](#what-this-does)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [What's Built](#whats-built)
- [In Progress](#in-progress)


## What This Does

Simulates the core integration pattern used by Smartsheet solution partners.

A POST request arrives with row data from a Smartsheet webhook. Lambda validates and processes the payload. The row is written to DynamoDB. If the row status is "Complete", Lambda also writes a CSV summary to S3.

- Validates incoming JSON payload
- Writes every row to DynamoDB
- Exports completed rows to S3 as CSV
- Logs errors and events to CloudWatch


## Tech Stack

- Python 3.12
- AWS Lambda
- AWS API Gateway
- AWS DynamoDB
- AWS S3
- AWS SAM (deployment)


## Architecture

```
POST request API Endpoint 
e.g. `https://abc123.execute-api.ap-southeast-2.amazonaws.com/prod/webhook`
      |
      ▼
API Gateway
      |
      ▼
   Lambda
   /    \
  ▼      ▼ (if status = "Complete")
DynamoDB  S3
          (CSV export)
```

## Getting Started

1. Clone the repo
2. Install AWS SAM CLI and run `aws configure`
3. Run `sam build`
4. Run `sam local invoke` to test locally
5. Run `sam deploy --guided` to deploy to AWS


## What's Built

- SAM project with `template.yaml` and `lambda_function.py`
- API Gateway POST endpoint
- Lambda validates and processes fake Smartsheet row data
- DynamoDB table defined in SAM template, written to via boto3
- S3 export triggered when `status == "Complete"`
- Structured logging to CloudWatch


## In Progress

- Real Smartsheet webhook signature verification
- Unit tests
- CI/CD with GitHub Actions