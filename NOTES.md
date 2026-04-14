# What I need to install
## Install Python 3.12 
Go to: python.org/downloads

My plan uses Python 3.12 because that is what AWS Lambda supports.

Click the Windows link, then scroll down the page until I see Python 3.12.x and download that one.

Scroll to the bottom and pick Windows installer (64-bit).

Run the installer.

Important: On the first screen, check the box that says "Add python.exe to PATH" before clicking Install.

On Windows, check if installed successfully:
```
python --version	
```

## Install AWS CLI - this lets you talk to AWS from your terminal
Go to: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

Close and reopen the command prompt window, check if installed successfully:
```
aws --version
```

## Install AWS SAM CLI - this is the tool for building and testing Lambda locally
For my AWS account other than root, I need an IAM user for setting up SAM CLI.

Step 1: Go to IAM
```
In the search bar at the top, type IAM and click it.
```

Step 2: Create a user
```
In the left menu, click Users.
Click Create user.
Enter a username, for example: sam-deploy.
Click Next.
```

Step 3: Set permissions
```
Select Attach policies directly.
Search for AdministratorAccess.
Check the box next to it.
Click Next, then Create user.
```

Step 4: Create an access key
```
Click on the user I just created.
Go to the Security credentials tab.
Scroll down to Access keys, click Create access key.
Select Command Line Interface (CLI).
Check the confirmation box, click Next, then Create access key.
Important: Download the CSV file or copy both keys now. The secret key cannot be seen again after this page.
```

Once I have the Access Key ID and Secret Access Key, run this in the terminal:
```
aws configure
```

It will ask 4 things, enter them one by one:
```
AWS Access Key ID: <paste your access key ID>
AWS Secret Access Key: <paste your secret key>
Default region name: ap-southeast-2
Default output format: json
```

Then verify it works:
```
aws sts get-caller-identity
```

I should see my account ID and sam-deploy as the user:
```
{
    "UserId": "YOUR_USER_ID",
    "Account": "YOUR_ACCOUNT_ID",
    "Arn": "YOUR_ARN"
}
```

Next, install SAM CLI. Go to this page and download the Windows installer:
docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

Click through it with default options.

After it finishes, verify it works:
```
sam --version
```

## Install Docker - SAM needs this to run Lambda locally

Check if installed:
```
docker --version
```

# Project setup

## Set the local folder to the remote repo
Create a .gitignore file:
```
echo ".aws-sam/ __pycache__/ *.pyc samconfig.toml" > .gitignore
```

Then verify it looks correct:
```
type .gitignore
```

Output:
```
".aws-sam/ __pycache__/ *.pyc samconfig.toml"
```

Now create the two project files. First, create template.yaml:
```
echo. > template.yaml
echo. > lambda_function.py
```

Then open the folder in VS Code:
```
code .
```

Create lambda_function.py, template.yaml, test_event.json.

Docker Desktop just needs to be running in the background. Open Docker Desktop and wait until it shows "Engine running" at the bottom left.

Then, in cmd, cd into the project folder and run:
```
sam local invoke SmartsheetFunction --event test_event.json
```

After a while I can see this:
```
{"statusCode": 200, "body": "{\"message\": \"Row processed successfully\", \"row_id\": \"101\", \"status\": \"In Progress\", \"project_name\": \"Bridge Construction\"}"}
```

## SAM Local vs SAM Deploy

One-liner: `sam local` runs everything in Docker on my machine with no AWS connection, and costs only start when I run `sam deploy`.

Key points:
- `sam local invoke` uses Docker to simulate Lambda locally, no AWS involved.
- `sam deploy` is when real AWS resources are created and billing can begin.
- Run `sam delete` when done to clean up and avoid surprise charges.


## Root vs IAM, and Why Lambda
One-liner: Root is too powerful to use daily, IAM limits the blast radius of mistakes or breaches, and Lambda removes the cost and effort of managing a server.

Key points:
- Root account should only be used for initial setup and billing. Lock it away after that.
- IAM users get least-privilege access, only what they need.
- Lambda bills per invocation, not per hour, so idle time costs nothing.
- Lambda also removes server maintenance and scales automatically.


## Deploy SAM

Run this command:
```
sam deploy --guided
```

It will ask several questions. Answer them like this:
```
Stack Name: smartsheet-pipeline
AWS Region: ap-southeast-2
Confirm changes before deploy: y
Allow SAM CLI IAM role creation: y
Disable rollback: n
SmartsheetFunction may not have authorization defined, Is this okay?: y
Save arguments to configuration file: y
SAM configuration file: samconfig.toml
SAM configuration environment: default
```

Note that always check with the `sam local invoke SmartsheetFunction --event test_event.json` first before actually going live with `sam deploy --guided`.

Click yes when it asked:
```
Previewing CloudFormation changeset before deployment
======================================================
Deploy this changeset? [y/N]: y
```

Once it shows:
```
Successfully created/updated stack - smartsheet-pipeline in ap-southeast-2
```

Do this to find the public URL of API Gateway:
```
sam list endpoints --stack-name smartsheet-pipeline --region ap-southeast-2
```

Which is this:
```
https://ww8673virj.execute-api.ap-southeast-2.amazonaws.com/Prod/webhook
```

## Test with a post request to the public url

In Postman:

Set method to POST

Enter this URL:
```
https://ww8673virj.execute-api.ap-southeast-2.amazonaws.com/Prod/webhook
```

Click Body, select raw, then select JSON from the dropdown

Paste this:
```
{
    "row_id": "101",
    "status": "In Progress",
    "project_name": "Bridge Construction"
}
```

Click Send. It should show response 200.

## See DynamoDB in AWS Console

Go to AWS Console and search DynamoDB in the top search bar

Click Tables in the left menu

Click `smartsheet-rows`

Click Explore table items button on the top right

Notes: make sure the console is set to the same region as deployed by SAM e.g. `ap-southeast-2 (Sydney)`.


## See S3 

Search S3 in the top search bar

See a bucket called `smartsheet-summaries-<my account id>`

Click it

Click the summaries/ folder after you send the Complete request


## Testing the script locally after the code included interactions with DynamoDB and S3

The code reads os.environ["DYNAMODB_TABLE"], but sam local invoke does not automatically load environment variables from template.yaml.

So table_name is probably an empty string or throwing a KeyError before even reaching put_item.

Fix: pass the environment variables when running locally:
```
sam local invoke SmartsheetFunction --event test_event.json --env-vars env.json
```

Create `env.json` in the project folder:
``
json{
  "SmartsheetFunction": {
    "DYNAMODB_TABLE": "<name of the table>",
    "S3_BUCKET": "<name of the bucket>"
  }
}
```

I didn't have to set the region in the `lambda_function.py` or `env.json` as I've set region in my `aws configure`.

Check what's in `aws configure`:
```
aws configure list
```