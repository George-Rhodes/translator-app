from flask import Flask, render_template
from os import getenv
import uuid, json, requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

app = Flask(__name__)


keyVaultName = os.environ["KEY_VAULT_NAME"]
KVU = f"https://{keyVaultName}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVU, credential=credential)
S-key = client.get_secret("SECRET-KEY").value
service_endpoint = client.get_secret("TRANSLATE-END").value
sub_key = client.get_secret("TRANSLATE-KEY").value



app.config['SECRET_KEY']= S-key 

langs = requests.get('https://api.cognitive.microsofttranslator.com/languages?api-version=3.0')
langs = langs.json()
languages = []
for lang in langs['translation']:
    languages.append((lang,langs['translation'][lang]['nativeName']))

class TranslateForm(FlaskForm):

    sentence = StringField('Enter Some Text')
    language = SelectField('Language',
        choices=languages)
    submit = SubmitField('Translate')

@app.route('/', methods=['GET', 'POST'])
def translate():
    form = TranslateForm()
    response = ""
    if form.validate_on_submit():
        subscription_key = sub_key
        endpoint = service_endpoint
        addition = "translate?api-version=3.0&to="
        headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'westeurope',
        'Content-Type':'application/json'
        }
        body = [{
        'Text': form.sentence.data
        }]
        constructed_url = endpoint + addition + form.language.data
        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()
        response = response[0]['translations'][0]['text']
    return render_template('index.html', form=form, translation=response)


if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0')