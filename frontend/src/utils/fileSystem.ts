// File System Utility for saving project files locally
export interface ProjectFile {
  name: string;
  content: string | Blob;
  type: 'input' | 'output';
  originalName?: string;
  timestamp: Date;
}

export interface ProjectStructure {
  projectName: string;
  inputFiles: ProjectFile[];
  outputFiles: ProjectFile[];
  basePath: string;
}

export class FileSystemManager {
  private static instance: FileSystemManager;
  
  private constructor() {}
  
  static getInstance(): FileSystemManager {
    if (!FileSystemManager.instance) {
      FileSystemManager.instance = new FileSystemManager();
    }
    return FileSystemManager.instance;
  }

  /**
   * Save input files to project folder with timestamped names
   */
  async saveInputFiles(projectName: string, files: File[]): Promise<ProjectFile[]> {
    const timestamp = new Date();
    const timestampStr = this.formatTimestamp(timestamp);
    
    const savedFiles: ProjectFile[] = [];
    
    for (const file of files) {
      const timestampedName = this.generateTimestampedName(file.name, timestampStr);
      
      try {
        // Create a copy of the file with timestamped name
        const timestampedFile = new File([file], timestampedName, {
          type: file.type,
          lastModified: timestamp.getTime()
        });
        
        // Save to local system using File System Access API or download
        await this.saveFileToLocal(timestampedFile, projectName, 'input');
        
        savedFiles.push({
          name: timestampedName,
          content: file,
          type: 'input',
          originalName: file.name,
          timestamp
        });
        
        console.log(`Input file saved: ${timestampedName}`);
      } catch (error) {
        console.error(`Failed to save input file ${file.name}:`, error);
      }
    }
    
    return savedFiles;
  }

  /**
   * Save output files to project folder with timestamped names
   */
  async saveOutputFiles(projectName: string, files: { name: string; content: string | Blob; type: string }[]): Promise<ProjectFile[]> {
    const timestamp = new Date();
    const timestampStr = this.formatTimestamp(timestamp);
    
    const savedFiles: ProjectFile[] = [];
    
    for (const file of files) {
      const timestampedName = this.generateTimestampedName(file.name, timestampStr);
      
      try {
        // Create a blob with the content
        const blob = typeof file.content === 'string' 
          ? new Blob([file.content], { type: file.type || 'text/plain' })
          : file.content;
        
        // Create a file object
        const timestampedFile = new File([blob], timestampedName, {
          type: file.type || 'text/plain',
          lastModified: timestamp.getTime()
        });
        
        // Save to local system
        await this.saveFileToLocal(timestampedFile, projectName, 'output');
        
        savedFiles.push({
          name: timestampedName,
          content: file.content,
          type: 'output',
          originalName: file.name,
          timestamp
        });
        
        console.log(`Output file saved: ${timestampedName}`);
      } catch (error) {
        console.error(`Failed to save output file ${file.name}:`, error);
      }
    }
    
    return savedFiles;
  }

  /**
   * Generate timestamped filename
   */
  private generateTimestampedName(originalName: string, timestamp: string): string {
    const nameParts = originalName.split('.');
    const extension = nameParts.length > 1 ? nameParts.pop() : '';
    const baseName = nameParts.join('.');
    
    if (extension) {
      return `${baseName}_${timestamp}.${extension}`;
    }
    return `${baseName}_${timestamp}`;
  }

  /**
   * Format timestamp for filename
   */
  private formatTimestamp(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;
  }

  /**
   * Save file to local system using File System Access API or download
   */
  private async saveFileToLocal(file: File, projectName: string, folderType: 'input' | 'output'): Promise<void> {
    try {
      // Try to use File System Access API (modern browsers)
      if ('showSaveFilePicker' in window) {
        await this.saveWithFileSystemAPI(file, projectName, folderType);
      } else {
        // Fallback to download
        await this.saveWithDownload(file, projectName, folderType);
      }
    } catch (error) {
      // If File System Access API fails, fallback to download
      console.warn('File System Access API failed, falling back to download:', error);
      await this.saveWithDownload(file, projectName, folderType);
    }
  }

  /**
   * Save using File System Access API
   */
  private async saveWithFileSystemAPI(file: File, projectName: string, folderType: 'input' | 'output'): Promise<void> {
    try {
      // Request permission to access files
      const handle = await (window as any).showDirectoryPicker({
        mode: 'readwrite',
        startIn: 'documents'
      });
      
      // Create project folder structure
      const projectFolder = await this.ensureProjectFolder(handle, projectName);
      const targetFolder = await this.ensureFolder(projectFolder, folderType === 'input' ? 'Input Files' : 'Output Files');
      
      // Create file in the folder
      const fileHandle = await targetFolder.getFileHandle(file.name, { create: true });
      const writable = await fileHandle.createWritable();
      await writable.write(file);
      await writable.close();
      
      console.log(`File saved using File System Access API: ${file.name}`);
    } catch (error) {
      throw new Error(`File System Access API failed: ${error}`);
    }
  }

  /**
   * Save using download (fallback method)
   */
  private async saveWithDownload(file: File, projectName: string, folderType: 'input' | 'output'): Promise<void> {
    // Create download link
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    link.download = file.name;
    
    // Add to DOM, click, and cleanup
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log(`File downloaded: ${file.name}`);
  }

  /**
   * Ensure project folder exists
   */
  private async ensureProjectFolder(rootHandle: any, projectName: string): Promise<any> {
    try {
      return await rootHandle.getDirectoryHandle(projectName, { create: true });
    } catch (error) {
      throw new Error(`Failed to create project folder: ${error}`);
    }
  }

  /**
   * Ensure subfolder exists
   */
  private async ensureFolder(parentHandle: any, folderName: string): Promise<any> {
    try {
      return await parentHandle.getDirectoryHandle(folderName, { create: true });
    } catch (error) {
      throw new Error(`Failed to create folder ${folderName}: ${error}`);
    }
  }

  /**
   * Get project file structure
   */
  async getProjectStructure(projectName: string): Promise<ProjectStructure> {
    return {
      projectName,
      inputFiles: [],
      outputFiles: [],
      basePath: `/${projectName}`
    };
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    // Clean up any temporary resources
  }
}

// Export singleton instance
export const fileSystemManager = FileSystemManager.getInstance();
