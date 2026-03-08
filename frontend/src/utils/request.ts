/**
 * HTTP 请求工具
 */
import axios, { AxiosError, AxiosRequestConfig } from 'axios';

const API_BASE_URL = '/api';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证 token
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error: AxiosError) => {
    console.error('API Error:', error.message);
    
    // 统一错误处理
    if (error.response) {
      // 服务器返回错误响应
      const status = error.response.status;
      
      if (status === 401) {
        // 未授权，跳转登录
        console.error('Unauthorized');
      } else if (status === 403) {
        // 禁止访问
        console.error('Forbidden');
      } else if (status === 404) {
        // 资源不存在
        console.error('Not Found');
      } else if (status >= 500) {
        // 服务器错误
        console.error('Server Error');
      }
    } else if (error.request) {
      // 请求已发送但没有响应
      console.error('No response received');
    }
    
    return Promise.reject(error);
  }
);

// 封装请求方法
export const request = {
  get: <T>(url: string, config?: AxiosRequestConfig) => {
    return apiClient.get<T>(url, config);
  },
  
  post: <T>(url: string, data?: any, config?: AxiosRequestConfig) => {
    return apiClient.post<T>(url, data, config);
  },
  
  put: <T>(url: string, data?: any, config?: AxiosRequestConfig) => {
    return apiClient.put<T>(url, data, config);
  },
  
  delete: <T>(url: string, config?: AxiosRequestConfig) => {
    return apiClient.delete<T>(url, config);
  },
};

export default apiClient;
