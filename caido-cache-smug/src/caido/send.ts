import type { CaidoClient } from "./client.js";
import type { Throttle } from "../core/throttle.js";
import type { HttpMessage } from "../types.js";

const SEND_MUTATION = `
  mutation SendRequest($input: SendRequestInput!) {
    sendRequest(input: $input) {
      request { id }
      response { id status headers body }
    }
  }
`;

export interface SendResult {
  requestId: string;
  response: HttpMessage;
}

export class CaidoSender {
  constructor(private client: CaidoClient, private throttle: Throttle) {}

  async send(req: HttpMessage): Promise<SendResult> {
    await this.throttle.acquire();
    const data = await this.client.graphql<{
      sendRequest: {
        request: { id: string };
        response: { id: string; status: number; headers: string; body: string };
      };
    }>(SEND_MUTATION, {
      input: {
        method: req.method,
        url: req.url,
        headers: Object.entries(req.headers).map(([name, value]) => ({ name, value })),
        body: req.body
      }
    });
    return {
      requestId: data.sendRequest.request.id,
      response: {
        status: data.sendRequest.response.status,
        headers: JSON.parse(data.sendRequest.response.headers),
        body: data.sendRequest.response.body
      }
    };
  }
}
