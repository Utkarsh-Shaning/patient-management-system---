from pydantic import BaseModel,EmailStr,Field,field_validator,model_validator,computed_field
from typing import List,Dict,Optional,Annotated
#In Pydantic, Annotated is used to attach metadata to type hints, allowing additional validation and customization. It is often used alongside Field to define constraints

class Patient(BaseModel):

    name: str
    email: EmailStr
    age: int =Field(gt=22,lt=98)
    height: float
    weight:Annotated[float, Field(gt=0, strict=True)]
    married:Optional[bool] = None
    allergies:List[str]
    contact:Dict[str,str]

    @computed_field
    @property
    def calculate_bmi(self)->float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @model_validator(mode='after')
    def validate_emergency_contact(cls,model):
        if model.age >60 and 'emergency' not in model.contact:
            raise ValueError('Patient older than 60 must have an emergency contact')
        return model

    @field_validator('email')
    @classmethod
    def emial_validator(cls,value):

        valid_domain = ['hdfc.com','icici.com']
        domain_name = value.split('@')[-1]
        if domain_name not in valid_domain:
            raise ValueError('Not a valid domain')
        return value
    

def inser_patient_data(patient: Patient):

    print(patient.name)
    print(patient.age)
    print(patient.weight)
    print(patient.married)
    print(patient.allergies)
    print(patient.contact)
    print(patient.calculate_bmi)
    print('inserted')

patient_info = {"name": "utkarsh",'email':'udit@icici.com',"age":93,'height':"5.2",'weight':63.2,
                'allergies':['dust','curd'],'contact':{'phone':'9201374403','emergency':'9424218911'}}

patient1 = Patient(**patient_info)

inser_patient_data(patient1)

















