import datetime

import pytest
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class DateTimeRequest(BaseModel):
    currentDateTime: str

russian_holidays = {
    "01-01": "Новый год",
    "01-07": "Рождество Христово",
    "02-23": "День защитника Отечества",
    "03-08": "Международный женский день",
    "05-01": "Праздник Весны и Труда",
    "05-09": "День Победы",
    "06-12": "День России",
    "11-04": "День народного единства",
    "12-31": "Канун Нового года"
}
@pytest.mark.slow
@app.post('/what_is_today')
def what_is_today(request: DateTimeRequest):
    try:
        date_str = request.currentDateTime
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%MZ")

        month_day = date_obj.strftime("%m-%d")
        holiday = russian_holidays.get(month_day, "Сегодня нет праздников в России.")

        return {'message': holiday}

    except ValueError:
        return HTTPException(status_code=400, detail="Некорректный формат даты. Используйте формат 'YYYY-MM-DDTHH:MMZ'.")

@app.get("/ping")
def ping():
    return "PONG"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",  port=16002)
