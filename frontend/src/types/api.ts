export interface Message {
  id?: number;
  content: string;
  sender: string;
  timestamp?: string;
}

export interface User {
  id?: number;
  username: string;
  email: string;
}

export interface ApiResponse<T> {
  message?: string;
  data?: T;
  messages?: Message[];
  users?: User[];
} 