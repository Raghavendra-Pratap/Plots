// Formula Service - Bridge between React frontend and Python formula engine
import { dataProcessor } from './dataProcessor';

export interface FormulaDefinition {
  name: string;
  category: string;
  description: string;
  syntax: string;
  parameters: FormulaParameter[];
  examples: string[];
  aliases?: string[];
}

export interface FormulaParameter {
  name: string;
  type: 'column' | 'value' | 'number' | 'string' | 'boolean';
  description: string;
  required: boolean;
  defaultValue?: any;
}

export interface FormulaExecutionResult {
  success: boolean;
  data?: any[];
  columns?: string[];
  error?: string;
  executionTime: number;
  memoryUsage: number;
}

export interface FormulaStep {
  id: string;
  type: 'formula';
  formulaName: string;
  parameters: string[];
  sourceColumns: string[];
  targetColumn?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

// Core formula definitions based on DATA_STUDIO_FORMULA_REFERENCE.md
export const CORE_FORMULAS: FormulaDefinition[] = [
  {
    name: 'TEXT_JOIN',
    category: 'Text & String',
    description: 'Joins text values together, with optional delimiter and empty handling.',
    syntax: 'TEXT_JOIN [delimiter -> ignore_empty -> text1 -> text2 -> ...]',
    parameters: [
      { name: 'delimiter', type: 'string', description: 'Character(s) placed between joined texts', required: true },
      { name: 'ignore_empty', type: 'boolean', description: 'TRUE/FALSE (skip blanks or not)', required: true },
      { name: 'text_values', type: 'column', description: 'Values to join', required: true }
    ],
    examples: ['TEXT_JOIN [", " -> TRUE -> City -> State -> Country]']
  },
  {
    name: 'UPPER',
    category: 'Text & String',
    description: 'Converts text to uppercase.',
    syntax: 'UPPER [column]',
    parameters: [
      { name: 'column', type: 'column', description: 'The text column to convert', required: true }
    ],
    examples: ['UPPER [Name]', 'UPPER [Email]']
  },
  {
    name: 'LOWER',
    category: 'Text & String',
    description: 'Converts text to lowercase.',
    syntax: 'LOWER [column]',
    parameters: [
      { name: 'column', type: 'column', description: 'The text column to convert', required: true }
    ],
    examples: ['LOWER [Name]', 'LOWER [Email]']
  },
  {
    name: 'TRIM',
    category: 'Text & String',
    description: 'Removes extra spaces from text, leaving single spaces between words.',
    syntax: 'TRIM [column]',
    parameters: [
      { name: 'column', type: 'column', description: 'The text column to clean', required: true }
    ],
    examples: ['TRIM [Comments]', 'TRIM [Address]']
  },
  {
    name: 'TEXT_LENGTH',
    category: 'Text & String',
    description: 'Returns the length of a text string.',
    syntax: 'TEXT_LENGTH [column]',
    parameters: [
      { name: 'column', type: 'column', description: 'The text column to measure', required: true }
    ],
    examples: ['TEXT_LENGTH [Name]', 'TEXT_LENGTH [Email]']
  },
  {
    name: 'PROPER_CASE',
    category: 'Text & String',
    description: 'Converts text to proper case (capitalize each word).',
    syntax: 'PROPER_CASE [column]',
    parameters: [
      { name: 'column', type: 'column', description: 'The text column to convert', required: true }
    ],
    examples: ['PROPER_CASE [Name]', 'PROPER_CASE [Title]']
  },
  {
    name: 'ADD',
    category: 'Mathematical',
    description: 'Adds two numbers or columns.',
    syntax: 'ADD [column1 -> column2]',
    parameters: [
      { name: 'column1', type: 'column', description: 'First number column', required: true },
      { name: 'column2', type: 'column', description: 'Second number column', required: true }
    ],
    examples: ['ADD [Price -> Tax]', 'ADD [Quantity -> Bonus]']
  },
  {
    name: 'SUBTRACT',
    category: 'Mathematical',
    description: 'Subtracts one number from another.',
    syntax: 'SUBTRACT [column1 -> column2]',
    parameters: [
      { name: 'column1', type: 'column', description: 'First number column', required: true },
      { name: 'column2', type: 'column', description: 'Second number column', required: true }
    ],
    examples: ['SUBTRACT [Total -> Discount]', 'SUBTRACT [Revenue -> Cost]']
  },
  {
    name: 'MULTIPLY',
    category: 'Mathematical',
    description: 'Multiplies two numbers.',
    syntax: 'MULTIPLY [column1 -> column2]',
    parameters: [
      { name: 'column1', type: 'column', description: 'First number column', required: true },
      { name: 'column2', type: 'column', description: 'Second number column', required: true }
    ],
    examples: ['MULTIPLY [Price -> Quantity]', 'MULTIPLY [Rate -> Hours]']
  },
  {
    name: 'DIVIDE',
    category: 'Mathematical',
    description: 'Divides one number by another.',
    syntax: 'DIVIDE [column1 -> column2]',
    parameters: [
      { name: 'column1', type: 'column', description: 'First number column', required: true },
      { name: 'column2', type: 'column', description: 'Second number column', required: true }
    ],
    examples: ['DIVIDE [Total -> Quantity]', 'DIVIDE [Revenue -> Units]']
  },
  {
    name: 'SUM',
    category: 'Mathematical',
    description: 'Sums values across columns for each row.',
    syntax: 'SUM [column1 -> column2 -> column3]',
    parameters: [
      { name: 'columns', type: 'column', description: 'Columns to sum', required: true }
    ],
    examples: ['SUM [Q1 -> Q2 -> Q3 -> Q4]', 'SUM [Sales -> Bonus -> Commission]']
  },
  {
    name: 'COUNT',
    category: 'Statistical',
    description: 'Counts non-null values in a column.',
    syntax: 'COUNT [column]',
    parameters: [
      { name: 'column', type: 'column', description: 'The column to count', required: true }
    ],
    examples: ['COUNT [ID]', 'COUNT [Sales]']
  },
  {
    name: 'UNIQUE_COUNT',
    category: 'Statistical',
    description: 'Counts unique values in a column.',
    syntax: 'UNIQUE_COUNT [column]',
    parameters: [
      { name: 'column', type: 'column', description: 'The column to count unique values', required: true }
    ],
    examples: ['UNIQUE_COUNT [Customer_ID]', 'UNIQUE_COUNT [Category]']
  },
  {
    name: 'IF',
    category: 'Conditional',
    description: 'Conditional logic with true/false values.',
    syntax: 'IF [condition_column -> condition_value -> true_value -> false_value]',
    parameters: [
      { name: 'condition_column', type: 'column', description: 'Column to check condition', required: true },
      { name: 'condition_value', type: 'value', description: 'Value to compare against', required: true },
      { name: 'true_value', type: 'value', description: 'Value if condition is true', required: true },
      { name: 'false_value', type: 'value', description: 'Value if condition is false', required: true }
    ],
    examples: ['IF [Status -> "Active" -> "Valid" -> "Invalid"]', 'IF [Amount -> 1000 -> "High" -> "Low"]']
  },
  {
    name: 'SUMIF',
    category: 'Conditional',
    description: 'Sums values when condition is met.',
    syntax: 'SUMIF [condition_column -> condition_value -> target_column]',
    parameters: [
      { name: 'condition_column', type: 'column', description: 'Column to check condition', required: true },
      { name: 'condition_value', type: 'value', description: 'Value to compare against', required: true },
      { name: 'target_column', type: 'column', description: 'Column to sum when condition is met', required: true }
    ],
    examples: ['SUMIF [Status -> "Active" -> Amount]', 'SUMIF [Category -> "Electronics" -> Sales]']
  },
  {
    name: 'COUNTIF',
    category: 'Conditional',
    description: 'Counts rows when condition is met.',
    syntax: 'COUNTIF [condition_column -> condition_value]',
    parameters: [
      { name: 'condition_column', type: 'column', description: 'Column to check condition', required: true },
      { name: 'condition_value', type: 'value', description: 'Value to compare against', required: true }
    ],
    examples: ['COUNTIF [Status -> "Active"]', 'COUNTIF [Amount -> ">1000"]']
  },
  {
    name: 'PIVOT',
    category: 'Data Transformation',
    description: 'Reorganizes data by categories.',
    syntax: 'PIVOT [index_column -> value_column]',
    parameters: [
      { name: 'index_column', type: 'column', description: 'Column to use as index', required: true },
      { name: 'value_column', type: 'column', description: 'Column to use as values', required: true }
    ],
    examples: ['PIVOT [Category -> Sales]', 'PIVOT [Month -> Revenue]']
  },
  {
    name: 'DEPIVOT',
    category: 'Data Transformation',
    description: 'Converts wide data to long format.',
    syntax: 'DEPIVOT [id_columns]',
    parameters: [
      { name: 'id_columns', type: 'column', description: 'Columns to keep as identifiers', required: true }
    ],
    examples: ['DEPIVOT [ID -> Name]', 'DEPIVOT [Customer_ID -> Product_ID]']
  },
  {
    name: 'REMOVE_DUPLICATES',
    category: 'Data Cleaning',
    description: 'Removes duplicate rows based on selected columns.',
    syntax: 'REMOVE_DUPLICATES [columns]',
    parameters: [
      { name: 'columns', type: 'column', description: 'Columns to check for duplicates', required: true }
    ],
    examples: ['REMOVE_DUPLICATES [Email]', 'REMOVE_DUPLICATES [Customer_ID -> Order_ID]']
  },
  {
    name: 'FILLNA',
    category: 'Data Cleaning',
    description: 'Fills null values with specified value.',
    syntax: 'FILLNA [column -> value]',
    parameters: [
      { name: 'column', type: 'column', description: 'Column to fill null values', required: true },
      { name: 'value', type: 'value', description: 'Value to use for null values', required: true }
    ],
    examples: ['FILLNA [Phone -> "N/A"]', 'FILLNA [Amount -> 0]']
  }
];

class FormulaService {
  private formulas: Map<string, FormulaDefinition> = new Map();

