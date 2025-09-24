/**
 * 主訴データのプリロードとキャッシュ管理
 * 全診療科の主訴データを事前に一括取得してローカルストレージに保存
 */

class ChiefComplaintsCache {
    constructor() {
        this.cacheKey = 'persona_chief_complaints_v1';
        this.cacheExpiryKey = 'persona_chief_complaints_expiry';
        this.cacheDuration = 24 * 60 * 60 * 1000; // 24時間
        this.cache = {};
    }

    /**
     * キャッシュが有効かチェック
     */
    isCacheValid() {
        const expiry = localStorage.getItem(this.cacheExpiryKey);
        if (!expiry) return false;
        return Date.now() < parseInt(expiry);
    }

    /**
     * ローカルストレージからキャッシュをロード
     */
    loadFromStorage() {
        try {
            if (this.isCacheValid()) {
                const cached = localStorage.getItem(this.cacheKey);
                if (cached) {
                    this.cache = JSON.parse(cached);
                    console.log('[Cache] Loaded chief complaints from localStorage');
                    return true;
                }
            }
        } catch (e) {
            console.error('[Cache] Failed to load from localStorage:', e);
        }
        return false;
    }

    /**
     * キャッシュをローカルストレージに保存（セキュリティ強化版）
     */
    saveToStorage() {
        try {
            // データサイズ制限（5MB）
            const dataStr = JSON.stringify(this.cache);
            if (dataStr.length > 5 * 1024 * 1024) {
                console.warn('[Cache] Data too large for localStorage, truncating...');
                // 古いデータから削除
                const keys = Object.keys(this.cache);
                while (dataStr.length > 5 * 1024 * 1024 && keys.length > 0) {
                    delete this.cache[keys.pop()];
                }
            }
            
            // データ整合性チェック
            if (!this.validateCacheData(this.cache)) {
                console.error('[Cache] Invalid cache data detected, aborting save');
                return;
            }
            
            localStorage.setItem(this.cacheKey, JSON.stringify(this.cache));
            localStorage.setItem(this.cacheExpiryKey, (Date.now() + this.cacheDuration).toString());
            console.log('[Cache] Saved chief complaints to localStorage');
        } catch (e) {
            console.error('[Cache] Failed to save to localStorage:', e);
            // クォータエラーの場合は古いデータをクリア
            if (e.name === 'QuotaExceededError') {
                this.clearOldData();
            }
        }
    }
    
    /**
     * キャッシュデータの検証
     */
    validateCacheData(data) {
        // 基本的なデータ構造検証
        if (typeof data !== 'object' || data === null) return false;
        
        for (const [key, value] of Object.entries(data)) {
            // キー形式の検証（category_department）
            if (!key.includes('_')) return false;
            
            // 値の検証（配列であること）
            if (!Array.isArray(value)) return false;
            
            // 各要素が文字列であること
            if (!value.every(item => typeof item === 'string')) return false;
            
            // XSS対策：危険な文字列のチェック
            if (value.some(item => this.containsDangerousContent(item))) {
                console.warn('[Cache] Dangerous content detected in cache data');
                return false;
            }
        }
        return true;
    }
    
    /**
     * 危険なコンテンツのチェック
     */
    containsDangerousContent(str) {
        // 基本的なXSSパターンのチェック
        const dangerousPatterns = [
            /<script/i,
            /<iframe/i,
            /javascript:/i,
            /on\w+\s*=/i,  // onclick=, onerror= など
            /<img.*?onerror/i
        ];
        
        return dangerousPatterns.some(pattern => pattern.test(str));
    }
    
    /**
     * 古いキャッシュデータのクリア
     */
    clearOldData() {
        try {
            // localStorage内の古いデータを探してクリア
            const keysToRemove = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith('persona_') && key !== this.cacheKey && key !== this.cacheExpiryKey) {
                    keysToRemove.push(key);
                }
            }
            
