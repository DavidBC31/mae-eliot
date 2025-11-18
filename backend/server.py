from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('SECRET_KEY', 'votre-cle-secrete-super-securisee-changez-moi')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = await db.users.find_one({"_id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Models
class UserSignup(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Punition(BaseModel):
    date: str
    nature: str
    raison: str

class Orgasme(BaseModel):
    date: str
    type: str
    notes: Optional[str] = ""

class CarnetEntry(BaseModel):
    date: str
    content: str

class Histoire(BaseModel):
    title: str
    date: str
    content: str

class Lien(BaseModel):
    title: str
    url: str
    description: Optional[str] = ""

class Seance(BaseModel):
    date: str
    title: str
    description: Optional[str] = ""
    duration: Optional[str] = ""

class InventaireItem(BaseModel):
    name: str
    category: Optional[str] = ""
    description: Optional[str] = ""
    quantity: int = 1

class Document(BaseModel):
    title: str
    url: str
    description: Optional[str] = ""

class Idee(BaseModel):
    title: str
    description: Optional[str] = ""
    theme: str
    sous_theme: Optional[str] = ""

class De10Option(BaseModel):
    number: int
    text: str

class De10List(BaseModel):
    name: str
    items: List[str] = Field(default_factory=lambda: [""] * 10)

class Rituel(BaseModel):
    number: int
    text: str

# Auth Routes
@api_router.post("/auth/signup")
async def signup(user: UserSignup):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Un compte avec cet email existe déjà")
    
    # Create user
    user_id = str(uuid.uuid4())
    new_user = {
        "_id": user_id,
        "email": user.email,
        "password": hash_password(user.password),
        "created_at": datetime.utcnow().isoformat()
    }
    await db.users.insert_one(new_user)
    
    return {"message": "Compte créé avec succès"}

@api_router.post("/auth/login")
async def login(user: UserLogin):
    # Find user
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create token
    access_token = create_access_token(data={"sub": db_user["_id"]})
    
    return {
        "token": access_token,
        "user": {
            "id": db_user["_id"],
            "email": db_user["email"]
        }
    }

# Punitions
@api_router.get("/punitions")
async def get_punitions(current_user: dict = Depends(get_current_user)):
    punitions = await db.punitions.find({"user_id": current_user["_id"]}).to_list(1000)
    return punitions

@api_router.post("/punitions")
async def create_punition(punition: Punition, current_user: dict = Depends(get_current_user)):
    punition_dict = punition.dict()
    punition_dict["_id"] = str(uuid.uuid4())
    punition_dict["user_id"] = current_user["_id"]
    await db.punitions.insert_one(punition_dict)
    return punition_dict

@api_router.put("/punitions/{id}")
async def update_punition(id: str, punition: Punition, current_user: dict = Depends(get_current_user)):
    await db.punitions.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": punition.dict()})
    return {"message": "Updated"}

@api_router.delete("/punitions/{id}")
async def delete_punition(id: str, current_user: dict = Depends(get_current_user)):
    await db.punitions.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Orgasmes
@api_router.get("/orgasmes")
async def get_orgasmes(current_user: dict = Depends(get_current_user)):
    orgasmes = await db.orgasmes.find({"user_id": current_user["_id"]}).to_list(1000)
    return orgasmes

@api_router.post("/orgasmes")
async def create_orgasme(orgasme: Orgasme, current_user: dict = Depends(get_current_user)):
    orgasme_dict = orgasme.dict()
    orgasme_dict["_id"] = str(uuid.uuid4())
    orgasme_dict["user_id"] = current_user["_id"]
    await db.orgasmes.insert_one(orgasme_dict)
    return orgasme_dict

@api_router.delete("/orgasmes/{id}")
async def delete_orgasme(id: str, current_user: dict = Depends(get_current_user)):
    await db.orgasmes.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Carnet Intime
@api_router.get("/carnet")
async def get_carnet(current_user: dict = Depends(get_current_user)):
    entries = await db.carnet.find({"user_id": current_user["_id"]}).to_list(1000)
    return entries

@api_router.post("/carnet")
async def create_carnet_entry(entry: CarnetEntry, current_user: dict = Depends(get_current_user)):
    entry_dict = entry.dict()
    entry_dict["_id"] = str(uuid.uuid4())
    entry_dict["user_id"] = current_user["_id"]
    await db.carnet.insert_one(entry_dict)
    return entry_dict

@api_router.put("/carnet/{id}")
async def update_carnet_entry(id: str, entry: CarnetEntry, current_user: dict = Depends(get_current_user)):
    await db.carnet.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": entry.dict()})
    return {"message": "Updated"}

@api_router.delete("/carnet/{id}")
async def delete_carnet_entry(id: str, current_user: dict = Depends(get_current_user)):
    await db.carnet.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Similar CRUD endpoints for all other collections
# Histoires
@api_router.get("/histoires")
async def get_histoires(current_user: dict = Depends(get_current_user)):
    histoires = await db.histoires.find({"user_id": current_user["_id"]}).to_list(1000)
    return histoires

@api_router.post("/histoires")
async def create_histoire(histoire: Histoire, current_user: dict = Depends(get_current_user)):
    histoire_dict = histoire.dict()
    histoire_dict["_id"] = str(uuid.uuid4())
    histoire_dict["user_id"] = current_user["_id"]
    await db.histoires.insert_one(histoire_dict)
    return histoire_dict

@api_router.put("/histoires/{id}")
async def update_histoire(id: str, histoire: Histoire, current_user: dict = Depends(get_current_user)):
    await db.histoires.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": histoire.dict()})
    return {"message": "Updated"}

@api_router.delete("/histoires/{id}")
async def delete_histoire(id: str, current_user: dict = Depends(get_current_user)):
    await db.histoires.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Liens
@api_router.get("/liens")
async def get_liens(current_user: dict = Depends(get_current_user)):
    liens = await db.liens.find({"user_id": current_user["_id"]}).to_list(1000)
    return liens

@api_router.post("/liens")
async def create_lien(lien: Lien, current_user: dict = Depends(get_current_user)):
    lien_dict = lien.dict()
    lien_dict["_id"] = str(uuid.uuid4())
    lien_dict["user_id"] = current_user["_id"]
    await db.liens.insert_one(lien_dict)
    return lien_dict

@api_router.put("/liens/{id}")
async def update_lien(id: str, lien: Lien, current_user: dict = Depends(get_current_user)):
    await db.liens.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": lien.dict()})
    return {"message": "Updated"}

@api_router.delete("/liens/{id}")
async def delete_lien(id: str, current_user: dict = Depends(get_current_user)):
    await db.liens.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Séances
@api_router.get("/seances")
async def get_seances(current_user: dict = Depends(get_current_user)):
    seances = await db.seances.find({"user_id": current_user["_id"]}).to_list(1000)
    return seances

@api_router.post("/seances")
async def create_seance(seance: Seance, current_user: dict = Depends(get_current_user)):
    seance_dict = seance.dict()
    seance_dict["_id"] = str(uuid.uuid4())
    seance_dict["user_id"] = current_user["_id"]
    await db.seances.insert_one(seance_dict)
    return seance_dict

@api_router.put("/seances/{id}")
async def update_seance(id: str, seance: Seance, current_user: dict = Depends(get_current_user)):
    await db.seances.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": seance.dict()})
    return {"message": "Updated"}

@api_router.delete("/seances/{id}")
async def delete_seance(id: str, current_user: dict = Depends(get_current_user)):
    await db.seances.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Inventaire
@api_router.get("/inventaire")
async def get_inventaire(current_user: dict = Depends(get_current_user)):
    items = await db.inventaire.find({"user_id": current_user["_id"]}).to_list(1000)
    return items

@api_router.post("/inventaire")
async def create_inventaire_item(item: InventaireItem, current_user: dict = Depends(get_current_user)):
    item_dict = item.dict()
    item_dict["_id"] = str(uuid.uuid4())
    item_dict["user_id"] = current_user["_id"]
    await db.inventaire.insert_one(item_dict)
    return item_dict

@api_router.put("/inventaire/{id}")
async def update_inventaire_item(id: str, item: InventaireItem, current_user: dict = Depends(get_current_user)):
    await db.inventaire.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": item.dict()})
    return {"message": "Updated"}

@api_router.delete("/inventaire/{id}")
async def delete_inventaire_item(id: str, current_user: dict = Depends(get_current_user)):
    await db.inventaire.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Documents
@api_router.get("/documents")
async def get_documents(current_user: dict = Depends(get_current_user)):
    documents = await db.documents.find({"user_id": current_user["_id"]}).to_list(1000)
    return documents

@api_router.post("/documents")
async def create_document(doc: Document, current_user: dict = Depends(get_current_user)):
    doc_dict = doc.dict()
    doc_dict["_id"] = str(uuid.uuid4())
    doc_dict["user_id"] = current_user["_id"]
    await db.documents.insert_one(doc_dict)
    return doc_dict

@api_router.delete("/documents/{id}")
async def delete_document(id: str, current_user: dict = Depends(get_current_user)):
    await db.documents.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Idées
@api_router.get("/idees")
async def get_idees(current_user: dict = Depends(get_current_user)):
    idees = await db.idees.find({"user_id": current_user["_id"]}).to_list(1000)
    return idees

@api_router.post("/idees")
async def create_idee(idee: Idee, current_user: dict = Depends(get_current_user)):
    idee_dict = idee.dict()
    idee_dict["_id"] = str(uuid.uuid4())
    idee_dict["user_id"] = current_user["_id"]
    await db.idees.insert_one(idee_dict)
    return idee_dict

@api_router.put("/idees/{id}")
async def update_idee(id: str, idee: Idee, current_user: dict = Depends(get_current_user)):
    await db.idees.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": idee.dict()})
    return {"message": "Updated"}

@api_router.delete("/idees/{id}")
async def delete_idee(id: str, current_user: dict = Depends(get_current_user)):
    await db.idees.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Dé 10
@api_router.get("/de10")
async def get_de10(current_user: dict = Depends(get_current_user)):
    options = await db.de10.find({"user_id": current_user["_id"]}).to_list(1000)
    return options

@api_router.post("/de10")
async def create_de10_option(option: De10Option, current_user: dict = Depends(get_current_user)):
    option_dict = option.dict()
    option_dict["_id"] = str(uuid.uuid4())
    option_dict["user_id"] = current_user["_id"]
    await db.de10.insert_one(option_dict)
    return option_dict

@api_router.put("/de10/{id}")
async def update_de10_option(id: str, option: De10Option, current_user: dict = Depends(get_current_user)):
    await db.de10.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": option.dict()})
    return {"message": "Updated"}

@api_router.delete("/de10/{id}")
async def delete_de10_option(id: str, current_user: dict = Depends(get_current_user)):
    await db.de10.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Rituels
@api_router.get("/rituels")
async def get_rituels(current_user: dict = Depends(get_current_user)):
    rituels = await db.rituels.find({"user_id": current_user["_id"]}).to_list(1000)
    return rituels

@api_router.post("/rituels")
async def create_rituel(rituel: Rituel, current_user: dict = Depends(get_current_user)):
    rituel_dict = rituel.dict()
    rituel_dict["_id"] = str(uuid.uuid4())
    rituel_dict["user_id"] = current_user["_id"]
    await db.rituels.insert_one(rituel_dict)
    return rituel_dict

@api_router.put("/rituels/{id}")
async def update_rituel(id: str, rituel: Rituel, current_user: dict = Depends(get_current_user)):
    await db.rituels.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": rituel.dict()})
    return {"message": "Updated"}

@api_router.delete("/rituels/{id}")
async def delete_rituel(id: str, current_user: dict = Depends(get_current_user)):
    await db.rituels.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Dé 10 - Listes thématiques
@api_router.get("/de10lists")
async def get_de10lists(current_user: dict = Depends(get_current_user)):
    lists = await db.de10lists.find({"user_id": current_user["_id"]}).to_list(1000)
    return lists

@api_router.post("/de10lists")
async def create_de10list(de10list: De10List, current_user: dict = Depends(get_current_user)):
    list_dict = de10list.dict()
    list_dict["_id"] = str(uuid.uuid4())
    list_dict["user_id"] = current_user["_id"]
    await db.de10lists.insert_one(list_dict)
    return list_dict

@api_router.put("/de10lists/{id}")
async def update_de10list(id: str, de10list: De10List, current_user: dict = Depends(get_current_user)):
    await db.de10lists.update_one({"_id": id, "user_id": current_user["_id"]}, {"$set": de10list.dict()})
    return {"message": "Updated"}

@api_router.delete("/de10lists/{id}")
async def delete_de10list(id: str, current_user: dict = Depends(get_current_user)):
    await db.de10lists.delete_one({"_id": id, "user_id": current_user["_id"]})
    return {"message": "Deleted"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()