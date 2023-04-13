# Search Keyword Performance Analysis

## Project Overview
This project involves creating a Python application that processes a file and generates a tab-delimited file with data on revenue obtained from external search engines such as Google, Yahoo, and MSN. The output file contains information on the search engine domain, search keyword, and revenue. The application is designed to be deployed and executed within AWS, using AWS Lambda and S3 bucket.

## Business Problem
The client requires information on the revenue generated from external search engines and which keywords are performing the best based on revenue.

## Development Requirements
The Python application needs to contain at least one class and accept a single argument, which is the file that needs to be processed. The final output file should have a header row and be sorted by revenue, descending.

## Deliverable Requirements
The final output is a tab-delimited file that includes the search engine domain, search keyword, and revenue. The file should be sorted by revenue, descending, and should have a naming convention of `[Date]_SearchKeywordPerformance.tab`.

## AWS Deployment
The application is deployed within AWS using AWS Lambda and S3 bucket. The Lambda function is triggered by S3 bucket events and processes the file stored in the S3 bucket. AWS SAM templates are used for deployments, which creates the bucket and Lambda function.

## File Processing
The file processing involves parsing the hit level data file and reviewing the following columns: hit_time_gmt, date_time, user_agent, ip, geo_city, geo_country, geo_region, pagename, page_url, product_list, referrer, and event_list.

## Project Setup
* Clone the project repository.
* Install AWS CLI, AWS SAM CLI, and Python 3.8 or later.
* Create an S3 bucket and update the bucket name in the template.yaml file.
* Deploy the application using AWS SAM CLI.
* Upload the data file to the S3 bucket to trigger the Lambda function.

