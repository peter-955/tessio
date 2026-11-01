type EventHandler = ((event: ProgressEvent) => void) | null;

interface FakeXmlHttpRequestUpload {
  onprogress: EventHandler;
}

export class FakeXmlHttpRequest {
  static instances: FakeXmlHttpRequest[] = [];

  method: string | null = null;
  url: string | null = null;
  body: FormData | null = null;
  withCredentials = false;
  requestHeaders: Record<string, string> = {};
  status = 0;
  statusText = "";
  responseText = "";
  isSent = false;
  isAborted = false;
  upload: FakeXmlHttpRequestUpload = { onprogress: null };
  onload: EventHandler = null;
  onerror: EventHandler = null;
  ontimeout: EventHandler = null;
  onabort: EventHandler = null;

  constructor() {
    FakeXmlHttpRequest.instances.push(this);
  }

  static get latest(): FakeXmlHttpRequest | undefined {
    return FakeXmlHttpRequest.instances.at(-1);
  }

  static reset(): void {
    FakeXmlHttpRequest.instances = [];
  }

  open(method: string, url: string): void {
    this.method = method;
    this.url = url;
  }

  setRequestHeader(name: string, value: string): void {
    this.requestHeaders[name] = value;
  }

  send(body: FormData): void {
    this.body = body;
    this.isSent = true;
  }

  abort(): void {
    this.isAborted = true;
    this.onabort?.(new ProgressEvent("abort"));
  }

  emitProgress(loaded: number, total: number): void {
    this.upload.onprogress?.(
      new ProgressEvent("progress", { lengthComputable: true, loaded, total }),
    );
  }

  respond(status: number, responseText = "", statusText = ""): void {
    this.status = status;
    this.statusText = statusText;
    this.responseText = responseText;
    this.onload?.(new ProgressEvent("load"));
  }

  failNetwork(): void {
    this.onerror?.(new ProgressEvent("error"));
  }
}
