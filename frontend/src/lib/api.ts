// Base API URL - uses NEXT_PUBLIC_API_BASE from environment variables
const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || 'https://decode-ndis-perplexity.onrender.com').replace(/\/+$/, '');

// Helper function to construct API URLs safely
const getApiUrl = (endpoint: string): string => {
  // Remove leading/trailing slashes from endpoint
  const cleanEndpoint = endpoint.replace(/^\/+|\/+$/g, '');  
  
  return `${API_BASE}/${cleanEndpoint}`;
};

/**
 * Fetch data from a backend API endpoint with support for request cancellation
 * @param endpoint The API endpoint path (without leading/trailing slashes)
 * @param body The request body as a string
 * @param abortController Optional AbortController to allow cancellation
 * @returns The JSON response from the API
 */
export const fetchFromEndpoint = async (
  endpoint: string, 
  body: string, 
  abortController?: AbortController
) => {
  const url = getApiUrl(endpoint);
  console.log('Making request to:', url); // Debug log
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      body,
      headers: {
        'Content-Type': 'application/json',
      },
      signal: abortController?.signal,
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('API Error:', {
        status: response.status,
        statusText: response.statusText,
        url,
        error: errorData,
      });
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
};
