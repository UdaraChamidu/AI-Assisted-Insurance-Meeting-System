/**
 * API client for backend communication
 */

import { config } from '../config';

export interface LeadCreate {
  phone_number: string;
  customer_name?: string;
  notes?: string;
}

export interface Session {
  id: string;
  booking_id?: string;
  zoom_meeting_id?: string;
  zoom_meeting_password?: string;
  status: string;
  participants: any[];
  created_at: string;
  expires_at: string;
}

export interface ZoomSignature {
  signature: string;
  sdk_key: string;
  meeting_number: string;
  password?: string;
}

export interface AIResponse {
  answer: string;
  follow_up_question?: string;
  confidence: number;
  rag_context?: any;
  timestamp: string;
}

class APIClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = config.apiUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || 'API request failed');
    }

    return response.json();
  }

  // Leads
  async createLead(data: LeadCreate) {
    return this.request('/api/leads', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listLeads(): Promise<any[]> {
    return this.request('/api/leads');
  }

  async resendSMS(leadId: string) {
    return this.request(`/api/leads/${leadId}/resend-sms`, {
      method: 'POST',
    });
  }

  async getLead(leadId: string) {
    return this.request(`/api/leads/${leadId}`);
  }

  // Bookings
  async createBooking(data: {
    lead_id?: string;
    customer_name: string;
    customer_email: string;
    customer_phone: string;
    scheduled_date: string;
    scheduled_time: string;
    notes?: string;
  }) {
    return this.request('/api/bookings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listBookings(): Promise<any[]> {
    return this.request('/api/bookings');
  }

  async sendReminder(bookingId: string) {
    return this.request(`/api/bookings/${bookingId}/send-reminder`, {
      method: 'POST',
    });
  }

  // Authentication
  async login(credentials: { email: string; password: string }) {
    return this.request<{ access_token: string; refresh_token: string; token_type: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: { email: string; password: string; full_name: string; role?: string }) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async refreshToken(refreshToken: string) {
    return this.request('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async getCurrentUser() {
    const token = localStorage.getItem('access_token');
    return this.request('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }



  // Sessions
  async createSession(bookingId?: string): Promise<Session> {
    return this.request('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ booking_id: bookingId }),
    });
  }

  async listSessions(): Promise<Session[]> {
    return this.request('/api/sessions');
  }

  async getSession(sessionId: string): Promise<Session> {
    return this.request(`/api/sessions/${sessionId}`);
  }

  async joinSession(
    sessionId: string,
    role: 'staff' | 'customer',
    userId?: string,
    name?: string
  ): Promise<Session> {
    return this.request(`/api/sessions/${sessionId}/join?role=${role}`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, name }),
    });
  }

  // Zoom
  async generateZoomSignature(
    meetingNumber: string,
    role: number = 0
  ): Promise<ZoomSignature> {
    return this.request('/api/zoom/signature', {
      method: 'POST',
      body: JSON.stringify({ meeting_number: meetingNumber, role }),
    });
  }

  // AI
  async queryAI(query: string, sessionId?: string): Promise<AIResponse> {
    return this.request('/api/ai/query', {
      method: 'POST',
      body: JSON.stringify({ query, session_id: sessionId }),
    });
  }

  async chatAI(query: string, sessionId?: string): Promise<AIResponse> {
    return this.request('/api/ai/chat', { // Use simple chat endpoint
      method: 'POST',
      body: JSON.stringify({ query, session_id: sessionId }),
    });
  }
}

export const apiClient = new APIClient();
