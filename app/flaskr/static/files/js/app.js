import Vue from "/static/js/vue.esm.browser.min.js";
import API from "./api.js";

const api = new API();

window.api = api;

new Vue({
  el: "#app",
  data:{
    tokens: [],
    files: [],
    token: null,
    file: null,
    lock:{
      upload: false,
    }
  },

  watch:{
    token(val){
      api.files(this.token).then(data=>{
        this.files = data;
      });
    }
  },

  methods:{
    upload(){
      const form = new FormData();
      form.append("file", this.file.files[0]);
      if (this.lock.upload) return;
      this.lock.upload = true;
      api.upload(this.file.value, this.token, form).then(data=>{
        this.files.push(data);
        this.file.value = null;
        this.wait(data);
      }).finally(()=>{
        this.lock.upload = false;
      });
    },
    del(file){
        api.del(this.token, file.uuid).then(()=>{
            this.files = this.files.filter(x=>x.uuid!==file.uuid);
        });
    },
    download(file){
        api.download(this.token, file.uuid).then(data=>{
            console.log(data);
        });
    },
    wait(file){
      const that = this;
      api.status(file.task).then(data=>{
        file.status = data;
        if (data==="PENDING"){
          setTimeout(()=>that.wait(file), 1e3);
          return;
        }
      });
    }
  },

  created(){
    api.tokens().then(data=>{
      this.tokens = data;
      this.token = this.tokens[0];
    });
  }
});
