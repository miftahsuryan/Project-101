export type Asset = {
  id: string;
  asset_code: string;
  name: string;
};

export type CreateAssetRequest = {
  asset_code: string;
  name: string;
};

export type PredictionRequest = {
  asset_id: string;
  readings: number[];
};

export type Prediction = {
  asset_id: string;
  predicted_value: number;
  model_version: "fake-v1";
};

export type ApiErrorDetail = {
  field: string;
  message: string;
};

export type ApiErrorResponse = {
  error: {
    code: string;
    message: string;
    details: ApiErrorDetail[];
  };
};

export type HealthResponse = {
  status: "ok";
  environment: "development" | "test" | "production";
};

export type OverviewResponse = {
  total_assets: number;
  total_readings: number;
  average_reading: number | null;
  latest_reading: number | null;
}

export type Reading = {
  id: string;
  asset_code: string;
  value: number;
};

export type ReadingPage = {
  items: Reading[];
  limit: number;
  offset: number;
  total: number;
};
const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

function isApiErrorResponse(value: unknown): value is ApiErrorResponse {
  if (
    typeof value !== "object" ||
    value === null ||
    !("error" in value)
  ) {
    return false;
  }

  const error = value.error;

  return (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof error.message === "string"
  );
}

async function request<T>(
  path: string,
  options: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const body: unknown = await response.json();

  if (!response.ok) {
    const message = isApiErrorResponse(body)
      ? body.error.message
      : `Request failed with status ${response.status}.`;

    throw new ApiRequestError(message, response.status);
  }

  return body as T;
}

export function createAsset(
  payload: CreateAssetRequest,
): Promise<Asset> {
  return request<Asset>("/api/v1/assets", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function createPrediction(
  payload: PredictionRequest,
): Promise<Prediction> {
  return request<Prediction>("/api/v1/predictions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function listAssets(): Promise<Asset[]> {
  return request<Asset[]>(
    "/api/v1/assets?limit=20&offset=0",
    {
      method: "GET",
    },
  );
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/v1/health", {
    method: "GET",
  });
}

export function getOverview(): Promise<OverviewResponse> {
  return request<OverviewResponse>("/api/v1/overview",{
    method: "GET"
  });
}

export function listReadings(
  assetCode = "",
  limit = 20,
  offset = 0,
): Promise<ReadingPage> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  if (assetCode.trim() !== "") {
    params.set("asset_code", assetCode.trim());
  }

  return request<ReadingPage>(
    `/api/v1/readings?${params.toString()}`,
    {
      method: "GET",
    },
  );
}