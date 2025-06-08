const { createApp } = Vue;
console.log(Vue);
createApp({
  data() {
    return {
      form: {
        username: '',
        school_email: '',
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
        this.form.phone = data.user.phone;
      } else {
        alert('請先登入');
        window.location.href = '/';
      }
    });
  },
  methods: {
    goToEditProfile() {
        window.location.href = '/edit_profile';
    }
  }
}).mount("#app");
