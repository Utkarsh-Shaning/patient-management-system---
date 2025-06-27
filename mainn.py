from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
app = FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(..., description='ID of the patient', examples=['p1'])]
    name:Annotated[str, Field(..., description='Name of the patient')]
    city:Annotated[str, Field(..., description='City where yje paitent is living')]
    age:Annotated[int, Field(..., gt=0,lt=120,description='Age of the patient')]
    gender:Annotated[Literal['male','female','others'], Field(..., description='Gender of the patient')]
    height:Annotated[float, Field(..., gt=0,description='Heiight of the patient in mtrs')]
    weight:Annotated[float, Field(..., gt=0,description='Weight of the patient in mtrs')]

    @computed_field
    @property
    def bmi(self)->float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi<30:
            return 'Noremal'
        else:
            return 'Obese'
        
class PatientUpdate(BaseModel):
    name:Annotated[Optional[str], Field(default=None)]
    city:Annotated[Optional[str], Field(default=None)]
    age:Annotated[Optional[int], Field(default=None, gt=0)]
    gender:Annotated[Optional[Literal['male','female','others']], Field(default=None)]
    height:Annotated[Optional[float], Field(default=None,gt=0)]
    weight:Annotated[Optional[float], Field(default=None,gt=0)]


def load_data():
    try:
        with open('patient.json', 'r') as a:
            data = json.load(a)
        return data
    except Exception as e:
        return {"error": str(e)}
    

def save_data(data):
    with open('patient.json','w') as f:
        json.dump(data,f)


@app.get("/about")
def hello():
    return {'message':'A fully functional API for patient records'}

@app.get('/home')
def about():
    return {'message':'Patient Management System API'}

@app.get('/view')
def view():
    data = load_data()

    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id:str= Path(..., description='id of the patient in DB',example='p1')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail='Record does not exist')

@app.get('/sort')

def sort_patient(sort_by:str = Query(..., description='sort on the basis ' \
'of height,weight,bmi'), order: str = Query('asc', description = 'sort in asc or desc')):
    
    valid_fields = ['height_cm','weight_kg','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid filed select from {valid_fields}")
        
    if order not in ['asc','desc']:
        raise HTTPException(status_code= 400, detail='Invalid order select between asc and desc')
    
    data = load_data()
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data.values(),key=lambda x: x.get(sort_by,0),reverse=sort_order)#True- desending False-Ascending

    return sorted_data


@app.post('/create')
def create_patient(patient:Patient):
    #load existing data
    data = load_data()
    #check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
    #new patient add to the database or json file
    data[patient.id] = patient.model_dump(exclude=['id'])

    #save into json file
    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created succesffully'})


@app.put('/edit/{patient_id}')
def update_patient(patient_id : str, patient_update : PatientUpdate):

    data = load_data()

    if patient_id not in data:
       raise HTTPException(status_code=404,detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key,value in updated_patient_info.items():
        existing_patient_info[key] = value

    
    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    existing_patient_info=patient_pydantic_obj.model_dump(exclude='id')
    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'Patient updatated'}) 
   


@app.delete('/delete{patient_id}')
def delete_patient(patient_id:str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient id not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=202, content='Patient deleted')
