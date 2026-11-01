export interface ApiResponseStub {
  data?: unknown;
  error?: unknown;
  response: Response;
}

export const buildSuccessResponse = (data: unknown): ApiResponseStub => {
  return { data, response: new Response(null, { status: 200 }) };
};

export const buildErrorResponse = (status: number, code: string): ApiResponseStub => {
  return {
    error: { code, message: code },
    response: new Response(null, { status }),
  };
};
