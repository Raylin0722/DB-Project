    const { createApp, ref, onMounted ,computed} = Vue;

    createApp({
      setup() {
        const newPassword = ref('');
        const token = ref('');
        const message = ref('');
        const error = ref(false);
        const resetSuccess = ref(false);

        const showPassword = ref(false);
        const showConfirmPassword = ref(false);


        const confirmPassword = ref('');

        const passwordsMatch = computed(() => {
          return newPassword.value === confirmPassword.value;
        });

        onMounted(() => {
          const urlParams = new URLSearchParams(window.location.search);
          token.value = urlParams.get('token');
          if (!token.value) {
            message.value = "⚠ 缺少驗證參數，請重新點擊信件中的連結";
            error.value = true;
          }
        });

        const passwordValid = computed(() => {
          const value = newPassword.value;
          const hasLetter = /[a-zA-Z]/.test(value);
          const hasNumber = /[0-9]/.test(value);
          const validLength = value.length >= 6 && value.length <= 12;
          return hasLetter && hasNumber && validLength;
        });

        const submitNewPassword = () => {
          message.value = '';
          error.value = false;

          axios.post('/reset-password', {
            token: token.value,
            new_password: newPassword.value
          })
          .then(res => {
            message.value = res.data.message;
            console.log(message.value)
            resetSuccess.value = true;

            // 可選自動跳轉
            // setTimeout(() => window.location.href = "/", 3000);
          })
          .catch(err => {
            message.value = err.response?.data?.message || "⚠ 發生錯誤，請稍後再試";
            console.log(message.value)
            error.value = true;
          });
        };

        return {
          newPassword,
          token,
          message,
          error,
          resetSuccess,
          submitNewPassword,
          passwordValid,
          confirmPassword,
          passwordsMatch,
          showPassword,
          showConfirmPassword
        };
      }
    }).mount("#app");