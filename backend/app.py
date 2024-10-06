from flask import Flask, request, send_file, jsonify, url_for, send_from_directory
from flask_cors import CORS
import subprocess
import os
import anthropic
import base64
from io import BytesIO
import ee
import requests
import matplotlib.pyplot as plt
from PIL import Image
import json
import pandas as pd

client = anthropic.Anthropic(
    api_key = 'your-api-key'
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # This allows all origins

ee.Authenticate()
ee.Initialize(project='project-name')

leads_path = 'leads.json' # OR provided by the user

@app.route('/upload', methods=['POST'])
def upload():

    if 'file' not in request.files:
        return jsonify(error='No file part'), 400

    file = request.files['file']
    leads_file = read_json(leads_path)

    if file.filename == '':
        return jsonify(error='No selected file'), 400

    if file and file.filename.endswith('.csv'):
        # Save the file temporarily
        temp_path = 'temp.csv'
        file.save(temp_path)

        FINAL = analyse_docs(temp_path, leads_file)

        return jsonify(output = FINAL)

    else:
        return jsonify(error='Invalid file type. Please upload a CSV file.'), 400

def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def analyse_docs(file_path, leads_file):

    FINAL = []

    usage_data = pd.read_csv(file_path)

    for i in range(len(usage_data.Item.values)):
        supplier = usage_data.loc[i].Manufacturer
        item = usage_data.loc[i].Item
        description = usage_data.loc[i].Description
        latitude = usage_data.loc[i].Latitude
        longitude = usage_data.loc[i].Longitude

        final_response = geo_query(supplier, description, latitude, longitude)
        final_response = json.loads(final_response)

        activity = final_response['activity']
        confidence = final_response['confidence']
        risk = final_response['risk']
        explanation = final_response['explanation']
        
        alt_suppliers = ''
        if risk > 7:
            alt_suppliers = leads_file[str(item)]

        entry = {"supplier": supplier, "item": item, "description": description, "activity": activity, "confidence": confidence, "risk": risk, "explanation": explanation, "alt_suppliers": alt_suppliers}
        
        FINAL.append(entry)

    return FINAL
        
def geo_query(supplier, part, latitude, longitude):

    # Extracting geo image for the manufacturing facility
    sat_img = geo_img(latitude, longitude)

    # Passing through mistral to count infra
    llm_vision_response = llm_vision(sat_img)
    llm_vision_response = json.loads(llm_vision_response)

    # Extracting num of buildings and damage
    num_buildings = llm_vision_response["num_buildings"]
    damage = llm_vision_response["damage"]

    # Reasoning
    reasoning = llm_reasoning(supplier, part)

    # Overall decision
    final_response = llm_master(num_buildings, damage, reasoning)

    return final_response

def geo_img(latitude, longitude):

    point = ee.Geometry.Point([longitude, latitude])

    # Select a satellite image dataset (Sentinel-2 in this case)
    satellite_image = ee.ImageCollection('COPERNICUS/S2') \
        .filterBounds(point) \
        .sort('CLOUD_COVER') \
        .first()

    # Set visualization parameters (RGB bands)
    vis_params = {
        'min': 500,
        'max': 3000,
        'bands': ['B4', 'B3', 'B2']  # Red, Green, Blue bands for true-color imagery
    }

    # Define a more zoomed-in region around the GPS point (e.g., a 500 meter x 500 meter area)
    region = point.buffer(200).bounds().getInfo()['coordinates']  # 500 meters

    # Get the URL of the satellite image
    image_url = satellite_image.getThumbURL({
        'min': 500,
        'max': 3000,
        'dimensions': 2048,  # Increase the resolution to make it more detailed
        'region': region,    # Zoomed-in area around the GPS point
        'format': 'png',
        'bands': ['B4', 'B3', 'B2']  # RGB bands
    })

    # Download the image from the URL
    response = requests.get(image_url)

    # Open the image with PIL
    img = Image.open(BytesIO(response.content))

    return img

def encode_image(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")  # Specify the format (e.g., PNG, JPEG)
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_base64

def llm_vision(img):
    #key = 'YyaY27Dif3szg7yHg5mAxSVNWCJELOM3'
    image_data = encode_image(img)

    question = f"""
    You are an AI assistant and you are given the following satelite image with manufacturing site positioned in the middle. Your job is to determine the number of buildings (integer) from the given image as well as whether there has been any visible damage to the facilities (boolean).
    The image is extremely low resolution, but you must provide your best estimations.
    Your entire response must be valid JSON. Use 'num_buildings' and 'damage' as keys.
    """
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ],
            }
        ],
    )
    
    return message.content[0].text

def llm_reasoning(supplier, part):

    question = f"""
    Imagine you are a supply chain specialist tasked to evaluate fitness of the following company in delivering the following medical item in time.
    Company: {supplier}
    Item: {part}

    Based on your knowledge so far, please provide short recommendation for whether or not there is a risk of them delivering part in time. Be as brief as possible.
    While evaluating, take into consideration the materials used for the manufacturing of the part (there might be some disruption there), complexity of the part, size of the firm.
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        messages=[
            {'role': 'user', 'content': question}
        ]
    )

    return message.content[0].text

def llm_master(num_buildings, damage, summary):

    question = f"""
    Imagine you are a supply chain specialist tasked to evaluate fitness of the following company in delivering medical item in time. You have some data available to you that should aid your decision making process.
    Previous evaluation from another model: 
    {summary}

    Number of building within manufacturing site (useful to evaluate infrastructure):
    {num_buildings}

    Whether or not there is any damage in the manufacturing site:
    {damage}

    Please provide your response in a structured way, providing activity score (integer between 1-10, represents facilities), confidence score (integer 1-10, represents expert sentiment), overall risk score (integer 1-10, infered from previous metrics), explanation (1 sentence explaining the decision betweem risk score, but don't mention exact numbers).
    Your entire response must be valid JSON. Use 'activity', 'confidence', 'risk', 'explanation' as keys.
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        messages=[
            {'role': 'user', 'content': question}
        ]
    )

    return message.content[0].text


if __name__ == '__main__':
    port = 5000#int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)