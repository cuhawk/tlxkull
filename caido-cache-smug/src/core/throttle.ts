interface ThrottleOpts {
  rps: number;
  burst?: number;
  hardFloorRps?: number;
}

export class Throttle {
  private rps: number;
  private capacity: number;
  private tokens: number;
  private last: number;

  constructor(opts: ThrottleOpts) {
    this.rps = opts.hardFloorRps ? Math.min(opts.rps, opts.hardFloorRps) : opts.rps;
    this.capacity = opts.burst ?? Math.max(1, Math.floor(this.rps));
    this.tokens = this.capacity;
    this.last = Date.now();
  }

  async acquire(): Promise<void> {
    while (true) {
      this.refill();
      if (this.tokens >= 1) {
        this.tokens -= 1;
        return;
      }
      const waitMs = Math.ceil((1 - this.tokens) * (1000 / this.rps));
      await new Promise((r) => setTimeout(r, waitMs));
    }
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.last) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.rps);
    this.last = now;
  }
}
