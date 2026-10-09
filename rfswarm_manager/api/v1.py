# routers/users.py
from fastapi import APIRouter, Request, Depends

router = APIRouter(prefix="/api/v1", tags=["v1"])

# 1. This helper function extracts your core reference from the app state
def get_core(request: Request):
    return request.app.state.core

def get_base(request: Request):
    return request.app.state.base

# 2. Use Depends(get_core) to inject it safely into your endpoints
@router.get("/status")
def get_shared_status(core=Depends(get_core), base=Depends(get_base)):
    # Read directly from the shared dictionaries in your parent app
    return {
        "system_status": core.shared_data["system_status"],
        "background_counter": core.shared_data["counter"]
    }

@router.post("/update-status")
def update_shared_status(new_status: str, core=Depends(get_core), base=Depends(get_base)):
    # Mutate the shared data across your whole application seamlessly
    core.shared_data["system_status"] = new_status
    return {"message": "Status updated successfully", "new_status": new_status}
