import requests
import json
from flask import Flask, request


app = Flask(__name__)

def get_line_item_details(line_item_ids,code):
    line_item_full = list()
    headers = {"Authorization": "Bearer " + code, "Content-Type": "application/json"}
    params = {'properties':"name, quantity, price,discount, hs_discount_percentage, hs_term_in_months, partner_commission, recurringbillingfrequency, category"}
    for line_item_id in line_item_ids:
        url = "https://api.hubapi.com/crm/v3/objects/line_items/" + str(line_item_id)
        response = requests.get(url, headers=headers, params=params)
        if(response):
          resp_lt = response.json()
          line_item_full.append(resp_lt.copy())
    return line_item_full

@app.route("/get_hubspot_info", methods=['GET','POST'])
def get_hubspot_info():
  error_logs_list = list()
  try:
    args = request.args
    print("ARGS", args)
    deal_record_id = args.get("deal_id")
    print("Deal ID", deal_record_id);
    code = args.get("access_token")
    print("code", code);
    if(len(deal_record_id) > 1):
      headers = {"Authorization": "Bearer " + code, "Content-Type": "application/json"}
      params = {'associations':"contacts,companies,line_items" }
      url = "https://api.hubapi.com/crm/v3/objects/deals/" + str(deal_record_id)
      response = requests.get(url, headers=headers, params=params)
      print("response", response);
      if(response.status_code == 200):
        resp = response.json()
        if "associations" in resp:
          associations = resp['associations']
          if "line items" in associations :
            line_item_ids = list()
            line_items = associations['line items']['results']
            for ids in line_items:
                line_item_ids.append(ids['id'])
            if(len(line_item_ids) >= 1):
              line_item_details = get_line_item_details(line_item_ids,code)
            else:
              error_logs_list.append("Line Items - Handling Issue")
              line_item_details = []
          else:
            error_logs_list.append("No Line item is associated with this Deal")
            line_item_details = []
        else:
          error_logs_list.append("No Associated Contact or Company or Line item Found")
          line_item_details = []
      else:
        error_logs_list.append("Failed Response!! Invalid Information provided")
        line_item_details = []
    else:
      error_logs_list.append("Invalid HubSpot Deal Record ID provided!!!")
      line_item_details = []
    results = {"line_item_details": line_item_details, "error_log_details": "".join(error_logs_list)}
    print(results)
    return results
  except:
    error_logs_list.append("Issue detected in server. Contact Process Administrator!!!")
    return error_logs_list
