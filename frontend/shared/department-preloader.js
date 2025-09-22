/**
 * 診療科選択時の主訴データ先読み機能
 * ユーザーが診療科を選択した瞬間に、その診療科の主訴データを事前取得
 */

class DepartmentPreloader {
    constructor() {
        this.preloadedDepartments = new Set();
        this.preloadingPromises = new Map();
    }

    /**
     * 診療科のマッピング情報を取得
     */
    getDepartmentInfo(departmentValue) {
        // 各ページのマッピングを統合
        const mappings = {
            // 医科（日本語名をvalueとして使用する場合）
            '眼科': { category: 'medical', name: '眼科' },
            '内科': { category: 'medical', name: '内科' },
            '外科': { category: 'medical', name: '外科' },
            '小児科': { category: 'medical', name: '小児科' },
            '整形外科': { category: 'medical', name: '整形外科' },
            '耳鼻咽喉科': { category: 'medical', name: '耳鼻咽喉科' },
            '皮膚科': { category: 'medical', name: '皮膚科' },
            '婦人科': { category: 'medical', name: '婦人科' },
            '泌尿器科': { category: 'medical', name: '泌尿器科' },
            '循環器内科': { category: 'medical', name: '循環器内科' },
            '消化器内科': { category: 'medical', name: '消化器内科' },
            '呼吸器内科': { category: 'medical', name: '呼吸器内科' },
            '糖尿病内科': { category: 'medical', name: '糖尿病内科' },
            '腎臓内科': { category: 'medical', name: '腎臓内科' },
            '神経内科': { category: 'medical', name: '神経内科' },
            '内分泌科': { category: 'medical', name: '内分泌科' },
            '血液内科': { category: 'medical', name: '血液内科' },
            '脳神経外科': { category: 'medical', name: '脳神経外科' },
            '形成外科': { category: 'medical', name: '形成外科' },
            '美容外科': { category: 'medical', name: '美容外科' },
            
            // 歯科（日本語名をvalueとして使用する場合）
            '一般歯科': { category: 'dental', name: '一般歯科' },
            '小児歯科': { category: 'dental', name: '小児歯科' },
            '矯正歯科': { category: 'dental', name: '矯正歯科' },
            '審美歯科': { category: 'dental', name: '審美歯科' },
            '口腔外科': { category: 'dental', name: '口腔外科' },

            // その他（日本語名をvalueとして使用する場合）
            '精神科': { category: 'others', name: '精神科' },
            '麻酔科': { category: 'others', name: '麻酔科' },
            'リハビリテーション科': { category: 'others', name: 'リハビリテーション科' },
            'アレルギー科': { category: 'others', name: 'アレルギー科' },
            
        };
        
        return mappings[departmentValue] || null;
    }

    /**
     * 診療科の主訴データを先読み
     */
    async preloadDepartment(departmentValue) {
        // 既に読み込み済みまたは読み込み中の場合はスキップ
        if (this.preloadedDepartments.has(departmentValue)) {
            console.log(`[Preload] ${departmentValue} already preloaded`);
            return;
        }
        
        if (this.preloadingPromises.has(departmentValue)) {
            console.log(`[Preload] ${departmentValue} already preloading`);
            return this.preloadingPromises.get(departmentValue);
        }
        
        const info = this.getDepartmentInfo(departmentValue);
        if (!info) {
            console.error(`[Preload] Unknown department: ${departmentValue}`);
            return;
        }
        
        console.log(`[Preload] Starting preload for ${departmentValue} (${info.name})`);
        
        // グローバルキャッシュが既に持っている場合はスキップ
        if (window.chiefComplaintsCache) {
            const cached = window.chiefComplaintsCache.get(info.category, info.name);
            if (cached) {
                console.log(`[Preload] ${departmentValue} already in global cache`);
                this.preloadedDepartments.add(departmentValue);
                return;
            }
        }
        
        // 非同期で先読み開始
        const promise = this.fetchAndCache(info.category, info.name, departmentValue);
        this.preloadingPromises.set(departmentValue, promise);
        
        try {
            await promise;
            this.preloadedDepartments.add(departmentValue);
            this.preloadingPromises.delete(departmentValue);
            console.log(`[Preload] Completed preload for ${departmentValue}`);
        } catch (error) {
            console.error(`[Preload] Failed to preload ${departmentValue}:`, error);
            this.preloadingPromises.delete(departmentValue);
            
            // ユーザー向けの軽微な通知（実装されている場合）
            if (window.showNotification) {
                window.showNotification('診療科データの準備中です...', 'info');
            }
        }
    }

    /**
     * APIから取得してキャッシュに保存
     */
    async fetchAndCache(category, departmentName, departmentValue) {
        const apiUrl = `/api/chief-complaints/${category}/${encodeURIComponent(departmentName)}`;
        
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // グローバルキャッシュに保存
        if (window.chiefComplaintsCache) {
            window.chiefComplaintsCache.set(category, departmentName, data.chief_complaints);
            // LocalStorageにも保存
            window.chiefComplaintsCache.saveToStorage();
        }
        
        return data.chief_complaints;
    }

    /**
     * 診療科選択のイベントリスナーを設定
     */
    setupPreloadListeners() {
        // ラジオボタンの変更を監視
        document.addEventListener('change', (event) => {
            const target = event.target;
            
            // 診療科選択のラジオボタンかチェック
            if (target.type === 'radio' && target.name === 'department') {
                const departmentValue = target.value;
                console.log(`[Preload] Department selected: ${departmentValue}`);
                
                // 非同期で先読み開始（UIをブロックしない）
                requestIdleCallback(() => {
                    this.preloadDepartment(departmentValue).catch(err => {
                        console.error('[Preload] Error:', err);
                    });
                }, { timeout: 500 }); // 500ms以内に開始
            }
        });
        
        // ホバー時の先読み（より積極的）
        document.addEventListener('mouseover', (event) => {
            const label = event.target.closest('label');
            if (label) {
                const radio = label.querySelector('input[type="radio"][name="department"]');
                if (radio) {
                    const departmentValue = radio.value;
                    
                    // デバウンス処理（連続ホバーを防ぐ）
                    if (!this.hoverTimeout) {
                        this.hoverTimeout = setTimeout(() => {
                            requestIdleCallback(() => {
                                this.preloadDepartment(departmentValue).catch(err => {
                                    console.error('[Preload] Hover preload error:', err);
                                });
                            }, { timeout: 1000 });
                            this.hoverTimeout = null;
                        }, 500); // 500ms以上ホバーしたら先読み（医療系ユーザーの慎重な操作を考慮）
                    }
                }
            }
        });
        
        // ホバー解除時のタイムアウトクリア
        document.addEventListener('mouseout', (event) => {
            if (this.hoverTimeout) {
                clearTimeout(this.hoverTimeout);
                this.hoverTimeout = null;
            }
        });
    }
}

// グローバルインスタンスを作成
window.departmentPreloader = new DepartmentPreloader();

// DOMContentLoadedで自動セットアップ
document.addEventListener('DOMContentLoaded', () => {
    window.departmentPreloader.setupPreloadListeners();
    console.log('[Preload] Department preloader initialized');
});