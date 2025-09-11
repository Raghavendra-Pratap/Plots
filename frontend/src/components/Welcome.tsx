import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  BarChart3, 
  Workflow, 
  Play, 
  ArrowRight, 
  Sparkles,
  Zap,
  Shield,
  Users,
  FileText,
  Settings,
  HelpCircle
} from 'lucide-react';

interface WelcomeStep {
  id: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  features: string[];
  action?: {
    text: string;
    route: string;
    icon: React.ReactNode;
  };
}

const Welcome: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  const steps: WelcomeStep[] = [
    {
      id: 1,
      title: "Welcome to Unified Data Studio v2",
      description: "Your powerful desktop application for data processing, analysis, and workflow automation.",
      icon: <Sparkles className="w-12 h-12 text-blue-500" />,
      features: [
        "Advanced data processing with Enhanced SQLite",
        "Intuitive workflow builder",
        "Real-time data preview and validation",
        "Cross-platform desktop application"
      ],
      action: {
        text: "Get Started",
        route: "/dashboard",
        icon: <ArrowRight className="w-4 h-4" />
      }
    },
    {
      id: 2,
      title: "Data Sources & Import",
      description: "Easily import and manage your data from various sources with automatic format detection.",
      icon: <Database className="w-12 h-12 text-green-500" />,
      features: [
        "CSV, Excel, and JSON file support",
        "Drag & drop file import",
        "Automatic header detection",
        "File management and organization"
      ]
    },
    {
      id: 3,
      title: "Workflow Builder",
      description: "Create powerful data processing workflows with our intuitive drag-and-drop interface.",
      icon: <Workflow className="w-12 h-12 text-purple-500" />,
      features: [
        "Visual workflow builder",
        "Pre-built formula library",
        "Real-time workflow validation",
        "Save and share workflows"
      ]
    },
    {
      id: 4,
      title: "Enhanced SQLite Processing",
      description: "High-performance data processing with our enhanced SQLite engine for complex operations.",
      icon: <Zap className="w-12 h-12 text-yellow-500" />,
      features: [
        "Advanced filtering and sorting",
        "Data aggregation and grouping",
        "Join operations across datasets",
        "Pivot table generation"
      ]
    },
    {
      id: 5,
      title: "Live Preview & Validation",
      description: "See your data transformations in real-time with comprehensive validation and error handling.",
      icon: <BarChart3 className="w-12 h-12 text-indigo-500" />,
      features: [
        "Real-time data preview",
        "Data quality indicators",
        "Error detection and suggestions",
        "Performance optimization"
      ]
    },
    {
      id: 6,
      title: "Ready to Start",
      description: "You're all set! Start exploring Unified Data Studio v2 and transform your data workflows.",
      icon: <Play className="w-12 h-12 text-red-500" />,
      features: [
        "Access to all features unlocked",
        "Comprehensive documentation",
        "Community support available",
        "Regular updates and improvements"
      ],
      action: {
        text: "Launch Application",
        route: "/playground",
        icon: <ArrowRight className="w-4 h-4" />
      }
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    setIsVisible(false);
    navigate('/dashboard');
  };

  const handleAction = (route: string) => {
    setIsVisible(false);
    navigate(route);
  };

  if (!isVisible) {
    return null;
  }

  const currentStepData = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Database className="w-8 h-8" />
              <h1 className="text-2xl font-bold">Unified Data Studio v2</h1>
            </div>
            <button
              onClick={handleSkip}
              className="text-white/80 hover:text-white transition-colors"
            >
              Skip Tour
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="bg-gray-100 h-1">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Content */}
        <div className="p-8">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              {currentStepData.icon}
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {currentStepData.title}
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              {currentStepData.description}
            </p>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {currentStepData.features.map((feature, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                <span className="text-gray-700">{feature}</span>
              </div>
            ))}
          </div>

          {/* Action Button */}
          {currentStepData.action && (
            <div className="text-center mb-6">
              <button
                onClick={() => handleAction(currentStepData.action!.route)}
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <span>{currentStepData.action!.text}</span>
                {currentStepData.action!.icon}
              </button>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                currentStep === 0
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <ArrowRight className="w-4 h-4 rotate-180" />
              <span>Previous</span>
            </button>

            <div className="flex space-x-2">
              {steps.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentStep(index)}
                  className={`w-3 h-3 rounded-full transition-colors ${
                    index === currentStep
                      ? 'bg-blue-500'
                      : 'bg-gray-300 hover:bg-gray-400'
                  }`}
                />
              ))}
            </div>

            <button
              onClick={handleNext}
              disabled={currentStep === steps.length - 1}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                currentStep === steps.length - 1
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <span>Next</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 p-4 border-t">
          <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4" />
              <span>Secure & Private</span>
            </div>
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4" />
              <span>Community Driven</span>
            </div>
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Open Source</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
