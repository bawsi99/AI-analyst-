        return UploadResponse(
            message="File uploaded successfully",
            session_id=session_id,
            filename=file.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        ) 