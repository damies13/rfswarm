# routers/users.py
from fastapi import APIRouter, Request, Depends, Body, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1", tags=["v1"])

# 1. This helper function extracts your core reference from the app state
def get_core(request: Request):
    return request.app.state.core

def get_base(request: Request):
    return request.app.state.base




	# V1 API
	# GET
	# "/", 
@router.get("/")
def get_index(core=Depends(get_core), base=Depends(get_base)):
	# Give the api endpoints to users
	res = base.qhandler._index()

	if int(res['status']) > 399:
		raise HTTPException(status_code=int(res['status']), detail=res['message'])

	return JSONResponse(status_code=int(res['status']), content=res['message'])

	# POST
	# "/AgentStatus", 
	# 
@router.post("/AgentStatus")
def update_shared_status(payload: dict = Body(...), core=Depends(get_core), base=Depends(get_base)):
	res = base.qhandler._AgentStatus(payload)

	if int(res['status']) > 399:
		raise HTTPException(status_code=int(res['status']), detail=res['message'])

	return JSONResponse(status_code=int(res['status']), content=res['message'])

	# "/Jobs", 
@router.post("/Jobs")
def update_shared_status(payload: dict = Body(...), core=Depends(get_core), base=Depends(get_base)):
	res = base.qhandler._Jobs(payload)

	if int(res['status']) > 399:
		raise HTTPException(status_code=int(res['status']), detail=res['message'])

	return JSONResponse(status_code=int(res['status']), content=res['message'])

	# "/Scripts", 
@router.post("/Scripts")
def update_shared_status(payload: dict = Body(...), core=Depends(get_core), base=Depends(get_base)):
	res = base.qhandler._Scripts(payload)

	if int(res['status']) > 399:
		raise HTTPException(status_code=int(res['status']), detail=res['message'])

	return JSONResponse(status_code=int(res['status']), content=res['message'])

	# "/File", 
@router.post("/File")
def update_shared_status(payload: dict = Body(...), core=Depends(get_core), base=Depends(get_base)):
	res = base.qhandler._File(payload)

	if int(res['status']) > 399:
		raise HTTPException(status_code=int(res['status']), detail=res['message'])

	return JSONResponse(status_code=int(res['status']), content=res['message'])

	# "/Result", 
@router.post("/Result")
def update_shared_status(payload: dict = Body(...), core=Depends(get_core), base=Depends(get_base)):
	res = base.qhandler._Result(payload)

	if int(res['status']) > 399:
		raise HTTPException(status_code=int(res['status']), detail=res['message'])

	return JSONResponse(status_code=int(res['status']), content=res['message'])

	# "/Metric"
@router.post("/Metric")
def update_shared_status(payload: dict = Body(...), core=Depends(get_core), base=Depends(get_base)):
	res = base.qhandler._Metric(payload)

	if int(res['status']) > 399:
		raise HTTPException(status_code=int(res['status']), detail=res['message'])

	return JSONResponse(status_code=int(res['status']), content=res['message'])










# # 2. Use Depends(get_core) to inject it safely into your endpoints
# @router.get("/status")
# def get_shared_status(core=Depends(get_core), base=Depends(get_base)):
#     # Read directly from the shared dictionaries in your parent app
#     return {
#         "Agents": base.Agents,
#         "background_counter": base.run_name
#     }

# @router.post("/update-status")
# def update_shared_status(new_status: str, core=Depends(get_core), base=Depends(get_base)):
#     # Mutate the shared data across your whole application seamlessly
#     core.shared_data["system_status"] = new_status
#     return {"message": "Status updated successfully", "new_status": new_status}
