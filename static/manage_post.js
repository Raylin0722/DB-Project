const { createApp } = Vue;

createApp({
    data() {
        return {
        items: window.pageData.items || [],
        mode: window.pageData.mode || '訪客'
        };
    },
    methods: {
        formatDate(dateStr) {
        if (!dateStr) return '';
        try {
            const date = new Date(dateStr);
            return date.toLocaleString('zh-TW', {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric'
            });
        } catch (e) {
            return dateStr;
        }
        }
    },
    mounted() {
    }
})
// 這裡指定 delimiters
.mount('#post-app');