  constructor() {
    this.initializeFormulas();
  }

  private initializeFormulas() {
    // Load core formulas
    CORE_FORMULAS.forEach(formula => {
      this.formulas.set(formula.name, formula);
      // Also add aliases
      if (formula.aliases) {
        formula.aliases.forEach(alias => {
          this.formulas.set(alias, { ...formula, name: alias });
        });
      }
    });
  }

  // Get all available formulas
  getAllFormulas(): FormulaDefinition[] {
    return Array.from(this.formulas.values());
  }

  // Get formula by name
  getFormula(name: string): FormulaDefinition | undefined {
    return this.formulas.get(name.toUpperCase());
  }

  // Get formulas by category
  getFormulasByCategory(): Record<string, FormulaDefinition[]> {
    const categorized: Record<string, FormulaDefinition[]> = {};
    
    this.getAllFormulas().forEach(formula => {
      if (!categorized[formula.category]) {
        categorized[formula.category] = [];
      }
      categorized[formula.category].push(formula);
    });
    
    return categorized;
  }

  // Parse formula string into components
  parseFormula(formulaString: string): { formulaName: string; parameters: string[] } | null {
    try {
      // Format: FORMULA_NAME [param1 -> param2 -> param3]
      const match = formulaString.match(/^(\w+)\s*\[(.*)\]$/);
      if (!match) return null;
      
      const formulaName = match[1].toUpperCase();
      const paramsString = match[2];
      
      // Split by -> and clean up
      const parameters = paramsString
        .split('->')
        .map(param => param.trim())
        .filter(param => param.length > 0);
      
      return { formulaName, parameters };
    } catch (error) {
      console.error('Error parsing formula:', error);
      return null;
    }
  }

