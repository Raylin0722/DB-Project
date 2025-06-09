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
        cloudinary_id: '',
        remark: '',
        user_id: null
      },
      imagePreview: null,
      campusOptions: [],
      locationOptions: [],
      locationMap: {},
      selectedCampus: '',
      user: null,
      imageFile: null,
      statusMessage: '',
      statusClass: '',
      isSubmitting: false,
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
    triggerFileSelect() {
      this.$refs.fileInput.click();
    },
    handleImageChange(event) {
      const file = event.target.files[0];
      if (file && file.type.startsWith("image/")) {

        this.imageFile = file;
      
        const reader = new FileReader();
        reader.onload = (e) => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    handleDrop(event) {
      const file = event.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        this.imagePreview = URL.createObjectURL(file);
      }
    },
    removeImage() {
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview);
        this.imagePreview = null;
      }
      this.$refs.fileInput.value = '';
    },
    goBack() {
      window.location = document.referrer || '/browse'; 
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
      return {
        image_url: result.secure_url,
        cloudinary_id: result.public_id
      };
    },
    async submitForm() {
      
      this.statusMessage = '';
      this.statusClass = '';
      
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

      if (this.isSubmitting) return; // 防止連點
      this.isSubmitting = true;      // 設定為送出中

      try {
        if (this.imageFile) {
          const uploadResult = await this.uploadImageToCloudinary();
          if (!uploadResult) {
            this.statusMessage = '❌ 圖片上傳失敗，請重試';
            this.statusClass = 'alert-danger';
            this.isSubmitting = false;
            return;
          }
          this.form.image_url = uploadResult.image_url;
          this.form.cloudinary_id = uploadResult.cloudinary_id;
        } else {
          this.form.image_url = null;
          this.form.cloudinary_id = null;
        }

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
        cloudinary_id: '',
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
