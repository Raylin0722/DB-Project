const { createApp } = Vue;

// 全域同步用
window.adminType = 'found';

// admin-app：顯示清單
const adminApp = createApp({
    data() {
        return {
            type: window.adminType,
            foundItems: window.pageData.found || [],
            lostItems: window.pageData.lost || [],
            items: window.pageData.found || [],
        };
    },
    methods: {
        switchType(type) {
            this.type = type;
            this.items = type === 'found' ? this.foundItems : this.lostItems;
            window.adminType = type;
            // 同步 click-app
            if (window.clickAppInstance) {
                window.clickAppInstance.type = type;
            }
            console.log(`ADMIN:Switched to ${type} items`);
        },
        formatDate(dateStr) {
            if (!dateStr) return '';
            try {
                const date = new Date(dateStr.replace(' ', 'T'));
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
    computed: {
        emptyText() {
            return this.type === 'found' ? '暫無拾獲物資訊' : '暫無遺失物資訊';
        }
    },
    mounted() {
        this.items = this.foundItems;
        window.adminAppInstance = this;
    }
});
adminApp.mount('#admin-app');

// click-app：只負責按鈕切換
const clickApp = createApp({
    data() {
        return {
            type: window.adminType
        };
    },
    methods: {
        switchType(type) {
            this.type = type;
            window.adminType = type;
            // 同步 admin-app
            if (window.adminAppInstance) {
                window.adminAppInstance.switchType(type);
            }
            console.log(`CLICK:Switched to ${type} items`);
        }
    }
});
window.clickAppInstance = clickApp.mount('#click-app');