  // Validate formula parameters
  validateFormula(formulaName: string, parameters: string[]): { isValid: boolean; errors: string[] } {
    const formula = this.getFormula(formulaName);
    if (!formula) {
      return { isValid: false, errors: [`Unknown formula: ${formulaName}`] };
    }

    const errors: string[] = [];
    const requiredParams = formula.parameters.filter(p => p.required);
    
    if (parameters.length < requiredParams.length) {
      errors.push(`Formula ${formulaName} requires ${requiredParams.length} parameters, got ${parameters.length}`);
    }
    
    if (parameters.length > formula.parameters.length) {
      errors.push(`Formula ${formulaName} accepts maximum ${formula.parameters.length} parameters, got ${parameters.length}`);
    }
    
    return { isValid: errors.length === 0, errors };
  }

  // Execute formula on data
  async executeFormula(
    formulaName: string,
    parameters: string[],
    data: any[],
    columns: string[]
  ): Promise<FormulaExecutionResult> {
    const startTime = performance.now();
    
    try {
      // Validate formula
      const validation = this.validateFormula(formulaName, parameters);
      if (!validation.isValid) {
        return {
          success: false,
          error: validation.errors.join(', '),
          executionTime: performance.now() - startTime,
          memoryUsage: 0
        };
      }

      // Execute formula using data processor
      const result = await dataProcessor.processWorkflowStep({
        id: `formula_${Date.now()}`,
        type: 'function',
        source: formulaName,
        parameters,
        status: 'processing'
      }, [{
        name: 'formula_data',
        type: 'application/json',
        data,
        columns
      }], data.length);

      const executionTime = performance.now() - startTime;
      const memoryUsage = this.estimateMemoryUsage(result.data);

      return {
        success: true,
        data: result.data,
        columns: result.columns,
        executionTime,
        memoryUsage
      };

    } catch (error) {
      console.error(`Error executing formula ${formulaName}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        executionTime: performance.now() - startTime,
        memoryUsage: 0
      };
    }
  }

  // Estimate memory usage
  private estimateMemoryUsage(data: any[]): number {
    if (data.length === 0) return 0;
    
    try {
      const rowSize = JSON.stringify(data[0]).length;
      const totalSize = data.length * rowSize;
      return Math.round(totalSize / (1024 * 1024) * 100) / 100; // MB
    } catch (error) {
      return 0;
    }
  }

  // Search formulas
  searchFormulas(query: string): FormulaDefinition[] {
    const searchTerm = query.toLowerCase();
    return this.getAllFormulas().filter(formula => 
      formula.name.toLowerCase().includes(searchTerm) ||
      formula.description.toLowerCase().includes(searchTerm) ||
      formula.category.toLowerCase().includes(searchTerm) ||
      (formula.aliases && formula.aliases.some(alias => 
        alias.toLowerCase().includes(searchTerm)
      ))
    );
  }

  // Get formula examples
  getFormulaExamples(formulaName: string): string[] {
    const formula = this.getFormula(formulaName);
    return formula?.examples || [];
  }

  // Get formula syntax
  getFormulaSyntax(formulaName: string): string {
    const formula = this.getFormula(formulaName);
    return formula?.syntax || 'Unknown formula';
  }
}

// Export singleton instance
export const formulaService = new FormulaService();
export default formulaService;
