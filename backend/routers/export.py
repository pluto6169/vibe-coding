from fastapi import APIRouter, HTTPException, Response
from routers.upload import job_store

router = APIRouter()

@router.get("/{job_id}/dublin-core/xml")
def export_dc_xml(job_id: str):
    if job_id not in job_store or "dublin_core_xml" not in job_store[job_id]:
        raise HTTPException(status_code=404, detail="Data not found")
        
    xml_data = job_store[job_id]["dublin_core_xml"]
    return Response(content=xml_data, media_type="application/xml", headers={"Content-Disposition": f"attachment; filename=dc_{job_id}.xml"})

@router.get("/{job_id}/dublin-core/json")
def export_dc_json(job_id: str):
    if job_id not in job_store or "dublin_core" not in job_store[job_id]:
        raise HTTPException(status_code=404, detail="Data not found")
        
    return job_store[job_id]["dublin_core"]

@router.get("/{job_id}/marc21/mrk")
def export_marc21_mrk(job_id: str):
    if job_id not in job_store or "marc21" not in job_store[job_id]:
        raise HTTPException(status_code=404, detail="Data not found")
        
    mrk_data = job_store[job_id]["marc21"].mrk_text
    return Response(content=mrk_data, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename=marc_{job_id}.mrk"})

@router.get("/{job_id}/marc21/json")
def export_marc21_json(job_id: str):
    if job_id not in job_store or "marc21" not in job_store[job_id]:
        raise HTTPException(status_code=404, detail="Data not found")
        
    return job_store[job_id]["marc21"].fields
