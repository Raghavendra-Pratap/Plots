import { WorkflowTemplate } from '../components/SaveWorkflowDialog';

// Database interfaces
export interface DatabaseProject {
  id: string;
  name: string;
  description: string;
  created: Date;
  lastModified: Date;
  status: 'in_progress' | 'completed' | 'idle';
  storagePath: string;
  workflows?: ProjectWorkflow[];
  inputFiles?: DatabaseFile[];
  outputFiles?: DatabaseFile[];
}

export interface ProjectWorkflow {
  id: string;
  name: string;
  description: string;
  steps: any[];
  status: 'draft' | 'ready' | 'running' | 'completed' | 'error';
  lastExecuted?: Date;
}

export interface DatabaseWorkflow {
  id: string;
  name: string;
  description: string;
  project: string;
  version: string;
  workflowSteps: any[];
  filePatterns: any[];
  columnSettings: any;
  createdAt: Date;
  updatedAt: Date;
  isTemporary: boolean;
  // Additional properties for compatibility
  steps: any[];
  created: Date;
  lastModified: Date;
}

export interface DatabaseFile {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: Date;
  status: 'pending' | 'processing' | 'completed' | 'error';
}

// SQLite Database Manager
class DatabaseManager {
  private db: any = null;
  private isInitialized = false;

  constructor() {
    // Don't initialize immediately - wait for app to be ready
    console.log('DatabaseManager: Constructor called, will initialize when needed');
  }

  public async initializeDatabase() {
    if (this.isInitialized) {
      console.log('Database already initialized');
      return;
    }

    try {
      console.log('DatabaseManager: Starting initialization...');
      
      // Try IndexedDB first
      if ('indexedDB' in window) {
        try {
          console.log('DatabaseManager: Attempting IndexedDB initialization...');
          await this.initializeIndexedDB();
          this.isInitialized = true;
          console.log('✅ Database initialized successfully with IndexedDB');
          return;
        } catch (indexedDBError) {
          console.warn('⚠️ IndexedDB failed, falling back to localStorage:', indexedDBError);
          // Continue to localStorage fallback
        }
      } else {
        console.warn('⚠️ IndexedDB not supported, using localStorage fallback');
      }
      
      // Fallback to localStorage
      console.log('DatabaseManager: Using localStorage fallback');
      this.isInitialized = true;
      console.log('✅ Database initialized successfully with localStorage fallback');
      
    } catch (error) {
      console.error('❌ Database initialization failed completely:', error);
      // Last resort: force localStorage mode
      this.isInitialized = true;
      console.log('🔄 Forcing localStorage mode as last resort');
    }
  }

  private async initializeIndexedDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('UnifiedDataStudio', 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as any).result;
        
        // Create projects store
        if (!db.objectStoreNames.contains('projects')) {
          const projectStore = db.createObjectStore('projects', { keyPath: 'id' });
          projectStore.createIndex('name', 'name', { unique: true });
        }
        
        // Create workflows store
        if (!db.objectStoreNames.contains('workflows')) {
          const workflowStore = db.createObjectStore('workflows', { keyPath: 'id' });
          workflowStore.createIndex('project', 'project', { unique: false });
          workflowStore.createIndex('name', 'name', { unique: false });
        }
        
