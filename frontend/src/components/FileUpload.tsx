import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadFile } from '../services/api.ts';

interface FileUploadProps {
  onUploadSuccess: (sessionId: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      toast.error('Please upload a CSV file');
      return;
    }

    // Validate file size (50MB limit)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await uploadFile(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setTimeout(() => {
        onUploadSuccess(response.session_id);
      }, 500);

    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Upload failed');
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/csv': ['.csv'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Upload Your CSV File
        </h3>
        <p className="text-gray-600">
          Upload a CSV file to begin your AI-powered data analysis
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive && !isDragReject
            ? 'border-primary-500 bg-primary-50'
            : isDragReject
            ? 'border-red-500 bg-red-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
          ${isUploading ? 'pointer-events-none opacity-75' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          {isUploading ? (
            <>
              <div className="flex justify-center">
                <div className="loading-spinner"></div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Uploading...</p>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">{uploadProgress}%</p>
              </div>
            </>
          ) : (
            <>
              <div className="flex justify-center">
                {isDragReject ? (
                  <AlertCircle className="h-12 w-12 text-red-500" />
                ) : (
                  <Upload className="h-12 w-12 text-gray-400" />
                )}
              </div>
              
              <div>
                {isDragReject ? (
                  <p className="text-sm text-red-600">Invalid file type. Please upload a CSV file.</p>
                ) : isDragActive ? (
                  <p className="text-sm text-primary-600">Drop your CSV file here</p>
                ) : (
                  <>
                    <p className="text-sm font-medium text-gray-900">
                      Drag and drop your CSV file here
                    </p>
                    <p className="text-sm text-gray-500">or click to browse</p>
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* File Requirements */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">File Requirements:</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li className="flex items-center">
            <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
            CSV format only
          </li>
          <li className="flex items-center">
            <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
            Maximum file size: 50MB
          </li>
          <li className="flex items-center">
            <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
            First row should contain column headers
          </li>
          <li className="flex items-center">
            <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
            UTF-8 encoding recommended
          </li>
        </ul>
      </div>

      {/* Sample Data Info */}
      <div className="bg-blue-50 rounded-lg p-4">
        <div className="flex items-start">
          <FileText className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-900">Need sample data?</h4>
            <p className="text-sm text-blue-700 mt-1">
              You can use any CSV file with numerical and categorical columns. 
              For best results, include a target column for prediction.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload; 