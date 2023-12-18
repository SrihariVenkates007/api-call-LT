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

def get_contact_details(contact_id, code):
    headers = {"Authorization": "Bearer " + code, "Content-Type": "application/json"}
    params = {"properties": "firstname, lastname, email"}
    url = "https://api.hubapi.com/crm/v3/objects/contacts/" + contact_id
    response = requests.get(url, headers=headers, params=params)
    if(response.status_code == 200):
        response_contact = response.json()
    return response_contact

def get_company_details(company_id, code):
    headers = {"Authorization": "Bearer " + code, "Content-Type": "application/json"}
    params = {"properties": "name, type"}
    url = "https://api.hubapi.com/crm/v3/objects/companies/" + company_id
    response = requests.get(url, headers=headers, params=params)
    if(response.status_code == 200):
        response_company = response.json()
    return response_company

def get_partner_details(partner_id, code):
    headers = {"Authorization": "Bearer " + code, "Content-Type": "application/json"}
    params = {"properties": "name"}
    url = "https://api.hubapi.com/crm/v3/objects/2-9233637/" + partner_id
    response = requests.get(url, headers=headers, params=params)
    if(response.status_code == 200):
        response_partner = response.json()
    return response_partner


@app.route("/get_hubspot_info", methods=['GET','POST'])
def get_hubspot_info():
    error_logs_list = list()
    try:
        args = request.args
        deal_id = args.get("deal_id")
        contact_id = ""
        company_id = ""
        partner_id = ""
        code = args.get("code")
        print("ARGS", args)
        if(len(deal_id)> 1):
            headers = { "Authorization": "Bearer " + code, "Content-Type": "application/json" }
            params = { "associations": "contacts,line_items,company,2-9233637" }
            url = "https://api.hubapi.com/crm/v3/objects/deals/" + str(deal_id)
            response = requests.get(url, headers=headers, params=params)
            print("RESPONSE", response)
            if(response.status_code == 200):
                resp = response.json()
                print("RESP", resp)
                if "associations" in resp:
                    associations = resp['associations']

                    contact_results = associations['contacts']['results'] if 'contacts' in associations else []
                    company_results = associations['companies']['results'] if 'companies' in associations else []
                    partner_id = associations['p20215080_partner']['results'] if 'p20215080_partner' in associations else ""
                    line_item_results = associations['line items']['results'] if 'line items' in associations else []

                    if(len(contact_results) > 1):
                        for contacts in contact_results:
                            if(contacts['type'] == "primary_decision_maker"):
                                contact_id = contacts['id']

                    if(len(company_results) >  1):
                        for companies in company_results:
                            if(companies['type'] == "deal_to_company"):
                                company_id = companies['id']

                    if(len(line_item_results) > 1):
                        line_item_ids = list()
                        for line_items in line_item_results:
                            line_item_ids.append(line_items['id'])

                    if(len(contact_id) > 1):
                        contact_response = get_contact_details(contact_id, code)
                    else:
                        contact_response = {}

                    if(len(company_id) > 1):
                        company_response = get_company_details(company_id, code)
                    else:
                        company_response = {}

                    if(len(partner_id) > 1):
                        partner_response = get_partner_details(partner_id, code)
                    else:
                        partner_response = {}

                    if(len(line_item_ids) >= 1):
                        lineItem_response = get_line_item_details(line_item_ids,code)
        else:
            error_logs_list.append("Invalid HubSpot Deal Record ID provided!!!")
        results = { "contact_details": contact_response, "company_details": company_response, "partner_details": partner_response, "lineItem_details": lineItem_response, "error_log_details": error_logs_list}
        print(results)
        return results
    except Exception as e:
        print(e)
        error_logs_list.append(f"Issue detected: Contact Process Administrator!!!")
        return { "error_details": error_logs_list }


if __name__ == '__main__':  
   app.run()
                            
