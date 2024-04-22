# Deploy Lambda

## This script will deploy your code to AWS Lambda and API Gateway.

It serves as an alternative to AWS SAM for my simple project structure.

## Why?

SAM requires some boilerplate and uses many services. Deploying one little lambda function and connecting it to API Gateway requires at least: CloudFormation, S3, IAM, API Gateway, Lambda, CloudWatch. This script requires just Lambda and API Gateway permissions.

## Required project structure

I made this having in mind such a structure:

```
├── app
	├── auth
		├── login
			├── GET
				├── GetAuthLogin.go
			└── POST
				└── PostAuthLogin.go
├── src
	├── models
	├── utils
		└── database
			└── ...
	└── utils
```

For example, `/app/auth/login/GET/GetAuthLogin.go`

- creates a function named `your-configured-prefix_GetAuthLogin.json`
- creates a GET endpoint `GET /auth/login`
