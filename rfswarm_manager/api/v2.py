# routers/users.py
from fastapi import APIRouter, Request, Depends, Body, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v2", tags=["v2"])

# 1. This helper function extracts your core reference from the app state
def get_core(request: Request):
	return request.app.state.core

def get_base(request: Request):
	return request.app.state.base


# this is just a placeholder untill we build the v2 api's
@router.get("/")
def get_index(core=Depends(get_core), base=Depends(get_base)):
	# Give the api endpoints to users
	res = base.qhandler._index()

	if int(res['status']) > 399:
		raise HTTPException(status_code=int(res['status']), detail=res['message'])

	return JSONResponse(status_code=int(res['status']), content=res['message'])
