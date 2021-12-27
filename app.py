from bs4 import BeautifulSoup
import requests

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.covidprac

from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('totalDetail.html')


@app.route('/api/update', methods=['POST'])
def update_covid():
    date_receive = request.form['date_give']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
    params = {'serviceKey': 'yx+XZVAzlekEeTqRQnfaGBfU6iS30Kd0Sr00VxKyS1fUSjse081rPIM/P7x3kpMttOODo/kF6O/Kzg0g/KTVgQ==',
              'pageNo': '1', 'numOfRows': '10', 'startCreateDt': date_receive, 'endCreateDt': date_receive}

    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = soup.find_all('item')

    for item in data:
        gubun = item.find('gubun').get_text()
        incDec = item.find('incdec').get_text()
        localOccCnt = item.find('localocccnt').get_text()
        overFlowCnt = item.find('overflowcnt').get_text()
        defCnt = item.find('defcnt').get_text()
        isolClearCnt = item.find('isolclearcnt').get_text()
        deathCnt = item.find('deathcnt').get_text()

        doc = {
            'gubun': gubun,
            'incDec': incDec,
            'localOccCnt': localOccCnt,
            'overFlowCnt': overFlowCnt,
            'defCnt': defCnt,
            'isolClearCnt': isolClearCnt,
            'deathCnt': deathCnt
        }
        db.covids.insert_one(doc)


    return jsonify({'date': date_receive})


@app.route('/api/totalDetail', methods=['GET'])
def show_covid():
    total_detail = list(db.covids.find({},{'_id':False}))
    db.covids.delete_many({})
    return jsonify({'total_detail': total_detail})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)