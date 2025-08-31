import React from 'react';

const Visualizations: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Visualizations
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Interactive charts and dashboards for data insights
        </p>
      </div>
      
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <p className="text-gray-600 dark:text-gray-400">
          Visualization interface coming soon...
        </p>
      </div>
    </div>
  );
};

export default Visualizations;
