from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional
import os
import json
import zipfile
import tempfile
from datetime import datetime
from app.core.auth import get_current_user
from app.services.database_service import database_service
from app.services.data_service import data_service
from app.services.summary_service import summary_service
from app.services.ai_analysis_service import ai_analysis_service
from app.ml.pipeline import ml_pipeline
from app.core.config import settings

router = APIRouter()

@router.get("/report/{session_id}")
async def export_report(
    session_id: str,
    model_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export a comprehensive analysis report as JSON.
    
    Args:
    - session_id: The session ID to export
    - model_id: Optional model ID to include model-specific data
    
    Returns:
    - JSON file containing complete analysis report
    """
    try:
        # Verify session belongs to user
        session = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get data profile
        profile_data = data_service.profile_data(session_id)
        
        # Get summary
        summary_data = summary_service.generate_complete_summary(session_id, model_id)
        
        # Get AI analysis if available
        ai_analysis_data = ai_analysis_service.generate_ai_analysis(session_id, model_id)
        
        # Get model info if model_id provided
        model_info = None
        if model_id:
            model_info = await database_service.get_model_by_id(model_id, current_user["id"])
        
        # Prepare report data
        report_data = {
            "export_info": {
                "exported_at": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "model_id": model_id,
                "user_id": current_user["id"]
            },
            "session_info": {
                "file_name": session.get("file_name"),
                "file_size": session.get("file_size"),
                "status": session.get("status"),
                "created_at": session.get("created_at")
            },
            "data_profile": {
                "schema": [schema.dict() for schema in profile_data["schema"]],  # Convert to dict for JSON serialization
                "statistics": profile_data["statistics"].dict(),  # Convert to dict for JSON serialization
                "insights": profile_data["insights"].dict()  # Convert to dict for JSON serialization
            },
            "summary": summary_data,
            "ai_analysis": ai_analysis_data,
            "model_info": model_info
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report_data, f, indent=2, default=str)
            temp_file_path = f.name
        
        # Return file response
        return FileResponse(
            path=temp_file_path,
            filename=f"analysis_report_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=analysis_report_{session_id}.json"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")

@router.get("/model/{model_id}")
async def download_model(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download a trained model file.
    
    Args:
    - model_id: The model ID to download
    
    Returns:
    - Model file (.joblib format)
    """
    try:
        # Verify model belongs to user
        model = await database_service.get_model_by_id(model_id, current_user["id"])
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get model file path
        model_path = model.get("model_path")
        if not model_path:
            raise HTTPException(status_code=404, detail="Model file not found")
        
        # Construct full path
        full_model_path = os.path.join(settings.MODEL_STORAGE_PATH, f"{model_id}.joblib")
        
        # Check if file exists
        if not os.path.exists(full_model_path):
            raise HTTPException(status_code=404, detail="Model file not found on disk")
        
        # Return file response
        return FileResponse(
            path=full_model_path,
            filename=f"model_{model_id}.joblib",
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=model_{model_id}.joblib"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download model: {str(e)}")

@router.get("/share/{session_id}")
async def share_results(
    session_id: str,
    model_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Share analysis results as a ZIP file containing all relevant data.
    
    Args:
    - session_id: The session ID to share
    - model_id: Optional model ID to include model-specific data
    
    Returns:
    - ZIP file containing all analysis results
    """
    try:
        # Verify session belongs to user
        session = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create temporary directory for ZIP
        with tempfile.TemporaryDirectory() as temp_dir:
            # Get all analysis data
            profile_data = data_service.profile_data(session_id)
            summary_data = summary_service.generate_complete_summary(session_id, model_id)
            ai_analysis_data = ai_analysis_service.generate_ai_analysis(session_id, model_id)
            
            # Get model info if model_id provided
            model_info = None
            if model_id:
                model_info = await database_service.get_model_by_id(model_id, current_user["id"])
            
            # Create report JSON
            report_data = {
                "export_info": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "session_id": session_id,
                    "model_id": model_id,
                    "user_id": current_user["id"]
                },
                "session_info": {
                    "file_name": session.get("file_name"),
                    "file_size": session.get("file_size"),
                    "status": session.get("status"),
                    "created_at": session.get("created_at")
                },
                "data_profile": {
                    "schema": [schema.dict() for schema in profile_data["schema"]],  # Convert to dict for JSON serialization
                    "statistics": profile_data["statistics"].dict(),  # Convert to dict for JSON serialization
                    "insights": profile_data["insights"].dict(),  # Convert to dict for JSON serialization
                    "metadata": profile_data["metadata"]
                },
                "summary": summary_data,
                "ai_analysis": ai_analysis_data,
                "model_info": model_info
            }
            
            # Write report to file
            report_file = os.path.join(temp_dir, "analysis_report.json")
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            # Add original data file if it exists
            original_file_path = session.get("file_path")
            if original_file_path and os.path.exists(original_file_path):
                import shutil
                shutil.copy2(original_file_path, os.path.join(temp_dir, session.get("file_name")))
            
            # Add model file if model_id provided
            if model_id and model_info:
                model_file_path = os.path.join(settings.MODEL_STORAGE_PATH, f"{model_id}.joblib")
                if os.path.exists(model_file_path):
                    import shutil
                    shutil.copy2(model_file_path, os.path.join(temp_dir, f"model_{model_id}.joblib"))
            
            # Create ZIP file
            zip_file_path = os.path.join(temp_dir, f"analysis_results_{session_id}.zip")
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != f"analysis_results_{session_id}.zip":  # Don't include the ZIP itself
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            # Return ZIP file
            return FileResponse(
                path=zip_file_path,
                filename=f"analysis_results_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename=analysis_results_{session_id}.zip"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to share results: {str(e)}")
