import React from 'react';
import { Card, CardContent } from './ui/card';
import { FileText, Upload, File, Trash2 } from 'lucide-react';

interface FileData {
  name: string;
  type: string;
  size: number;
  columns: string[];
  path: string;
  lastModified: Date;
  sheets?: { [sheetName: string]: string[] };
  headerConfig?: {
    row: number;
    merged: boolean;
    customHeaders?: string[];
    autoDetected: boolean;
  };
  currentSheet?: string;
}

interface DataSourcesProps {
  importedFiles: FileData[];
  onBrowseFiles: () => void;
  onDragDropImport: (files: FileList) => void;
  onDeleteFile?: (fileName: string) => void;
  height: number;
  showDeleteButton?: boolean;
  showHeaderConfig?: boolean;
  className?: string;
}

const DataSources: React.FC<DataSourcesProps> = ({
  importedFiles,
  onBrowseFiles,
  onDragDropImport,
  onDeleteFile,
  height,
  showDeleteButton = false,
  showHeaderConfig = false,
  className = ""
}) => {
  const triggerBrowse = () => {
    // Only call the parent's browse function, don't create our own file input
    if (onBrowseFiles) {
      onBrowseFiles();
    }
  };

  return (
    <Card className={`h-full ${className}`}>
      <CardContent className="p-4 h-full flex flex-col">
        <div className="flex items-center justify-between mb-4 flex-shrink-0">
          <h3 className="font-semibold flex items-center">
            <FileText className="w-4 h-4 mr-2" />
            Data Sources
            {importedFiles.length > 0 && (
              <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                {importedFiles.length} file{importedFiles.length !== 1 ? 's' : ''} loaded
              </span>
            )}
          </h3>
          <button
            onClick={triggerBrowse}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Import Files"
          >
            <Upload className="w-4 h-4" />
          </button>
        </div>
        
        {/* File Import Area - Only show when no files are imported */}
        {importedFiles.length === 0 ? (
          <div 
            className="text-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 flex flex-col justify-center flex-1 data-source-drop-area"
            onDragOver={(e) => {
              e.preventDefault();
              e.currentTarget.classList.add('border-blue-400', 'bg-blue-50');
            }}
            onDragLeave={(e) => {
              e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
              if (e.dataTransfer.files.length > 0) {
                onDragDropImport(e.dataTransfer.files);
              }
            }}
          >
            <div>
              <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h4 className="text-lg font-semibold mb-2">Drop Files Here</h4>
              <p className="text-sm text-gray-500 mb-4">Support for CSV, Excel files</p>
              <p className="text-xs text-blue-600 mb-4">💡 Tip: Drag & drop files here or use the upload button above!</p>
              <button 
                onClick={triggerBrowse}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Browse Files
              </button>
            </div>
          </div>
        ) : (
          /* Scrollable content area - Only when files are imported */
          <div 
            className="overflow-y-auto data-sources-scrollbar flex-1" 
            style={{ 
              maxHeight: `${height - 120}px` // Subtract header height + padding
            }}
          >
            <div className="space-y-2">
              {/* File count indicator */}
              <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded text-center">
                {importedFiles.length} file{importedFiles.length !== 1 ? 's' : ''} loaded
                {importedFiles.length > 3 && (
                  <span className="block text-blue-600 mt-1">Scroll to see all files</span>
                )}
              </div>
              
              {/* File list with strict height constraint */}
              <div className="space-y-2">
                {importedFiles.map((file, index) => (
                  <div key={file.name} className="border rounded-lg p-3 bg-white">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0 mr-3">
                        <div className="flex items-center space-x-2 mb-2">
                          <File className="w-4 h-4 text-gray-500 flex-shrink-0" />
                          <span className="text-sm font-medium text-gray-900 break-words leading-tight">
                            {file.name}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500 break-words">
                          {file.type} • {Math.round(file.size / 1024)} KB
                        </div>
                        <div className="text-xs text-gray-600 break-words">
                          {file.columns.length} column{file.columns.length !== 1 ? 's' : ''}
                        </div>
                        {/* Header Configuration Status - Only show if enabled */}
                        {showHeaderConfig && file.headerConfig && (
                          <div className="text-xs text-green-600 mt-1 break-words">
                            {file.headerConfig.autoDetected ? 'Auto-detected headers' : 'Custom headers configured'}
                            {file.headerConfig.merged && ' • Merged headers'}
                          </div>
                        )}
                        {/* Sheets info if available */}
                        {file.sheets && Object.keys(file.sheets).length > 0 && (
                          <div className="text-xs text-blue-600 break-words">
                            {Object.keys(file.sheets).length} sheet{Object.keys(file.sheets).length !== 1 ? 's' : ''} available
                          </div>
                        )}
                      </div>
                      {showDeleteButton && onDeleteFile && (
                        <div className="flex items-center space-x-1">
                          {/* Delete Button */}
                          <button
                            onClick={() => onDeleteFile(file.name)}
                            className="text-red-500 hover:text-red-700 transition-colors p-1 hover:bg-red-50 rounded-md"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DataSources;
