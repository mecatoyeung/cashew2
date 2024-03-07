import sys
import decimal
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import requests

from apscheduler.schedulers.background import BackgroundScheduler

from parsers.models.parser import Parser
from parsers.models.open_ai_metrics import OpenAIMetrics

def get_open_ai_metrics(start_date=None, end_date=None):
    parsers = Parser.objects.select_related("open_ai_metrics_key").all()
    for parser in parsers:

        if hasattr(parser, 'open_ai_metrics_key') and \
            parser.open_ai_metrics_key != None and \
            parser.open_ai_metrics_key.open_ai_metrics_tenant_id != "" and \
            parser.open_ai_metrics_key.open_ai_metrics_client_id != "" and \
            parser.open_ai_metrics_key.open_ai_metrics_client_secret != "" and \
            parser.open_ai_metrics_key.open_ai_metrics_subscription_id != "" and \
            parser.open_ai_metrics_key.open_ai_metrics_service_name != "":

            tenant_id = parser.open_ai_metrics_key.open_ai_metrics_tenant_id
            client_id = parser.open_ai_metrics_key.open_ai_metrics_client_id
            client_secret = parser.open_ai_metrics_key.open_ai_metrics_client_secret
            resource = "https://management.core.windows.net/"

            token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"

            payload = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "resource": resource,
            }

            token_response = requests.post(token_url, data=payload)

            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data.get("access_token")

                subscription_id = parser.open_ai_metrics_key.open_ai_metrics_subscription_id
                open_ai_service_name = parser.open_ai_metrics_key.open_ai_metrics_service_name

                metrics_headers = {
                    'Authorization': 'Bearer ' + access_token,
                }

                if start_date == None and end_date == None:
                    start_date = datetime.now() + relativedelta(months=-1)
                    end_date = datetime.now()
                    
                timespan = start_date.strftime("%Y-%m-%dT00:00:00Z/") + end_date.strftime("%Y-%m-%dT00:00:00Z")

                generated_tokens_metrics_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/Cashew/providers/Microsoft.CognitiveServices/accounts/{open_ai_service_name}/providers/microsoft.insights/metrics?api-version=2023-10-01&metricnames=GeneratedTokens&interval=P1D&aggregation=Total&timespan={timespan}"
                generated_tokens_metrics_response = requests.get(generated_tokens_metrics_url, headers=metrics_headers)
                generated_tokens_metrics_data = generated_tokens_metrics_response.json()

                processed_tokens_metrics_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/Cashew/providers/Microsoft.CognitiveServices/accounts/{open_ai_service_name}/providers/microsoft.insights/metrics?api-version=2023-10-01&metricnames=ProcessedPromptTokens&interval=P1D&aggregation=Total&timespan={timespan}"
                processed_tokens_metrics_response = requests.get(processed_tokens_metrics_url, headers=metrics_headers)
                processed_tokens_metrics_data = processed_tokens_metrics_response.json()

                processed_tokens_pricing = 0.0005
                generated_tokens_pricing = 0.0015
                processed_tokens_data = processed_tokens_metrics_data['value'][0]['timeseries'][0]['data']
                generated_tokens_data = generated_tokens_metrics_data['value'][0]['timeseries'][0]['data']
                pricing_metrics_data = []
                for i in range(len(generated_tokens_data)):
                    price = decimal.Decimal(processed_tokens_data[i]['total'] * processed_tokens_pricing / 1000 + generated_tokens_data[i]['total'] * generated_tokens_pricing / 1000)
                    rounded_price = decimal.Decimal(price).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
                    remained_value = price - rounded_price
                    if remained_value > 0:
                        rounded_price += decimal.Decimal(0.01)
                    pricing_metrics_data.append({
                        "timeStamp": generated_tokens_data[i]["timeStamp"],
                        "total": rounded_price
                    })

                delta = end_date - start_date

                for i in range(delta.days):
                    day = start_date + timedelta(days=i)

                    day_min = datetime.combine(day, time.min)
                    day_max = datetime.combine(day, time.max)

                    existing_metrics_list = OpenAIMetrics.objects.filter(parser=parser, date__range=(day_min, day_max))
                    if existing_metrics_list.count() > 0:
                        existing_metrics = existing_metrics_list[0]
                        existing_metrics.processed_tokens = processed_tokens_data[i]["total"]
                        existing_metrics.generated_tokens = generated_tokens_data[i]["total"]
                        existing_metrics.price = pricing_metrics_data[i]["total"]
                        existing_metrics.save()
                    else:
                        new_metrics = OpenAIMetrics()
                        new_metrics.parser = parser
                        new_metrics.date = day
                        new_metrics.processed_tokens = processed_tokens_data[i]["total"]
                        new_metrics.generated_tokens = generated_tokens_data[i]["total"]
                        new_metrics.price = pricing_metrics_data[i]["total"]
                        new_metrics.save()

def get_open_ai_metrics_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    scheduler.add_job(get_open_ai_metrics, 'interval', days=1)
    scheduler.start()
    print("Processing File Source", file=sys.stdout)