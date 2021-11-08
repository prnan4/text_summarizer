from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status, Query
import uvicorn
import time
import datetime
import configparser
from tf_idf.summariser import summariser
from redact_text.philter import philter
from datewise_extractor.date_regex import date_regex
config = configparser.ConfigParser()
config.read('config.ini')

HTTPS_PORT = config['ADDRESS']['HTTPS_PORT']
app = FastAPI(
    title="Doctext",
    description="To summarise date wise observations in In-patient medical charts",
    version="1.0.0",
)
REDUCTION_RATE = float(config['TF_IDF']['REDUCTION_RATE'])
REL_VALUE = False
if config['TF_IDF']['REL_VALUE'].lower() == "true": REL_VALUE = True

redact_obj = philter()

# Create object of class summariser
sum_obj = summariser()
sum_obj.set_reduction_rate(REDUCTION_RATE)
sum_obj.set_relation_value(REL_VALUE)

@app.get("/health_check")
async def health_check():
    message = {'version': "1.0", 'status': "I am Running", "requestTimeStamp": datetime.datetime.now(),
              "responseTimeStamp": datetime.datetime.now()}
    return message


@app.post("/text_summarizer")
async def get_summary_from_text(txt: Optional[str] = Query(None), min_length=0):
    start = time.time()
    content = {'original_text': txt}

    if min_length == 0:
        return {'ERROR MESSAGE': 'Section text cannot be empty'}

    # Redact text
    # redact_obj = philter()
    # redacted_text = redact_obj.philter_text(txt)

    # Create object of class summariser
    sum_obj = summariser()
    sum_obj.set_reduction_rate(REDUCTION_RATE)
    sum_obj.set_text(txt)
    sum_obj.set_relation_value(REL_VALUE)
    summarised_text = sum_obj.get_summarised_text()
    content['summarised_text'] = summarised_text

    end = time.time()
    content['time_taken'] = round(end - start, 5)
    content['api_name'] = "text_summarizer"
    return content


@app.post("/datewise_summarizer")
async def get_datewise_summary(txt: Optional[str] = Query(None)):
    start = time.time()
    content = {}
    if len(txt) == 0:
        return {'ERROR MESSAGE': 'Section text cannot be empty'}

    regex_obj = date_regex()
    # extracting the date indexes
    dates, txt = regex_obj.set_replace_date(txt)
    # Redact text
    txt = redact_obj.philter_text(txt)

    txt = regex_obj.reset_replace_date(dates, txt)
    # Date wise content extraction
    date_txt_dict = regex_obj.get_date_wise_content(dates, txt)

    summarized_dict = []

    content["duration_of_stay"] = len(date_txt_dict)

    for date in date_txt_dict:
        date_entity = {}
        txt = date_txt_dict[date]
        sum_obj.set_text(txt)
        summarised_text = sum_obj.get_summarised_text()
        sum_obj.set_obj_null()

        date_entity['date'] = date
        date_entity['summary'] = summarised_text.strip()
        summarized_dict.append(date_entity)

    end = time.time()
    content["date_wise_summary"] = summarized_dict
    content['time_taken'] = round(end - start, 5)
    content['api_name'] = "In Patient Chart Datewise Summarizer"
    return content


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(HTTPS_PORT))
