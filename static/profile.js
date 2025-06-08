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
      posts: window.posts|| [],
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
    isExtendEnabled(p) {
    console.log(p.notified_at)
    return !!p.notified_at;  
    },
    formatDate(dateString) {
      const date = new Date(dateString); 
      const yyyy = date.getUTCFullYear();
      const mm = String(date.getUTCMonth() + 1).padStart(2, '0'); 
      const dd = String(date.getUTCDate()).padStart(2, '0');
      const hh = String(date.getUTCHours()).padStart(2, '0');
      const mi = String(date.getUTCMinutes()).padStart(2, '0');
      const ss = String(date.getUTCSeconds()).padStart(2, '0');
      return `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`;
    },
    extendItem(lost_id) {
      fetch(`/lost_items/${lost_id}/extend`, {
        method: 'POST'
      })
        .then(res => res.json())
        .then(data => {
          alert(data.message);
          if (data.status === 'success') location.reload();
        })
        .catch(err => alert('延長失敗：' + err));
    },
    deleteItem(lost_id) {
      if (!confirm('確定要刪除這筆資料嗎？')) return;

      fetch(`/lost_items/${lost_id}/delete`, {
        method: 'POST'
      })
        .then(res => res.json())
        .then(data => {
          alert(data.message);
          if (data.status === 'success') {
            window.location.href = '/profile';
          }
        })
        .catch(err => alert('刪除失敗：' + err));
    },
    goToEditProfile() {
        window.location.href = '/edit_profile';
    }
  }
}).mount("#app");
