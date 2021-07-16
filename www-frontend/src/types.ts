export interface APIError {
  error: string;
}

export interface APISuccess {
  message: MessageNode[];
  timestamp: string;
  username: string;
}

export type APIResponse = APISuccess | APIError;

export interface EmoteNode {
  type: "emote";
  id: string;
  name: string;
  source: string;
}

export interface WordNode {
  type: "word";
  text: string;
}

export type MessageNode = EmoteNode | WordNode;
