Sure, here is a Python script using FastAPI to create an endpoint for converting temperatures.

The file `main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Utility functions
def celsius_to_fahrenheit(celsius: float):
    return round((celsius * 9/5) + 32, 2)

def fahrenheit_to_celsius(fahrenheit: float):
    return round((fahrenheit - 32) * 5/9, 2)

class Temp(BaseModel):
    scale: str
    value: float

@app.post("/convert_temp")
async def convert_temp(temp: Temp):
    if temp.scale.lower() not in ['celsius', 'fahrenheit']:
        raise HTTPException(status_code=400, detail="Invalid temperature scale.")
    
    if temp.scale.lower() == 'celsius':
        return {"fahrenheit": celsius_to_fahrenheit(temp.value)}
    else:
        return {"celsius": fahrenheit_to_celsius(temp.value)}
```

In this code, we define two utility functions `celsius_to_fahrenheit` and `fahrenheit_to_celsius` to convert between temperature scales. Then we have a POST endpoint "/convert_temp" that takes a temperature and a scale ('celsius' or 'fahrenheit') as input and returns the converted temperature. 

The `Temp` class is a Pydantic model that is used for data validation. It ensures the `scale` is a string and `value` is a float. If the `scale` is not 'celsius' or 'fahrenheit', a HTTP 400 error is returned.