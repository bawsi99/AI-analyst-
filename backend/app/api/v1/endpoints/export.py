from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from services.data_service import data_service
from services.summary_service import summary_service
from ml.pipeline import ml_pipeline
import os
import json
import zipfile
import io
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.get("/report/{session_id}")
async def export_report(
    session_id: str,
    model_id: Optional[str] = Query(None, description="Optional model ID to include model insights")
):
    """
    Export a comprehensive analysis report as a JSON file.
    
    - **session_id**: Session ID from upload endpoint
    - **model_id**: Optional model ID from training endpoint
    - Returns a JSON file with complete analysis report
    """
    try:
        # Check if session exists
        session_info = data_service.get_session_info(session_id)
        
        # Get profile data
        profile_data = data_service.profile_data(session_id)
        
        # Get summary data
        summary_data = summary_service.generate_complete_summary(session_id, model_id)
        
        # Prepare report data
        report_data = {
            "export_info": {
                "exported_at": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "model_id": model_id,
                "filename": session_info['filename']
            },
            "data_profile": {
                "metadata": profile_data['metadata'],
                "schema": profile_data['schema'],
                "statistics": profile_data['statistics'],
                "insights": profile_data['insights']
            },
            "summary": {
                "data_summary": summary_data['data_summary'],
                "model_summary": summary_data['model_summary'],
                "key_insights": summary_data['key_insights'],
                "recommendations": summary_data['recommendations']
            }
        }
        
        # Add model information if available
        if model_id:
            try:
                model_info = ml_pipeline.get_model_info(model_id)
                report_data["model_info"] = {
                    "model_id": model_id,
                    "model_type": model_info['model_type'],
                    "target_column": model_info['target_column'],
                    "algorithm": model_info['algorithm'],
                    "metrics": model_info['metrics'],
                    "feature_importance": model_info['feature_importance'],
                    "training_time": model_info['training_time'],
                    "created_at": model_info['created_at'].isoformat()
                }
            except Exception as e:
                report_data["model_info"] = {"error": f"Could not retrieve model info: {str(e)}"}
        
        # Convert to JSON string
        json_content = json.dumps(report_data, indent=2, default=str)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_report_{session_id}_{timestamp}.json"
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(json_content.encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting report: {str(e)}"
        )

@router.get("/model/{model_id}")
async def download_model(model_id: str):
    """
    Download a trained model as a joblib file.
    
    - **model_id**: Model ID from training endpoint
    - Returns the trained model file for local use
    """
    try:
        # Check if model exists
        model_info = ml_pipeline.get_model_info(model_id)
        model_path = model_info['model_path']
        
        # Check if file exists
        if not os.path.exists(model_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model file not found"
            )
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"model_{model_id}_{timestamp}.joblib"
        
        # Return the model file
        return FileResponse(
            path=model_path,
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading model: {str(e)}"
        )

@router.get("/share/{session_id}")
async def share_results(
    session_id: str,
    model_id: Optional[str] = Query(None, description="Optional model ID to include model results")
):
    """
    Generate a shareable results package with all analysis data.
    
    - **session_id**: Session ID from upload endpoint
    - **model_id**: Optional model ID from training endpoint
    - Returns a ZIP file with all analysis results
    """
    try:
        # Check if session exists
        session_info = data_service.get_session_info(session_id)
        
        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add report JSON
            profile_data = data_service.profile_data(session_id)
            summary_data = summary_service.generate_complete_summary(session_id, model_id)
            
            report_data = {
                "export_info": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "session_id": session_id,
                    "model_id": model_id,
                    "filename": session_info['filename']
                },
                "data_profile": profile_data,
                "summary": summary_data
            }
            
            if model_id:
                try:
                    model_info = ml_pipeline.get_model_info(model_id)
                    report_data["model_info"] = {
                        "model_id": model_id,
                        "model_type": model_info['model_type'],
                        "target_column": model_info['target_column'],
                        "algorithm": model_info['algorithm'],
                        "metrics": model_info['metrics'],
                        "feature_importance": model_info['feature_importance'],
                        "training_time": model_info['training_time'],
                        "created_at": model_info['created_at'].isoformat()
                    }
                except Exception as e:
                    report_data["model_info"] = {"error": f"Could not retrieve model info: {str(e)}"}
            
            # Add report to ZIP
            zip_file.writestr("analysis_report.json", json.dumps(report_data, indent=2, default=str))
            
            # Add original data file if it exists
            if os.path.exists(session_info['file_path']):
                zip_file.write(session_info['file_path'], "original_data.csv")
            
            # Add model file if available
            if model_id:
                try:
                    model_info = ml_pipeline.get_model_info(model_id)
                    model_path = model_info['model_path']
                    if os.path.exists(model_path):
                        zip_file.write(model_path, f"model_{model_id}.joblib")
                except Exception:
                    pass  # Skip if model file can't be added
            
            # Add README file
            readme_content = f"""# Analysis Results Package

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Session ID: {session_id}
Model ID: {model_id or 'N/A'}

## Contents:
- analysis_report.json: Complete analysis report with insights
- original_data.csv: Original uploaded dataset
- model_{model_id}.joblib: Trained model file (if available)

## How to use:
1. Open analysis_report.json to view the complete analysis
2. Use the model file with scikit-learn for predictions
3. Original data is included for reference

Generated by Mini AI Analyst API
"""
            zip_file.writestr("README.md", readme_content)
        
        # Reset buffer position
        zip_buffer.seek(0)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_results_{session_id}_{timestamp}.zip"
        
        # Return the ZIP file
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sharing results: {str(e)}"
        ) 