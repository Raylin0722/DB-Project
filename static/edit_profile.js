const { createApp } = Vue;
console.log(Vue);
createApp({
  data() {
    return {
      form: {
        username: '',
        school_email: '',
        department: '',
        phone: ''
      },
      successMsg: '',
      errorMsg: ''
    };
  },
  mounted() {
    fetch('/me')
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        this.user = data.user;
        this.form.username = data.user.username;
        this.form.school_email = data.user.school_email;
        this.form.department = data.user.department;
        this.form.phone = data.user.phone;
      } else {
        alert('請先登入');
        window.location.href = '/';
      }
    });
  },
  methods: {
    submitEdit() {
        axios.post('/check_edit_profile', this.form)
          .then(res => {
            this.successMsg = res.data.message;
            this.errorMsg = '';
      
            setTimeout(() => {
                window.location.href = '/profile';  // 例如導回個人檔案
              }, 2000);              
          })
          .catch(err => {
            this.errorMsg = err.response?.data?.message || '更新失敗';
            this.successMsg = '';
          });
      }
      
  }
}).mount("#app");
