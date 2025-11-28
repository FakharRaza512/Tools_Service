#from fastapi import FastAPI
#from routes.parse_route import router as parse_router

#app = FastAPI(title="Tools Service", version="1.0")

#app.include_router(parse_router)

#@app.get("/")
#def root():
#    return {"message": "Tools Service Running (Parser Tools Ready)"}
# onstartup function 
# health function 


from fastapi import FastAPI

# Routers
from routes.parse_route import router as parse_router
from routes.aspect_route import router as aspect_router


app = FastAPI(
    title="Tools Service",
    version="1.0",
    description="Parser Tools + Aspect Analysis Tools"
)

# Register Routers
app.include_router(parse_router)
app.include_router(aspect_router)


@app.get("/")
def root():
    return {
        "message": "Tools Service Running (Parser + Aspect Tools Ready)"
    }
