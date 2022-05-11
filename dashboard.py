from flask import Flask, render_template, request, jsonify
import flask
import pandas as pd
from datetime import datetime
import plotly.express as px
import json
import plotly
import pytz
from PIL import Image
import cv2
import base64
import io


app = Flask(__name__)

@app.route("/images", methods=["POST"])
def process_image():
#     file = request.files['file']
#     # Read the image via file.stream
#     img = Image.open(file.stream)
    
#     payload = request.form.to_dict()
#     title =  payload['name']
   
     # get the base64 encoded string
    im_b64 = request.json['image']
    type_sense = request.json['sensor_type']
    name_current = request.json['name']
    # convert it into bytes  
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))
    name = type_sense + str(name_current) 
    name = name.split('.')
    name = name[0].replace(" ", "")
    name = name.replace("-", "_")
    name = name.replace(":", "_")
    name = name + '.jpg'
    
    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))
    img = img.convert('RGB')
    img.save('/home/ubuntu/Farming/images/'+name)
    width, height = img.size
    #file.save('images/'+title)
    return jsonify({'msg': 'success', 'size': [width, height ]})


#publish online
@app.route("/dash", methods=['POST','GET'])
def options():
   
    eastern = pytz.timezone('US/Eastern')
    df=pd.read_csv("sensor_data/data.csv") 
    #argList = request.json()

    if  flask.request.method == 'POST':
        
        temp =  request.form['Data']
      
        sensor =  request.form['sensor_type']
      
        current_datetime = datetime.now(eastern)
        current_datetime = current_datetime.strftime("%d/%m/%Y %H:%M:%S")
        ls = {
                        'Sensor':sensor,
                        'Result':temp,
                        'Time': current_datetime
                        
                    }
        
        data2 = pd.DataFrame([ls])
        df = pd.concat([df, data2])
        print('request completed')
        df.to_csv('sensor_data/data.csv',index=False)
        fig = px.scatter(df, x="Time", y="Result", hover_name="Sensor")
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('index.html', tables=[df.to_html()], titles=df.columns.values,graphJSON=graphJSON )
    fig = px.scatter(df, x="Time", y="Result", hover_name="Sensor")
    print('no request')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', tables=[df.to_html()], titles=df.columns.values,graphJSON=graphJSON)
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)
