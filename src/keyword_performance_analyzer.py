import boto3
import io
import csv
import os
from datetime import datetime

date_str = datetime.today().strftime('%Y-%m-%d')

s3 = boto3.client("s3")

destination_bucket = os.environ["DESTINATION_BUCKETNAME"]


class KeywordPerformanceAnalyzer:
    """
    A class that analyzes web traffic data from a log file and identifies search keywords
    and their associated revenue for different search engine domains.

    Attributes:
        bucket_name (str): The name of the S3 bucket containing the log file.
        object_key (str): The key of the S3 object (log file) to be analyzed.

    Methods:
        __init__(self, event):
            Initializes a new instance of the KeywordPerformanceAnalyzer class.
            Parses the event object and sets the bucket_name and object_key attributes.

        analyze(self):
            Performs the analysis of the log file.
            Reads the log file from S3, parses the data, and extracts relevant information.
            Merges the data based on search engine domain and search keyword.
            Sorts the data by revenue.
            Writes the resulting data to a .tsv file and uploads it to an S3 bucket.

        __get_search_engine_domain(self, referrer):
            Returns the search engine domain from the referrer URL.

        __get_search_keyword(self, referrer, search_engine_domain):
            Returns the search keyword from the referrer URL for the given search engine domain.

        __get_revenue(self, events, product):
            Returns the revenue for the given events and product data.
    """

    def __init__(self, event):
        try:
            self.bucket_name = event['Records'][0]['s3']['bucket']['name']
            self.object_key = event['Records'][0]['s3']['object']['key']
        except KeyError as e:
            print(f"Invalid event format: {e}")

    def analyze(self):
        try:
            response = s3.get_object(Bucket=self.bucket_name, Key=self.object_key)
            contents = response["Body"].read().decode('utf-8')
            file = io.StringIO(contents)
            search_engine_results = []
            data = []
            reader = csv.DictReader(file, delimiter="\t")
            for row in reader:
                ip = row['ip']
                events = row['event_list']
                product = row['product_list']
                referrer = row['referrer']
                search_engine_domain = self.__get_search_engine_domain(referrer)
                search_keyword = self.__get_search_keyword(referrer, search_engine_domain)
                revenue = self.__get_revenue(events, product)
                if search_engine_domain != "unknown":
                    search_engine_results.append({'search_engine_domain': search_engine_domain,
                                        'search_keyword': search_keyword,
                                        'revenue': revenue,
                                        'ip': ip})
                if events == "1":
                    for i in search_engine_results:
                        if ip == i['ip']:
                            search = i['search_engine_domain']
                            keyword = i['search_keyword']
                            data.append({'Search Engine Domain': search,
                                        'Search Keyword': keyword,
                                        'Revenue': revenue
                                        })
                            break
            merged_data = {}

            for item in data:
                key = item['Search Engine Domain'] + '|' + item['Search Keyword'].lower()
                if key in merged_data:
                    merged_data[key]['Revenue'] += item['Revenue']
                else:
                    merged_data[key] = item
                    merged_data[key]['Search Keyword'] = merged_data[key]['Search Keyword'].lower()

            merged_list = list(merged_data.values())

            sorted_data = sorted(merged_list, key=lambda x: x['Revenue'], reverse=True)
            file_name = f"{date_str}_SearchKeywordPerformance.tab"
            fieldnames = ['Search Engine Domain', 'Search Keyword', 'Revenue']
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, delimiter='\t', fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_data)
            try:
                s3.put_object(Bucket=destination_bucket, Key=file_name, Body=csv_buffer.getvalue())
            except Exception as e:
                print(f"Error uploading file to S3: {e}")
        except KeyError as ke:
            print(f"Invalid document format. Error at {ke}")

    def __get_search_engine_domain(self, referrer):
        search_engines = ['google.com', 'bing.com', 'yahoo.com']
        for engine in search_engines:
            if engine in referrer:
                return engine
        return 'unknown'

    def __get_search_keyword(self, referrer, search_engine_domain):
        for s in referrer.split("&"):
            if search_engine_domain in ["google.com", "bing.com"] and "q=" in s:
                print(s)
                return s.split("=")[1]
            elif search_engine_domain == "yahoo.com" and "p=" in s:
                print(s)
                return s.split("=")[1]
        return "unknown"

    def __get_revenue(self, events, product):
        if events == "1":
            return float(product.split(";")[3])  
        else:
            return "0.00"


def lambda_handler(event, context):
    try:
        log_analyzer = KeywordPerformanceAnalyzer(event)
        log_analyzer.analyze()
        return {
            "statusCode" : 200,
            "body" : "Execution Completed Successfully"
        }
    except Exception as e:
        print(f"An error occurred: {e}")