            keysToRemove.forEach(key => localStorage.removeItem(key));
            console.log(`[Cache] Cleared ${keysToRemove.length} old cache entries`);
        } catch (e) {
            console.error('[Cache] Failed to clear old data:', e);
        }
    }

    /**
     * 特定の診療科の主訴を取得
     */
    get(category, department) {
        return this.cache[`${category}_${department}`] || null;
    }

    /**
     * 特定の診療科の主訴を設定
     */
    set(category, department, complaints) {
        this.cache[`${category}_${department}`] = complaints;
    }

    /**
     * 全診療科の主訴を一括プリロード（最適化版）
     */
    async preloadAll() {
        // まずローカルストレージから読み込み試行
        if (this.loadFromStorage()) {
            return true;
        }

        console.log('[Cache] Preloading all chief complaints...');
        
        // 優先度の高い診療科から段階的にロード
        const priorityDepartments = {
            medical: ['内科', '外科', '小児科', '整形外科', '皮膚科'], // よく使われる診療科
            dental: ['一般歯科']
        };
        
        const remainingDepartments = {
            medical: ['眼科', '耳鼻咽喉科', '泌尿器科', '婦人科', '精神科', '循環器内科', '消化器内科', '呼吸器内科', '神経内科', '血液内科', '腎臓内科', '糖尿病内科', '内分泌科', '形成外科', '美容外科', '脳神経外科'],
            dental: ['矯正歯科', '小児歯科', '口腔外科', '審美歯科'],
            others: ['リハビリテーション科', 'アレルギー科', '放射線科', '麻酔科']
        };
        
        // バッチサイズを設定（同時リクエスト数を制限）
        const batchSize = 5;
        const delay = 100; // バッチ間の遅延（ミリ秒）
        
        // バッチ処理関数
        const processBatch = async (items) => {
            const promises = items.map(({ category, dept }) =>
                fetch(`/api/chief-complaints/${category}/${encodeURIComponent(dept)}`)
                    .then(res => {
                        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                        return res.json();
                    })
                    .then(data => {
                        this.set(category, dept, data.chief_complaints);
                    })
                    .catch(err => {
                        console.error(`[Cache] Failed to load ${category}/${dept}:`, err);
                    })
            );
            
            await Promise.allSettled(promises);
        };
        
        // 優先度の高い診療科を先にロード
        const priorityItems = [];
        for (const [category, depts] of Object.entries(priorityDepartments)) {
            for (const dept of depts) {
                priorityItems.push({ category, dept });
            }
        }
        
        // 優先度の高いものを処理
        for (let i = 0; i < priorityItems.length; i += batchSize) {
            const batch = priorityItems.slice(i, i + batchSize);
            await processBatch(batch);
        }
        
        // 中間保存（優先度の高いデータを先に保存）
        this.saveToStorage();
        
        // 残りの診療科をバックグラウンドで処理
        const remainingItems = [];
        for (const [category, depts] of Object.entries(remainingDepartments)) {
            if (depts) {
                for (const dept of depts) {
                    remainingItems.push({ category, dept });
                }
            }
        }
        
        // 残りをバッチ処理（遅延を入れてサーバー負荷を軽減）
        for (let i = 0; i < remainingItems.length; i += batchSize) {
            const batch = remainingItems.slice(i, i + batchSize);
            await processBatch(batch);
            
            // 次のバッチまで少し待機
            if (i + batchSize < remainingItems.length) {
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        
        // 最終保存
        this.saveToStorage();
        
        console.log('[Cache] Preload completed');
        return true;
    }

    /**
     * キャッシュをクリア
     */
    clear() {
        this.cache = {};
        localStorage.removeItem(this.cacheKey);
        localStorage.removeItem(this.cacheExpiryKey);
    }
}

// グローバルインスタンスを作成
window.chiefComplaintsCache = new ChiefComplaintsCache();

// DOMContentLoadedで自動プリロード
document.addEventListener('DOMContentLoaded', () => {
    // 即座にプリロード開始（UIをブロックしない）
    requestIdleCallback(() => {
        window.chiefComplaintsCache.preloadAll().catch(err => {
            console.error('[Cache] Preload failed:', err);
        });
    }, { timeout: 2000 }); // 最大2秒以内に開始
});