// Central API client with error normalization

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    // Try to parse JSON
    let data: any = null;
    const text = await response.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        // Non-JSON response
      }
    }

    if (!response.ok) {
      const detail =
        data?.detail ||
        data?.message ||
        `Request failed (${response.status})`;
      throw new ApiError(response.status, detail);
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Network errors, CORS, etc.
    if (error instanceof TypeError) {
      throw new ApiError(
        0,
        "Unable to connect to the server. Please check your connection and try again."
      );
    }
    throw error;
  }
}

export { apiFetch };
