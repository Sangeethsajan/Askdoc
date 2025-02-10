export interface Document {
  id: number;
  user_id: string;
  filename: string;
  created_at: string;
}

export interface ChatProps {
  documents: Document[];            // Array of available documents
  selectedDocuments: number[];      // Array of selected document IDs
  onDocumentSelect: (ids: number[]) => void;  // Function to handle document selection
  userId: string;                   // Current user's ID
}
export interface ChatRequest {
  text: string;
  document_ids: number[];
  user_id: string;
}

export interface ChatResponse {
  answer: string;
  sources: {
    metadata: {
      content: string;
      filename: string;
      page_number: number;
    };
    score: number;
  }[];
}
// types/index.ts
export interface StreamResponse {
  content?: string;
  sources?: {
    metadata: {
      content: string;
      filename: string;
      page_number: number;
    };
    score: number;
  }[];
  error?: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: StreamResponse['sources'];  // Use the same type from StreamResponse
}