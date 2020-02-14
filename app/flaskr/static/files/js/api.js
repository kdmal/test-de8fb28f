export default function API()
{
  const INIT = {
    headers: {
      'Content-Type': 'application/json'
    }
  }

  function response(data)
  {
    if (data.status!==200){
      return Promise.reject(
        new Error(`Invalid HTTP status: ${data.status}`)
      );
    }
    return data.json();
  }

  function json(data)
  {
    if ("error" in data){
      return Promise.reject(data);
    }
    return Promise.resolve(data.result);
  }

  function request(endpoint, method, params){
    const args = Object.assign({
      method,
      body: JSON.stringify(params)
    }, INIT);
    return fetch(endpoint, args).then(response).then(json);
  }

  function ping(){
    return request("/ping", "GET");
  }

  function tokens(){
    return request("/tokens", "GET");
  }

  function upload(filename, token, form){
    const args = {
      method: "POST",
      body: form,
      headers:{
        "X-Filename": filename,
        "X-Token": token,
      }
    }
    return fetch("/files/upload", args).then(response).then(json);
  }

  function files(token){
    const args = {
      method: "GET",
      headers:{
        "X-Token": token
      }
    }
    return fetch("/files/upload", args).then(response).then(json);
  }

  function del(token, uuid){
    const args = {
      method: "DELETE",
      headers:{
        "X-Token": token
      }
    }
    return fetch(`/files/upload/${uuid}`, args).then(response).then(json);
  }

  function download(token, uuid){
    const args = {
      method: "GET",
      headers:{
        "X-Token": token
      }
    }
    return fetch(`/files/upload/${uuid}`, args).then(async response=>{
      if (response.status!==200){
        return Promise.reject(
          new Error(`Invalid HTTP status: ${response.status}`)
        );
      }
      const filename = response.headers.get("content-disposition")
          .split(";")
          .find(n=>n.includes("filename="))
          .replace("filename=", "")
          .trim(),
        blob = await response.blob(),
        url = URL.createObjectURL(blob),
        el = document.createElement("a");
      el.href = url;
      el.download = filename;
      el.click();
      el.remove();
      URL.revokeObjectURL(url);
      return Promise.resolve();
    });
  }

  function status(task){
    return request(`/files/status/${task}`, "GET");
  }

  Object.entries({
    request,
    ping,
    tokens,
    upload,
    files,
    del,
    download,
    status,
  }).forEach(([name, foo])=>{
    Object.defineProperty(this, name, { value: foo, writable: false });
  });

  return this;
}
