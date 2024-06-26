import axios from 'axios'

class Service {
  constructor() {
    let baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL
    if (typeof window !== 'undefined') {
      baseUrl = 'http://' + window.location.hostname + ':8000/api'
    }
    let service = axios.create({
      baseURL: baseUrl,
    })
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
    return response
  }

  handleError = (error) => {
    console.error(error)
    let callbackUrl
    switch (error.response.status) {
      case 400:
        console.error(error)
        break
      case 401:
        callbackUrl = document.location
        this.redirectTo(document, '/signin?callbackUrl=' + callbackUrl)
        break
      case 403:
        callbackUrl = document.location
        //this.redirectTo(document, '/signin?callbackUrl=' + callbackUrl)
        break
      case 404:
        console.error(error)
        //this.redirectTo(document, '/404')
        break
      default:
        console.error(error)
        //this.redirectTo(document, '/500')
        break
    }
    return Promise.reject(error)
  }

  redirectTo = (document, path) => {
    document.location = path
  }

  get(path, callback, errorCallback) {
    return this.service
      .get(path)
      .then((response) => callback(response))
      .catch(errorCallback)
  }

  getFile(path, callback) {
    let baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL
    if (typeof window !== 'undefined') {
      baseUrl = 'http://' + window.location.hostname + ':8000/api'
    }
    let service = axios.create({
      baseURL: baseUrl,
      responseType: 'arraybuffer',
    })
    service.interceptors.response.use(this.handleSuccess, this.handleError)
    service.interceptors.request.use(function (config) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Token ${token}`
      }
      return config
    })
    return service.get(path).then((response) => callback(response))
  }

  getFileBlob(path, callback) {
    let baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL
    if (typeof window !== 'undefined') {
      baseUrl = 'http://' + window.location.hostname + ':8000/api'
    }
    let service = axios.create({
      baseURL: baseUrl,
      responseType: 'blob',
    })
    service.interceptors.response.use(this.handleSuccess, this.handleError)
    service.interceptors.request.use(function (config) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Token ${token}`
      }
      return config
    })
    return service.get(path).then((response) => {
      callback(response)
    })
  }

  patch(path, payload, callback, errorCallback) {
    return this.service
      .request({
        method: 'PATCH',
        url: path,
        responseType: 'json',
        data: payload,
      })
      .then((response) => callback(response))
      .catch((error) => {
        if (errorCallback == null) return
        errorCallback(error)
      })
  }

  post(path, payload, callback, errorCallback, headers, extraArgs = {}) {
    return this.service
      .request({
        method: 'POST',
        url: path,
        responseType: 'json',
        data: payload,
        headers,
        ...extraArgs,
      })
      .then((response) => {
        callback(response)
      })
      .catch((error) => {
        if (errorCallback == null) return
        errorCallback(error)
      })
  }

  put(path, payload, callback, errorCallback = null) {
    return this.service
      .request({
        method: 'PUT',
        url: path,
        responseType: 'json',
        data: payload,
      })
      .then((response) => {
        callback(response)
      })
      .catch((error) => {
        if (errorCallback == null) return
        errorCallback(error)
      })
  }

  update(path, payload, callback, errorCallback = null) {
    return this.service
      .request({
        method: 'UPDATE',
        url: path,
        responseType: 'json',
        data: payload,
      })
      .then((response) => {
        callback(response)
      })
      .catch((error) => {
        if (errorCallback == null) return
        errorCallback(error)
      })
  }

  delete(path, callback, errorCallback = null) {
    return this.service
      .request({
        method: 'DELETE',
        url: path,
        responseType: 'json',
      })
      .then((response) => {
        callback(response)
      })
      .catch((error) => {
        if (errorCallback == null) return
        errorCallback(error)
      })
  }
}

export default new Service()
