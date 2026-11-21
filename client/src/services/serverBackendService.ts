import { cache } from "react";
import axios from "axios";
import { createBackendService } from "./backendService";
import { getBackendUrl, sessionHeaders } from "@/lib/serverBackend";

export const getServerBackendService = cache(async () => createBackendService(axios.create({
  baseURL: getBackendUrl(),
  headers: await sessionHeaders(),
})));
