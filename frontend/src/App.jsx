import React, { useState } from 'react';
import Header from './components/Header';
import Stepper from './components/Stepper';
import FileUpload from './components/FileUpload';
import TextReview from './components/TextReview';
import MetadataResults from './components/MetadataResults';

export default function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [jobs, setJobs] = useState([]);
  const [completedSteps, setCompletedSteps] = useState([]);

  const handleFilesProcessed = (jobsData) => {
    setJobs(jobsData);
    setCompletedSteps(prev => [...new Set([...prev, 0])]);
    setCurrentStep(1);
  };

  const handleTextReviewed = (updatedJobs) => {
    setJobs(updatedJobs);
    setCompletedSteps(prev => [...new Set([...prev, 1])]);
    setCurrentStep(2);
  };

  const handleBack = () => {
    setCurrentStep(prev => Math.max(0, prev - 1));
  };

  const handleStartOver = () => {
    setJobs([]);
    setCurrentStep(0);
    setCompletedSteps([]);
  };

  return (
    <>
      <Header />
      <main className="container">
        <Stepper currentStep={currentStep} completedSteps={completedSteps} />
        
        <div style={{ position: 'relative', overflow: 'hidden' }}>
          {currentStep === 0 && (
            <FileUpload onFilesProcessed={handleFilesProcessed} />
          )}
          
          {currentStep === 1 && (
            <TextReview 
              jobsData={jobs} 
              onBack={handleBack} 
              onContinue={handleTextReviewed} 
            />
          )}
          
          {currentStep === 2 && (
            <MetadataResults 
              jobsData={jobs}
              onBack={handleBack}
              onStartOver={handleStartOver}
            />
          )}
        </div>
      </main>
    </>
  );
}
