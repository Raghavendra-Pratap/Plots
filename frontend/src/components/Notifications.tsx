import React, { useState, useMemo } from 'react';
import { 
  Bell, 
  CheckCircle,
  AlertCircle, 
  Info, 
  Play, 
  FileText, 
  Folder, 
  Trash2, 
  Filter,
  Clock,
  Zap,
  Eye,
  EyeOff,
  X
} from 'lucide-react';
import { Card, CardContent } from './ui/card';

// Enhanced notification types based on the flow document
interface Notification {
  id: string;
  type: 'execution' | 'template' | 'error' | 'warning' | 'info';
  category: 'Execution Logs' | 'Template Events' | 'Errors & Warnings' | 'System Info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
  linkedReferences?: {
    templateName?: string;
    outputFolder?: string;
    fileName?: string;
    workflowId?: string;
  };
  metadata?: {
    executionTime?: number;
    fileSize?: string;
    rowCount?: number;
    errorCode?: string;
  };
}

interface NotificationsProps {
  notifications?: Notification[];
  onMarkAsRead?: (id: string) => void;
  onDelete?: (id: string) => void;
  onMarkAllAsRead?: () => void;
  onBulkDelete?: (ids: string[]) => void;
}

const Notifications: React.FC<NotificationsProps> = ({ 
  notifications: propNotifications, 
  onMarkAsRead, 
  onDelete, 
  onMarkAllAsRead,
  onBulkDelete
}) => {
  // Sample notifications data - in a real app, this would come from props or API
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'execution',
      category: 'Execution Logs',
      title: 'Workflow Execution Completed',
      message: 'Template "Customer Data Cleaner" executed successfully. Processed 1,250 rows in 45 seconds.',
      timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
      read: false,
      severity: 'low',
      linkedReferences: {
        templateName: 'Customer Data Cleaner',
        outputFolder: '/output/customer_data_2024-01-18/',
        workflowId: 'WF-001'
      },
      metadata: {
        executionTime: 45,
        fileSize: '2.3 MB',
        rowCount: 1250
      }
    },
    {
      id: '2',
      type: 'template',
      category: 'Template Events',
      title: 'New Template Created',
      message: 'Template "Sales Analytics" has been created and saved to your workspace.',
      timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 minutes ago
      read: false,
      severity: 'low',
      linkedReferences: {
        templateName: 'Sales Analytics',
        workflowId: 'WF-002'
      }
    },
    {
      id: '3',
      type: 'error',
      category: 'Errors & Warnings',
      title: 'Column Mismatch Detected',
      message: 'Template "Data Processor" failed due to missing column "Customer_ID" in input file.',
      timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
      read: false,
      severity: 'high',
      linkedReferences: {
        templateName: 'Data Processor',
        fileName: 'customer_data.csv'
      },
      metadata: {
        errorCode: 'COL_MISSING_001'
      }
    },
    {
      id: '4',
      type: 'warning',
      category: 'Errors & Warnings',
      title: 'Large File Processing',
      message: 'File "sales_data_2024.csv" (15.7 MB) is being processed. This may take several minutes.',
      timestamp: new Date(Date.now() - 45 * 60 * 1000), // 45 minutes ago
      read: true,
      severity: 'medium',
      linkedReferences: {
        fileName: 'sales_data_2024.csv'
      },
      metadata: {
        fileSize: '15.7 MB'
      }
    },
    {
      id: '5',
      type: 'execution',
      category: 'Execution Logs',
      title: 'Workflow Execution Failed',
      message: 'Template "Inventory Manager" failed during data transformation step. Check error logs for details.',
      timestamp: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
      read: true,
      severity: 'critical',
      linkedReferences: {
        templateName: 'Inventory Manager',
        workflowId: 'WF-003'
      },
      metadata: {
        errorCode: 'TRANSFORM_ERR_002'
      }
    },
    {
      id: '6',
      type: 'template',
      category: 'Template Events',
      title: 'Template Standardized',
      message: 'Template "Product Catalog" has been standardized according to company guidelines.',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      read: true,
      severity: 'low',
      linkedReferences: {
        templateName: 'Product Catalog'
      }
    },
    {
      id: '7',
      type: 'info',
      category: 'System Info',
      title: 'System Maintenance',
      message: 'Scheduled maintenance completed. All services are running normally.',
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000), // 3 hours ago
      read: true,
      severity: 'low'
    }
  ]);

  const [selectedNotifications, setSelectedNotifications] = useState<Set<string>>(new Set());
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [showRead, setShowRead] = useState(true);

  // Filter notifications based on current filters
  const filteredNotifications = useMemo(() => {
    return notifications.filter(notification => {
      const categoryMatch = filterCategory === 'all' || notification.category === filterCategory;
      const severityMatch = filterSeverity === 'all' || notification.severity === filterSeverity;
      const readMatch = showRead || !notification.read;
      
      return categoryMatch && severityMatch && readMatch;
    });
  }, [notifications, filterCategory, filterSeverity, showRead]);

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'execution':
        return <Play className="w-5 h-5 text-blue-500" />;
      case 'template':
        return <FileText className="w-5 h-5 text-purple-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-500" />;
      default:
        return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };



  const getSeverityBadge = (severity: Notification['severity']) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800'
    };

    return (
      <span className={`px-2 py-1 text-xs rounded-full font-medium ${colors[severity]}`}>
        {severity.charAt(0).toUpperCase() + severity.slice(1)}
      </span>
    );
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  };

  const handleMarkAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
    if (onMarkAsRead) onMarkAsRead(id);
  };

  const handleDelete = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    setSelectedNotifications(prev => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
    if (onDelete) onDelete(id);
  };

  const handleMarkAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    if (onMarkAllAsRead) onMarkAllAsRead();
  };

  const handleSelectNotification = (id: string) => {
    setSelectedNotifications(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedNotifications.size === filteredNotifications.length) {
      setSelectedNotifications(new Set());
    } else {
      setSelectedNotifications(new Set(filteredNotifications.map(n => n.id)));
    }
  };

  const handleBulkDelete = () => {
    if (selectedNotifications.size === 0) return;
    
    if (window.confirm(`Are you sure you want to delete ${selectedNotifications.size} notification(s)?`)) {
      const idsToDelete = Array.from(selectedNotifications);
      setNotifications(prev => prev.filter(n => !idsToDelete.includes(n.id)));
      setSelectedNotifications(new Set());
      if (onBulkDelete) onBulkDelete(idsToDelete);
    }
  };



  const unreadCount = notifications.filter(n => !n.read).length;
  const selectedCount = selectedNotifications.size;

  return (
    <div className="flex-1 p-6 overflow-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <h2 className="text-2xl font-bold flex items-center">
            <Bell className="w-6 h-6 mr-2" />
            Notifications
          </h2>
          {unreadCount > 0 && (
            <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full font-medium">
              {unreadCount} unread
            </span>
          )}
        </div>
        <div className="flex items-center space-x-3">
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllAsRead}
              className="px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Mark all as read
            </button>
          )}

        </div>
      </div>

      {/* Filters and Bulk Actions */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              {/* Category Filter */}
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Categories</option>
                  <option value="Execution Logs">Execution Logs</option>
                  <option value="Template Events">Template Events</option>
                  <option value="Errors & Warnings">Errors & Warnings</option>
                  <option value="System Info">System Info</option>
                </select>
              </div>

              {/* Severity Filter */}
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Severities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>

              {/* Show/Hide Read */}
              <button
                onClick={() => setShowRead(!showRead)}
                className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
              >
                {showRead ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                <span>{showRead ? 'Hide Read' : 'Show Read'}</span>
              </button>
            </div>

            {/* Bulk Actions */}
            {selectedCount > 0 && (
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-600">
                  {selectedCount} selected
                </span>
                <button
                  onClick={handleSelectAll}
                  className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors"
                >
                  {selectedCount === filteredNotifications.length ? 'Deselect All' : 'Select All'}
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded transition-colors flex items-center"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Delete Selected
                </button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Notifications List */}
      {filteredNotifications.length === 0 ? (
        <div className="text-center py-12">
          <Bell className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No notifications</h3>
          <p className="text-gray-500">
            {filterCategory === 'all' && filterSeverity === 'all' && showRead
              ? "You're all caught up!"
              : "No notifications match the current filters."}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredNotifications.map((notification) => (
            <Card key={notification.id} className={`${notification.read ? 'opacity-75' : ''}`}>
              <CardContent className="p-4">
                <div className="flex items-start space-x-3">
                  {/* Selection Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedNotifications.has(notification.id)}
                    onChange={() => handleSelectNotification(notification.id)}
                    className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  />

                  {/* Notification Icon */}
                  {getNotificationIcon(notification.type)}

                  {/* Notification Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className={`font-medium ${notification.read ? 'text-gray-600' : 'text-gray-900'}`}>
                            {notification.title}
                          </h4>
                          {getSeverityBadge(notification.severity)}
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                            {notification.category}
                          </span>
                        </div>
                        
                        <p className={`text-sm mb-3 ${notification.read ? 'text-gray-500' : 'text-gray-700'}`}>
                          {notification.message}
                        </p>

                        {/* Linked References */}
                        {notification.linkedReferences && (
                          <div className="flex flex-wrap gap-2 mb-3">
                            {notification.linkedReferences.templateName && (
                              <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                <FileText className="w-3 h-3 mr-1" />
                                {notification.linkedReferences.templateName}
                              </span>
                            )}
                            {notification.linkedReferences.outputFolder && (
                              <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                <Folder className="w-3 h-3 mr-1" />
                                {notification.linkedReferences.outputFolder}
                              </span>
                            )}
                            {notification.linkedReferences.fileName && (
                              <span className="inline-flex items-center px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                                <FileText className="w-3 h-3 mr-1" />
                                {notification.linkedReferences.fileName}
                              </span>
                            )}
                            {notification.linkedReferences.workflowId && (
                              <span className="inline-flex items-center px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                                <Zap className="w-3 h-3 mr-1" />
                                {notification.linkedReferences.workflowId}
                              </span>
                            )}
                          </div>
                        )}

                        {/* Metadata */}
                        {notification.metadata && (
                          <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                            {notification.metadata.executionTime && (
                              <span className="flex items-center">
                                <Clock className="w-3 h-3 mr-1" />
                                {notification.metadata.executionTime}s
                              </span>
                            )}
                            {notification.metadata.fileSize && (
                              <span className="flex items-center">
                                <FileText className="w-3 h-3 mr-1" />
                                {notification.metadata.fileSize}
                              </span>
                            )}
                            {notification.metadata.rowCount && (
                              <span className="flex items-center">
                                <FileText className="w-3 h-3 mr-1" />
                                {notification.metadata.rowCount} rows
                              </span>
                            )}
                            {notification.metadata.errorCode && (
                              <span className="flex items-center">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                {notification.metadata.errorCode}
                              </span>
                            )}
                          </div>
                        )}

                        <p className="text-xs text-gray-400 mt-2 flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatTimeAgo(notification.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-2">
                    {!notification.read && (
                      <button
                        onClick={() => handleMarkAsRead(notification.id)}
                        className="p-2 text-gray-400 hover:text-green-600 transition-colors rounded"
                        title="Mark as read"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(notification.id)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors rounded"
                      title="Delete notification"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notifications;
