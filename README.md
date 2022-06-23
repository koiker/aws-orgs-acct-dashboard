# AWS Organizations Account Dashboard

This solution create a Cloudwatch rule that triggers a lambda function on a daily basis.  
The lambda function will list all AWS accounts and generate a CSV file with the last 24 months of accounts created

To deploy this solution you need to deploy a Cloudformation Stack with the template: `template/template.yaml`
The parameters are the S3 bucket name and if you want to create a new S3 bucket or point to an existing one.
