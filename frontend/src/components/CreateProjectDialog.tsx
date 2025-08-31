import React, { useState } from 'react';
import { X, Folder, Plus } from 'lucide-react';

interface CreateProjectDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateProject: (projectName: string, description: string) => void;
}

const CreateProjectDialog: React.FC<CreateProjectDialogProps> = ({
  isOpen,
  onClose,
  onCreateProject
}) => {
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [errors, setErrors] = useState<string[]>([]);
  const [isCreating, setIsCreating] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const newErrors: string[] = [];
    if (!projectName.trim()) {
      newErrors.push('Project name is required');
    }
    if (projectName.trim().length < 3) {
      newErrors.push('Project name must be at least 3 characters');
    }
    if (projectName.trim().length > 50) {
      newErrors.push('Project name must be less than 50 characters');
    }
    
    setErrors(newErrors);
    
    if (newErrors.length === 0) {
      setIsCreating(true);
      try {
        await onCreateProject(projectName.trim(), description.trim());
        handleClose();
      } catch (error) {
        setErrors(['Failed to create project. Please try again.']);
      } finally {
        setIsCreating(false);
      }
    }
  };

  const handleClose = () => {
    setProjectName('');
    setDescription('');
    setErrors([]);
    setIsCreating(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Folder className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Create New Project</h2>
              <p className="text-sm text-gray-600">Set up a new project for your workflows and files</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Project Name */}
          <div>
            <label htmlFor="projectName" className="block text-sm font-medium text-gray-700 mb-2">
              Project Name *
            </label>
            <input
              type="text"
              id="projectName"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Enter project name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              disabled={isCreating}
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional project description..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
              disabled={isCreating}
            />
          </div>

          {/* Error Messages */}
          {errors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              {errors.map((error, index) => (
                <p key={index} className="text-sm text-red-600">
                  {error}
                </p>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              disabled={isCreating}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isCreating || !projectName.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {isCreating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating...</span>
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Create Project</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProjectDialog;