        // Create files store
        if (!db.objectStoreNames.contains('files')) {
          const fileStore = db.createObjectStore('files', { keyPath: 'id' });
          fileStore.createIndex('project', 'project', { unique: false });
        }
      };
    });
  }

  private async ensureInitialized(): Promise<boolean> {
    if (!this.isInitialized) {
      console.log('DatabaseManager: Not initialized, calling initializeDatabase...');
      await this.initializeDatabase();
    }
    return this.isInitialized;
  }

  // Project operations
  async createProject(project: DatabaseProject): Promise<void> {
    console.log('createProject called with:', project);
    console.log('Database initialized:', this.isInitialized);
    
    if (!(await this.ensureInitialized())) {
      console.log('Falling back to localStorage for project creation');
      // Fallback to localStorage
      const storedProjects = JSON.parse(localStorage.getItem('projectData') || '{}');
      storedProjects[project.name] = project;
      localStorage.setItem('projectData', JSON.stringify(storedProjects));
      
      const projectNames = JSON.parse(localStorage.getItem('projects') || '[]');
      if (!projectNames.includes(project.name)) {
        projectNames.push(project.name);
        localStorage.setItem('projects', JSON.stringify(projectNames));
      }
      console.log('Project stored in localStorage:', project.name);
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['projects'], 'readwrite');
      const store = transaction.objectStore('projects');
      const request = store.add(project);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getProjects(): Promise<DatabaseProject[]> {
    console.log('getProjects called');
    console.log('Database initialized:', this.isInitialized);
    
    if (!(await this.ensureInitialized())) {
      console.log('Falling back to localStorage for getProjects');
      // Fallback to localStorage
      const storedProjects = JSON.parse(localStorage.getItem('projectData') || '{}');
      console.log('Stored projects from localStorage:', storedProjects);
      const projects = Object.values(storedProjects).map((project: any) => ({
        ...project,
        created: new Date(project.created),
        lastModified: new Date(project.lastModified)
      }));
      console.log('Processed projects from localStorage:', projects);
      return projects;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['projects'], 'readonly');
      const store = transaction.objectStore('projects');
      const request = store.getAll();
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async updateProject(project: DatabaseProject): Promise<void> {
    if (!(await this.ensureInitialized())) {
      // Fallback to localStorage
      const storedProjects = JSON.parse(localStorage.getItem('projectData') || '{}');
      storedProjects[project.name] = project;
      localStorage.setItem('projectData', JSON.stringify(storedProjects));
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['projects'], 'readwrite');
      const store = transaction.objectStore('projects');
      const request = store.put(project);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async deleteProject(projectName: string): Promise<void> {
    if (!(await this.ensureInitialized())) {
      // Fallback to localStorage
      const storedProjects = JSON.parse(localStorage.getItem('projectData') || '{}');
      delete storedProjects[projectName];
      localStorage.setItem('projectData', JSON.stringify(storedProjects));
      
      const projectNames = JSON.parse(localStorage.getItem('projects') || '[]');
      const updatedNames = projectNames.filter((name: string) => name !== projectName);
      localStorage.setItem('projects', JSON.stringify(updatedNames));
      
      // Also remove workflows
      const workflows = JSON.parse(localStorage.getItem('workflowTemplates') || '[]');
      const filteredWorkflows = workflows.filter((w: WorkflowTemplate) => w.project !== projectName);
      localStorage.setItem('workflowTemplates', JSON.stringify(filteredWorkflows));
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['projects', 'workflows'], 'readwrite');
      const projectStore = transaction.objectStore('projects');
      const workflowStore = transaction.objectStore('workflows');
      
      // Delete project
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const projectRequest = projectStore.delete(projectName);
      
      // Delete associated workflows
      const workflowIndex = workflowStore.index('project');
      const workflowRequest = workflowIndex.openCursor(IDBKeyRange.only(projectName));
      
      workflowRequest.onsuccess = (event: any) => {
        const cursor = (event.target as any).result;
        if (cursor) {
          cursor.delete();
          cursor.continue();
        }
      };
      
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  // Workflow operations
  async createWorkflow(workflow: DatabaseWorkflow): Promise<void> {
    if (!(await this.ensureInitialized())) {
      // Fallback to localStorage
      const workflows = JSON.parse(localStorage.getItem('workflowTemplates') || '[]');
      const template: WorkflowTemplate = {
        id: workflow.id,
        name: workflow.name,
        description: workflow.description,
        project: workflow.project,
        version: workflow.version,
        compatibility: { minVersion: '1.0.0', maxVersion: '2.0.0' },
        filePatterns: workflow.filePatterns,
        workflowSteps: workflow.workflowSteps,
        createdAt: workflow.createdAt,
        updatedAt: workflow.updatedAt,
        isTemporary: workflow.isTemporary,
        columnSettings: workflow.columnSettings
      };
      workflows.push(template);
      localStorage.setItem('workflowTemplates', JSON.stringify(workflows));
      
      // Update project data
      const projectData = JSON.parse(localStorage.getItem('projectData') || '{}');
      if (projectData[workflow.project]) {
        projectData[workflow.project].workflows.push({
          id: workflow.id,
          name: workflow.name,
          description: workflow.description,
          steps: workflow.workflowSteps,
          status: 'ready',
          lastExecuted: null
        });
        projectData[workflow.project].lastModified = new Date();
        localStorage.setItem('projectData', JSON.stringify(projectData));
      }
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['workflows'], 'readwrite');
      const store = transaction.objectStore('workflows');
      const request = store.add(workflow);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getWorkflows(): Promise<DatabaseWorkflow[]> {
    if (!(await this.ensureInitialized())) {
      // Fallback to localStorage
      const templates = JSON.parse(localStorage.getItem('workflowTemplates') || '[]');
      return templates.map((template: WorkflowTemplate) => ({
        id: template.id,
        name: template.name,
        description: template.description,
        project: template.project,
        version: template.version,
        workflowSteps: template.workflowSteps,
        filePatterns: template.filePatterns,
        columnSettings: template.columnSettings,
        createdAt: template.createdAt,
        updatedAt: template.updatedAt,
        isTemporary: template.isTemporary,
        steps: template.workflowSteps,
        created: template.createdAt,
        lastModified: template.updatedAt
      }));
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['workflows'], 'readonly');
      const store = transaction.objectStore('workflows');
      const request = store.getAll();
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async getWorkflowsByProject(projectName: string): Promise<DatabaseWorkflow[]> {
    if (!(await this.ensureInitialized())) {
      // Fallback to localStorage
      const workflows = await this.getWorkflows();
      return workflows.filter(w => w.project === projectName);
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['workflows'], 'readonly');
      const store = transaction.objectStore('workflows');
      const index = store.index('project');
      const request = index.getAll(projectName);
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async updateWorkflow(workflow: DatabaseWorkflow): Promise<void> {
    if (!(await this.ensureInitialized())) {
      // Fallback to localStorage
      const workflows = JSON.parse(localStorage.getItem('workflowTemplates') || '[]');
      const index = workflows.findIndex((w: WorkflowTemplate) => w.id === workflow.id);
      if (index !== -1) {
        const template: WorkflowTemplate = {
          id: workflow.id,
          name: workflow.name,
          description: workflow.description,
          project: workflow.project,
          version: workflow.version,
          compatibility: { minVersion: '1.0.0', maxVersion: '2.0.0' },
          filePatterns: workflow.filePatterns,
          workflowSteps: workflow.workflowSteps,
          createdAt: workflow.createdAt,
          updatedAt: workflow.updatedAt,
          isTemporary: workflow.isTemporary,
          columnSettings: workflow.columnSettings
        };
        workflows[index] = template;
        localStorage.setItem('workflowTemplates', JSON.stringify(workflows));
      }
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['workflows'], 'readwrite');
      const store = transaction.objectStore('workflows');
      const request = store.put(workflow);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async deleteWorkflow(workflowId: string): Promise<void> {
    if (!(await this.ensureInitialized())) {
      // Fallback to localStorage
      const workflows = JSON.parse(localStorage.getItem('workflowTemplates') || '[]');
      const filteredWorkflows = workflows.filter((w: WorkflowTemplate) => w.id !== workflowId);
      localStorage.setItem('workflowTemplates', JSON.stringify(filteredWorkflows));
      
      // Update project data
      const projectData = JSON.parse(localStorage.getItem('projectData') || '{}');
      Object.keys(projectData).forEach(projectName => {
        projectData[projectName].workflows = projectData[projectName].workflows
          .filter((w: any) => w.id !== workflowId);
      });
      localStorage.setItem('projectData', JSON.stringify(projectData));
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['workflows'], 'readwrite');
      const store = transaction.objectStore('workflows');
      const request = store.delete(workflowId);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // Utility methods
  async clearAllData(): Promise<void> {
    if (!(await this.ensureInitialized())) {
      // Fallback to localStorage
      localStorage.removeItem('workflowTemplates');
      localStorage.removeItem('projectData');
      localStorage.removeItem('projects');
      return;
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['projects', 'workflows', 'files'], 'readwrite');
      
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const promises = [
        transaction.objectStore('projects').clear(),
        transaction.objectStore('workflows').clear(),
        transaction.objectStore('files').clear()
      ];
      
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  async exportData(): Promise<any> {
    const projects = await this.getProjects();
    const workflows = await this.getWorkflows();
    
    return {
      projects,
      workflows,
      exportedAt: new Date(),
      version: '1.0.0'
    };
  }

  async importData(data: any): Promise<void> {
    await this.clearAllData();
    
    for (const project of data.projects) {
      await this.createProject(project);
    }
    
    for (const workflow of data.workflows) {
      await this.createWorkflow(workflow);
    }
  }
}

// Export singleton instance
export const databaseManager = new DatabaseManager();
