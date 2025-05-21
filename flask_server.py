
import requests
import json
import os
from flask_session import Session
from dotenv import get_key, load_dotenv
from flask import Flask, render_template, request, session,redirect, url_for
import hvac
_is_initialized = False
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
load_dotenv()

def get_vault_client():
    vault_url = os.environ.get('VAULT_ADDR', 'http://72.146.232.109:8200')
    client = hvac.Client(url=vault_url)
    
    # token authentication 
    vault_token = os.environ.get('VAULT_TOKEN')
    print(f"Vault token: {vault_token}")
    if vault_token:
        client.token = vault_token
    
    return client

# Function to get secrets from Vault
def get_secret(path, key=None):
    client = get_vault_client()
    
    try:
        response = client.secrets.kv.v2.read_secret_version(path=path)
        
        # Extract just the data portion
        secret_data = response['data']['data']
        
        # Return specific key or all data
        if key and key in secret_data:
            return secret_data[key]
        return secret_data
    
    except Exception as e:
        app.logger.error(f"Error fetching secret from Vault: {str(e)}")
        return None

@app.before_request
def configure_app():
    global _is_initialized
    
    # Only run once
    if not _is_initialized:    
        # Get API keys from Vault
        weather_api = get_secret('myapp/config', 'weather_api')
        if weather_api:
            app.config['weather_api'] = weather_api
        
        # Get other secrets if needed
        SuperSecret = get_secret('myapp/config', 'SuperSecret')
        if SuperSecret:
            app.config['SuperSecret'] = SuperSecret
        _is_initialized = True


def send_api_request(search_value:str):
    print("sent another request")
    key = app.config['weather_api']
    r = requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{search_value}/next7days?unitGroup=metric&elements=datetime%2Ctempmax%2Ctempmin%2Chumidity&include=days&key={key}&contentType=json")
    if r.status_code == 400:
        return "Error"
    j = r.json()
    return j

@app.route("/results")
def get_results():

    country_name = request.args.get('Country_Name')
    if country_name == "":
        redirect("/weather")
    if not session.get(country_name):
        print(country_name)
        json_val = send_api_request(country_name)
        if json_val == "Error":
            return redirect(url_for("home"))
        returned_dict = {}
        for i in json_val["days"]:
            returned_dict.update({i['datetime']: (i['tempmax'], i['tempmin'], i['humidity'])})
        session[country_name] = returned_dict
        return render_template('weather_for_country.html', Title=country_name, Start_Time=list(returned_dict.items())[0][0], End_Time=list(returned_dict.items())[-1][0], Week_Forcast=returned_dict.items())
    else:
        returned_dict = session.get(country_name)
        return render_template('weather_for_country.html', Title=country_name, Start_Time=list(returned_dict.items())[0][0], End_Time=list(returned_dict.items())[-1][0], Week_Forcast=returned_dict.items())


@app.route("/")
def home():
    # Pass the SuperSecret value to the template
    return render_template('base.html', title="Weather forcast with nitzan", cur_ip="0.0.0.0", SuperSecret=app.config.get('SuperSecret', 'No secret available'))


if __name__ == "__main__":
  
  app.run()
