const { createApp } = Vue;

createApp({
  data() {
    return {
      form: {
        item_name: '',
        category: '',
        found_campus: '',
        found_location: '',
        found_time: '',
        storage_location: '',
        contact_phone: '',
        contact_email: '',
        image_url: '',
        remark: '',
        user_id: null
      },
      campusOptions: [],
      locationOptions: [],
      locationMap: {},
      selectedCampus: '',
      user: null,
      imageFile: null,
      statusMessage: '',
      statusClass: ''
    };
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
    handleImageChange(e) {
      this.imageFile = e.target.files[0];
    },
    async uploadImageToCloudinary() {
      if (!this.imageFile) return null;

      const formData = new FormData();
      formData.append('file', this.imageFile);
      formData.append('upload_preset', 'found_items'); 

      const res = await fetch('https://api.cloudinary.com/v1_1/dpnwrye7n/image/upload', {
        method: 'POST',
        body: formData
      });
      const result = await res.json();
      return result.secure_url;
    },
    async submitForm() {
      if (!this.isRequiredFieldsFilled) {
        this.statusMessage = '⚠ 請填寫所有必填欄位';
        this.statusClass = 'alert-warning';
        return;
      }
      if (!this.isFoundTimeValid) {
        this.statusMessage = '⚠ 拾獲時間不能是未來時間';
        this.statusClass = 'alert-warning';
        return;
      }
      try {
        const imageUrl = await this.uploadImageToCloudinary();
        this.form.image_url = imageUrl;

        const response = await fetch('/found_items/create', {
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
          console.error('[後端錯誤]', result.error);
        }
      } catch (error) {
        this.statusMessage = '❌ 系統發生錯誤，請稍後再試';
        this.statusClass = 'alert-danger';
        console.error('[前端錯誤]', error);
      }
    },
    resetForm() {
      this.form = {
        item_name: '',
        category: '',
        found_campus: '',
        found_location: '',
        found_time: '',
        storage_location: '',
        contact_phone: this.user?.phone || '',
        contact_email: this.user?.school_email || '',
        image_url: '',
        remark: '',
        user_id: this.user?.user_id || null
      };
      this.imageFile = null;
    }
  },
  computed: {
    isRequiredFieldsFilled() {
      const f = this.form;
      return [f.item_name, f.category, f.found_campus, f.found_location, f.found_time, f.storage_location]
        .every(v => v && v.toString().trim() !== '');
    },
    isFoundTimeValid() {
      const t = this.form.found_time;
      return !t || new Date(t) <= new Date();
    }
  },
  watch: {
    selectedCampus(newCampus) {
      this.locationOptions = this.locationMap[newCampus] || [];
      this.form.found_campus = newCampus;
      this.form.found_location = '';
    }
  }
}).mount('#app');
