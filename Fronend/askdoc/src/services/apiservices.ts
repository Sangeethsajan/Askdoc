import axios,{AxiosRequestConfig} from 'axios';

const BASE_URL = 'http://localhost:8000'
const makeAPIRequest = async (url: string, method: string, data: FormData,config?: AxiosRequestConfig) => {
  try {
    const response = await axios({
      method,
      url: `${BASE_URL}/${url}`,
      data,
      ...config
    });
    return response.data;
  } catch (error) {
    console.error("API request failed:", error);
    return null;
  }
}

const makeStreamingAPIREquest = async (url: string, method: string, data: FormData) => {
    try{
        const response = await fetch(`${BASE_URL}/${url}`, {method, body: data});
        return response;
    }
    catch(error){
        console.error("Streaming API request failed:", error);
        return null;
    }

    
}

export {makeAPIRequest, makeStreamingAPIREquest};