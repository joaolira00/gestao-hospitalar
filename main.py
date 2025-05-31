from fastapi import FastAPI
import models.pacient_model as pacient_model
from database.database import engine
from scalar_fastapi import get_scalar_api_reference
from auth import auth
from routers import pacients, appointments

app = FastAPI()

pacient_model.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(pacients.router)
app.include_router(appointments.router)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )