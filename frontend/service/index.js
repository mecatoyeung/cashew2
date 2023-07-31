import axios from 'axios'

class Service {
  constructor() {
    let service = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_BASE_URL
    });
    service.interceptors.response.use(this.handleSuccess, this.handleError)
    service.interceptors.request.use(function (config) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Token ${token}`
      }
      return config
    })
    this.service = service
  }

  handleSuccess(response) {
    return response;
  }

  handleError = (error) => {
    console.error(error)
    let callbackUrl
    switch (error.response.status) {
      case 400:
        console.error(error)
        break;
      case 401:
        callbackUrl = document.location
        this.redirectTo(document, '/signin?callbackUrl=' + callbackUrl)
        break;
      case 403:
        callbackUrl = document.location
        this.redirectTo(document, '/signin?callbackUrl=' + callbackUrl)
        break;
      case 404:
        console.error(error)
        //this.redirectTo(document, '/404')
        break;
      default:
        console.error(error)
        //this.redirectTo(document, '/500')
        break;
    }
    return Promise.reject(error)
  }

  redirectTo = (document, path) => {
    document.location = path
  }

  get(path, callback) {
    return this.service.get(path).then(
      (response) => callback(response)
    );
  }

  getFile(path, callback) {
    let service = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
      responseType: "arraybuffer",
    })
    service.interceptors.response.use(this.handleSuccess, this.handleError)
    service.interceptors.request.use(function (config) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Token ${token}`
      }
      return config
    })
    return service.get(path).then(
      (response) => callback(response)
    );
  }

  patch(path, payload, callback) {
    return this.service.request({
      method: 'PATCH',
      url: path,
      responseType: 'json',
      data: payload
    }).then((response) => callback(response));
  }

  post(path, payload, callback, errorCallback = null) {
    return this.service.request({
      method: 'POST',
      url: path,
      responseType: 'json',
      data: payload
    }).then((response) => {
      callback(response)
    }).catch((error) => {
      if (errorCallback == null) return
      errorCallback(error)
    });
  }

  put(path, payload, callback, errorCallback = null) {
    return this.service.request({
      method: 'PUT',
      url: path,
      responseType: 'json',
      data: payload
    }).then((response) => {
      callback(response)
    }).catch((error) => {
      if (errorCallback == null) return
      errorCallback(error)
    });
  }

  update(path, payload, callback, errorCallback = null) {
    return this.service.request({
      method: 'UPDATE',
      url: path,
      responseType: 'json',
      data: payload
    }).then((response) => {
      callback(response)
    }).catch((error) => {
      if (errorCallback == null) return
      errorCallback(error)
    });
  }

  delete(path, callback, errorCallback = null) {
    return this.service.request({
      method: 'DELETE',
      url: path,
      responseType: 'json'
    }).then((response) => {
      callback(response)
    }).catch((error) => {
      if (errorCallback == null) return
      errorCallback(error)
    });
  }
}

export default new Service;