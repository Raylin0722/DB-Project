const { createApp } = Vue;
createApp({
    mounted() {
      fetch('/static/departments.json')
        .then(res => res.json())
        .then(data => {
          this.departments = data;
        });
    },
    data() {
        return {
            loginPasswordVisible: false,
            registerPasswordVisible: false,
            guestMode: false,
            showLogin: true,
            loggedIn: false,
            userInfo: {},
            loginForm: {
                school_email: '',
                password: ''
            },
            registerForm: {
                username: '',
                school_email: '',
                password: '',
                department: '',
                phone: ''
            },
            showDeptDropdown: false,
            departments: [],
            loginMessage: '',
            registerMessage: '',
            forgotEmail: '',
            forgotMessage: '',
            forgotError: '',
            showForgot: false,
            confirmPassword: '',
            confirmPasswordVisible: false,
        }
    },
    methods: {
        selectDepartment(dept) {
          this.registerForm.department = dept;
          this.showDeptDropdown = false;
        },
        switchToRegister() {
            this.showLogin = false;
            this.clearForgotForm();
            this.clearLoginForm();
            this.loginMessage = '';
        },
        switchToLogin() {
            this.showLogin = true;
            this.clearForgotForm();
            this.clearRegisterForm();
            this.registerMessage = '';
        },
        clearLoginForm() {
            this.loginForm.school_email = '';
            this.loginForm.password = '';
            this.loginPasswordVisible = false;
        },
        clearRegisterForm() {
            this.registerForm.username = '';
            this.registerForm.school_email = '';
            this.registerForm.password = '';
            this.registerForm.department = '';
            this.registerForm.phone = '';
            this.registerPasswordVisible = false;
            this.confirmPassword= '';
            this.showDeptDropdown = false;
        },
        clearForgotForm() {
            this.showForgot = !this.showForgot,
            this.forgotMessage = '',
            this.forgotError = ''
        },
        handleLogin() {
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.loginForm)
            })
            .then(async res => {
                const text = await res.text();
                try {
                    const data = JSON.parse(text);
                    this.loginMessage = data.message;
                    if (data.status === 'success') {
                        this.loggedIn = true;
                        this.userInfo = data.user;
                    }
                } catch (e) {
                    console.error('回傳不是 JSON：', text);
                    this.loginMessage = '伺服器回傳錯誤（不是 JSON）';
                }
            });
                },
        handleRegister() {
            if (!this.passwordsMatch) {
                this.registerMessage = "兩次輸入的密碼不一致";
                return;
            }
            if (!this.passwordLengthValid) {
                this.registerMessage = "密碼長度需為 6 到 12 個字元";
                return;
            }
        
            if (!this.passwordHasLetter || !this.passwordHasNumber) {
                this.registerMessage = "密碼需包含英文字母與數字";
                return;
            }
        
            if (!this.emailValid) {
                this.registerMessage = "請輸入有效的 Email 格式";
                return;
            }
        
            // 送出註冊
        fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.registerForm)
            })
            .then(res => res.json())
            .then(data => {
                this.registerMessage = data.message;
                if (data.status === 'success') {
                    
                }
            });
        },
        goToBrowse() {
          const mode = this.loggedIn ? 'user' : (this.guestMode ? 'guest' : 'unknown');
          window.location.href = `/browse?mode=${mode}`;
        },

        logout() {
            this.loggedIn = false;
            this.clearLoginForm();
            this.loginMessage = '';
            this.guestMode = false;
        },
        guestLogin() {
            this.guestMode = true;
        },
        guestLogout() {
            this.switchToLogin() 
            this.showForgot = !this.showForgot
            this.guestMode = false;
        },
        sendForgotEmail() {
            this.forgotMessage = ''
            this.forgotError = ''
            if (!this.forgotEmail) {
              this.forgotError = '請輸入信箱'
              return
            }
        
            axios.post('/forgot-password', {
              school_email: this.forgotEmail
            })
            .then(res => {
              this.forgotMessage = res.data.message
            })
            .catch(err => {
              this.forgotError = err.response?.data?.message || '發生錯誤'
            })
          }
      
    },
    computed: {
        passwordsMatch() {
          return this.registerForm.password === this.confirmPassword;
        },
        emailValid() {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(this.registerForm.school_email);
        },
        passwordHasLetter() {
            return /[A-Za-z]/.test(this.registerForm.password);
        },
        passwordHasNumber() {
            return /\d/.test(this.registerForm.password);
        },
        passwordLengthValid() {
            const len = this.registerForm.password.length;
            return len >= 6 && len <= 12;
        },
        passwordValid() {
            return this.passwordHasLetter && this.passwordHasNumber && this.passwordLengthValid;
        }    
    }
}).mount('#app');