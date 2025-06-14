const { createApp } = Vue;

createApp({
  data() {
    return {
      form: {
        item_name: '',
        category: '',
        lost_campus:'',
        lost_location: '',
        lost_time: '',
        contact_phone: '',
        contact_email: '',
        notification_period: null,
        remark: '',
        // user_id: localStorage.getItem('user_id')
        user_id: null 
      },
      campusOptions: [],
      locationOptions: [],
      locationMap: {},
      selectedCampus: '',
      user: null, 
      statusMessage: '',
      statusClass: '',
      isSubmitting: false,
    }
  },
  mounted() {
    fetch('/static/locations.json')
      .then(res => res.json())
      .then(data => {
        this.locationMap = data;
        this.campusOptions = Object.keys(data);
    });
    fetch('/me')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          this.user = data.user;
          this.form.user_id = data.user.user_id;  
          this.form.contact_email = data.user.school_email;
          this.form.contact_phone = data.user.phone;
        } else {
          alert('請先登入');
          window.location.href = '/';
        }
    });
  },
  methods: {
    goBack() {
      window.location = document.referrer || '/browse'; 
    },
    async submitForm() {
      
      this.statusMessage = '';
      this.statusClass = '';

    if (!this.isRequiredFieldsFilled) {
      this.statusMessage = '⚠ 請填寫所有必填欄位';
      this.statusClass = 'alert-warning';
      return;
    }
    if (!this.isLostTimeValid) {
      this.statusMessage = '⚠ 遺失時間不能是未來時間';
      this.statusClass = 'alert-warning';
      return;
    }

    if (this.isSubmitting) return; // 防止連點
    this.isSubmitting = true;      // 設定為送出中
    try {
        const response = await fetch('/lost_items/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });
        const result = await response.json();
        if (response.ok) {
          this.statusMessage = '✅ 發布成功！2 秒後將返回...';
          this.statusClass = 'alert-success';
          this.resetForm();

          setTimeout(() => {
            window.history.back();
          }, 2000);
        } else {
          this.statusMessage = '❌ 系統發生錯誤，請稍後再試';
          this.statusClass = 'alert-danger';
          console.error('[後端ㄉ錯誤]', result.error); 
        }
      } catch (error) {
        this.statusMessage = '❌ 系統發生錯誤，請稍後再試';
        this.statusClass = 'alert-danger';
        console.error('[前端ㄉ錯誤]', error);
      }
  },
    resetForm() {
      this.form = {
        item_name: '',
        category: '',
        lost_campus:'',
        lost_location: '',
        lost_time: '',
        contact_phone: this.user?.phone || '',
        contact_email: this.user?.school_email || '',
        notification_period: null,
        remark: '',
        user_id:this.user?.user_id || null
      };
    }
  },
  
  computed: {
    isRequiredFieldsFilled() {
      const f = this.form;
      return [f.item_name, f.category, f.lost_campus,f.lost_location, f.lost_time, f.contact_email]
      .every(v => v && v.toString().trim() !== '');
    },
    isLostTimeValid() {
      const t = this.form.lost_time;
      return !t || new Date(t) <= new Date(); 
    }
  },
  watch: {
    selectedCampus(newCampus) {
      this.locationOptions = this.locationMap[newCampus] || [];
      this.form.lost_campus = newCampus;  
      this.form.lost_location = '';  
    },
  }
}).mount('#app');
