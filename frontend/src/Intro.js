import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Canvas } from "@react-three/fiber";
import Blob from "./Blob/blob";
import './Intro.css';

function Intro() {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles) => {
    setFile(acceptedFiles[0]);
    handleUpload(acceptedFiles[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsLoading(true);
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log('File uploaded successfully:', response);
      setIsLoading(false);

      navigate('/main', { 
        state: { 
          uploadResponse: {
            output: response.data.output
          }
        } 
      });
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="intro-container">
      {isLoading ? (
        <div className="blob__container">
          <Canvas camera={{ position: [0, 0, 5] }}>
            <Blob />
          </Canvas>
        </div>
      ):(
      <>
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the file here ...</p>
        ) : (
          <p>Drag and drop a file here, or click to select a file</p>
        )}
      </div>
      {file && <p>File selected: {file.name}</p>}
      </>
      )}
    </div>
  );
}

export default Intro;