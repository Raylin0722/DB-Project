const { createApp } = Vue;

// 全域同步用
window.adminType = 'found';

// admin-app：顯示清單
const adminApp = createApp({
    
    data() {
        const urlType = new URLSearchParams(window.location.search).get('type');
        return {
            type: urlType || window.adminType || 'found',
            foundItems: window.pageData.found || [],
            lostItems: window.pageData.lost || [],
            reportItems: window.pageData.report || [], // 新增
            items: (urlType === 'lost')
            ? (window.pageData.lost || [])
            : (urlType === 'report')
                ? (window.pageData.report || [])
                : (window.pageData.found || []),
        };
    },
    methods: {
        switchType(type) {
            this.type = type;
            if (type === 'found') {
                this.items = this.foundItems;
            } else if (type === 'lost') {
                this.items = this.lostItems;
            } else if (type === 'report') {
                this.items = this.reportItems;
            }
            window.adminType = type;
            const params = new URLSearchParams(window.location.search);
            params.set('type', type);
            window.history.replaceState({}, '', `${location.pathname}?${params}`);
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
        },
        
        async deleteItem(id, type) {
            console.log(id, type);
            if (!confirm('確定要刪除這筆資料嗎？')) return;
            let url = type === 'found'
                ? `/adminDelete?target=found&item_id=${id}`
                : `/adminDelete?target=lost&item_id=${id}`;
            try {
                const res = await fetch(url, { method: 'GET' });
                const data = await res.json();
                if (data.success) {
                    alert('刪除成功！');
                    const params = new URLSearchParams(window.location.search);
                    params.set('type', this.type);
                    window.location.search = params.toString();
                    
                } else {
                    alert('刪除失敗：' + (data.error || '未知錯誤'));
                }
            } catch (e) {
                alert('刪除失敗：' + e);
            }
        }
        

    },
    computed: {
        emptyText() {
            if (this.type === 'found') {
                return '暫無拾獲物資訊';
            } else if (this.type === 'lost') {
                return '暫無遺失物資訊';
            } else if (this.type === 'report') {
                return '暫無檢舉資訊';
            }
            return '';
        }
    },
    mounted() {
        if (this.type === 'found') {
            this.items = this.foundItems;
        } else if (this.type === 'lost') {
            this.items = this.lostItems;
        } else if (this.type === 'report') {
            this.items = this.reportItems;
        }
        window.adminAppInstance = this;
        console.log('刷新後當前 type:', this.type); // 新增這行
    }
});
adminApp.mount('#admin-app');

// click-app：只負責按鈕切換
const clickApp = createApp({
    data() {
        const urlType = new URLSearchParams(window.location.search).get('type');
        return {
            type: urlType || window.adminType || 'found'
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