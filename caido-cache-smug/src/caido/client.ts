import { request } from "undici";

export interface CaidoClientOpts {
  url: string;
  token: string;
}

export class CaidoClient {
  private url: string;
  private token: string;

  constructor(opts: CaidoClientOpts) {
    if (!opts.token) throw new Error("Caido token required");
    this.url = opts.url.replace(/\/$/, "");
    this.token = opts.token;
  }

  authHeader(): string {
    return `Bearer ${this.token}`;
  }

  async graphql<T>(query: string, variables: Record<string, unknown> = {}): Promise<T> {
    const res = await request(`${this.url}/graphql`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: this.authHeader()
      },
      body: JSON.stringify({ query, variables })
    });
    if (res.statusCode >= 400) throw new Error(`Caido GraphQL ${res.statusCode}`);
    const json = (await res.body.json()) as { data?: T; errors?: unknown };
    if (json.errors) throw new Error(`Caido GraphQL errors: ${JSON.stringify(json.errors)}`);
    return json.data as T;
  }
}
