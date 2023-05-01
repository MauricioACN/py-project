from fastapi import FastAPI, Body, Request, Query, status, HTTPException, Depends, Path
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from starlette.requests import Request
from jwt_manager import create_token,validate_token
from pydantic import BaseModel, Field
from typing import Optional,List
from fastapi.security import HTTPBearer
from config.database import Session, Base, engine
from models.clientes import Clientes as ClientesModel
from fastapi.encoders import jsonable_encoder
from middlewares.error_handler import ErrorHandler

app = FastAPI()

app.title = "Riskio APP"
app.version = "0.0.1"
app.add_middleware(ErrorHandler)

Base.metadata.create_all(bind= engine)

class User(BaseModel):
    email:str
    pasword:str

class JWTBearer(HTTPBearer):
    
    async def __call__(self, request: Request):
        auth =  await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Credenciales Invalidas")

class Cliente(BaseModel):
    
        # id:int = Field(ge=1,le=2000)
        nombre:str = Field(max_length=20,min_length=5)
        sector:str = Field(max_length=20,min_length=5)
        metodologia: Optional[int] = None
        pais:str = Field(max_length=20,min_length=4)
        
        class Config:
            schema_extra = {
                "example":{
                    "nombre":"Blau Farmaceutica",
                    'sector':'farmaceutico',
                    'metodologia':0,
                    'pais':'Colombia'
                }
            }
    
@app.post("/login",tags = ["auth"])
def login(user:User):
    if user.email=="admin@gmail.com" and user.pasword=="admin":
        token:str = create_token(data=user.dict())
        return JSONResponse(status_code= status.HTTP_200_OK,content=token)

@app.get("/clientes",tags=['clientes'], response_model=List[Cliente],status_code=status.HTTP_200_OK)
def get_clientes() -> List[Cliente]:
    db = Session()
    consulta = jsonable_encoder(db.query(ClientesModel).all())
    
    return JSONResponse(status_code=status.HTTP_200_OK,content=consulta) 

@app.get('/clientes/{id}',tags=["clientes"], dependencies=[Depends(JWTBearer())], response_model=Cliente)
def get_clientes(id:int) -> List[Cliente]:
    
    db = Session()
    consulta = db.query(ClientesModel).filter(ClientesModel.id ==id).first()
    if not consulta:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message":"No encontrado"})
    
    return JSONResponse(status_code=status.HTTP_200_OK,content=jsonable_encoder(consulta))

@app.get('/clientes/',tags = ["clientes"],response_model=List[Cliente])
def get_clientes_por_pais(pais:str) -> List[Cliente]:
    
    db = Session()
    consulta = db.query(ClientesModel).filter(ClientesModel.pais==pais).all()
    
    if not consulta:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"No encontrado"})
    
    return JSONResponse(status_code=status.HTTP_200_OK,content=jsonable_encoder(consulta))

@app.post('/clientes',tags = ["clientes"], response_model=dict, status_code= status.HTTP_200_OK)
def create_cliente(cliente:Cliente) -> dict:
    
    db = Session()
    new_cliente =  ClientesModel(**cliente.dict())
    db.add(new_cliente)
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f"Se ha registrado exitosamente el cliente {new_cliente.id}"})    

@app.delete('/clientes/{id}',tags=['clientes'], response_model=dict, status_code=status.HTTP_200_OK)
def delete_cliente(id:int) -> dict:
    db = Session()
    consulta = db.query(ClientesModel).filter(ClientesModel.id == id).first()
    
    if not consulta:    
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"No encontrado"})
    
    db.delete(consulta)
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f"El Cliente {id} ha sido eliminado con éxito!"})


@app.put('/clientes/{id}', tags = ['clientes'], response_model=dict, status_code=status.HTTP_200_OK)
def update_cliente(id:int,cliente:Cliente) -> dict:
    db = Session()
    consulta = db.query(ClientesModel).filter(ClientesModel.id == id)
    
    if not consulta.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"No encontrado"})
    
    consulta.update(cliente.dict(),synchronize_session=False)
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f"El Cliente {id} se ha actualizado con éxito!"})