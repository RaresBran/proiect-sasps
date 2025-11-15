const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  is_completed: boolean;
  due_date: string | null;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface Stats {
  total_tasks: number;
  completed_tasks: number;
  completed_percentage: number;
}

class ApiClient {
  private getAuthHeader(): HeadersInit {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  async register(email: string, username: string, password: string, full_name?: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password, full_name }),
    });
    if (!response.ok) throw new Error('Registration failed');
    return response.json();
  }

  async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!response.ok) throw new Error('Login failed');
    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getAuthHeader(),
    });
    if (!response.ok) throw new Error('Failed to get user');
    return response.json();
  }

  async getTasks(status?: string, priority?: string): Promise<{ tasks: Task[]; total: number }> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    
    const response = await fetch(`${API_BASE_URL}/tasks/?${params}`, {
      headers: this.getAuthHeader(),
    });
    if (!response.ok) throw new Error('Failed to get tasks');
    return response.json();
  }

  async createTask(data: { title: string; description?: string; status?: string; priority?: string; due_date?: string }): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/tasks/`, {
      method: 'POST',
      headers: { ...this.getAuthHeader(), 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create task');
    return response.json();
  }

  async updateTask(id: number, data: Partial<Task>): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: { ...this.getAuthHeader(), 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update task');
    return response.json();
  }

  async deleteTask(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    });
    if (!response.ok) throw new Error('Failed to delete task');
  }

  async markTaskCompleted(id: number): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}/complete`, {
      method: 'PATCH',
      headers: this.getAuthHeader(),
    });
    if (!response.ok) throw new Error('Failed to mark task as completed');
    return response.json();
  }

  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE_URL}/stats/`, {
      headers: this.getAuthHeader(),
    });
    if (!response.ok) throw new Error('Failed to get stats');
    return response.json();
  }
}

export const apiClient = new ApiClient();

