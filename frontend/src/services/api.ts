import request from '@/utils/request';

export interface Interface {
  id?: number;
  name: string;
  url: string;
  method: string;
  headers?: any;
  params?: any;
  response_example?: any;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface TestPoint {
  id?: number;
  interface_id?: number;
  title: string;
  description?: string;
  test_type: 'api' | 'ui';
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  category?: string;
  created_at?: string;
}

export interface TestCase {
  id?: number;
  interface_id?: number;
  test_point_id?: number;
  name: string;
  description?: string;
  test_type: 'api' | 'ui';
  code: string;
  test_data?: any;
  expected_result?: string;
  tags?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface TestExecution {
  id?: number;
  test_case_id?: number;
  status: 'pending' | 'running' | 'success' | 'failed' | 'error';
  start_time?: string;
  end_time?: string;
  duration?: number;
  result?: any;
  error_message?: string;
  created_at?: string;
}

export interface TestReport {
  id?: number;
  execution_id: number;
  title: string;
  summary?: string;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  error_cases: number;
  pass_rate?: string;
  risk_analysis?: any;
  optimization_suggestions?: any;
  created_at?: string;
}

// Interface API
export const interfaceAPI = {
  list: (params?: any) => request.get('/interfaces/', { params }),
  create: (data: Interface) => request.post('/interfaces/', data),
  get: (id: number) => request.get(`/interfaces/${id}`),
  delete: (id: number) => request.delete(`/interfaces/${id}`),
  analyze: (id: number) => request.post(`/interfaces/${id}/analyze`),
  getTestPoints: (id: number) => request.get(`/interfaces/${id}/test-points`),
};

// Test Case API
export const testCaseAPI = {
  list: (params?: any) => request.get('/testcases/', { params }),
  create: (data: TestCase) => request.post('/testcases/', data),
  get: (id: number) => request.get(`/testcases/${id}`),
  update: (id: number, data: TestCase) => request.put(`/testcases/${id}`, data),
  delete: (id: number) => request.delete(`/testcases/${id}`),
  batchDelete: (ids: number[]) => request.post('/testcases/batch-delete', ids),
  batchExecute: (ids: number[]) => request.post('/testcases/batch-execute', ids),
  clone: (id: number) => request.post(`/testcases/${id}/clone`),
  generate: (testPointId: number) =>
    request.post(`/testcases/generate/${testPointId}`),
  execute: (id: number) => request.post(`/testcases/${id}/execute`),
  getExecutions: (id: number, params?: any) =>
    request.get(`/testcases/${id}/executions`, { params }),
  exportJson: (params?: any) => request.get('/testcases/export/json', { params }),
  importJson: (data: any[]) => request.post('/testcases/import/json', data),
};

// Report API
export const reportAPI = {
  list: (params?: any) => request.get('/reports/', { params }),
  get: (id: number) => request.get(`/reports/${id}`),
  generate: (executionId: number) =>
    request.post(`/reports/generate/${executionId}`),
  getByExecution: (executionId: number) =>
    request.get(`/reports/execution/${executionId}`),
};

