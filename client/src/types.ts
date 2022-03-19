interface APIError {
  source: string;
  id: string;
  details?: string;
}

export interface APIErrors {
  errors: APIError[];
}

interface APISource {
  lines: number;
  logFiles: number;
  first: string;
  last: string;
}

export type APISources = Record<string, APISource>;

export interface APISuccess {
  message: MessageNode[];
  timestamp: string;
  username: string;
}

export type APIResponse = APISuccess | APIErrors;

export interface EmoteNode {
  type: "emote";
  id: string;
  name: string;
  source: string;
}

export interface TextNode {
  type: "text";
  text: string;
}

export type MessageNode = EmoteNode | TextNode;
