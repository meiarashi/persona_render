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
            // 医科
            'ophthalmology': { category: 'medical', name: '眼科' },
            'internal_medicine': { category: 'medical', name: '内科' },
            'surgery': { category: 'medical', name: '外科' },
            'pediatrics': { category: 'medical', name: '小児科' },
            'orthopedics': { category: 'medical', name: '整形外科' },
            'otorhinolaryngology': { category: 'medical', name: '耳鼻咽喉科' },
            'dermatology': { category: 'medical', name: '皮膚科' },
            'gynecology': { category: 'medical', name: '婦人科' },
            'urology': { category: 'medical', name: '泌尿器科' },
            'cardiology': { category: 'medical', name: '循環器内科' },
            'gastroenterology': { category: 'medical', name: '消化器内科' },
            'respiratory_medicine': { category: 'medical', name: '呼吸器内科' },
            'diabetes_medicine': { category: 'medical', name: '糖尿病内科' },
            'nephrology': { category: 'medical', name: '腎臓内科' },
            'neurology': { category: 'medical', name: '神経内科' },
            'endocrinology': { category: 'medical', name: '内分泌科' },
            'hematology': { category: 'medical', name: '血液内科' },
            'neurosurgery': { category: 'medical', name: '脳神経外科' },
            'plastic_surgery': { category: 'medical', name: '形成外科' },
            'beauty_surgery': { category: 'medical', name: '美容外科' },

            // 歯科
            'general_dentistry': { category: 'dental', name: '一般歯科' },
            'pediatric_dentistry': { category: 'dental', name: '小児歯科' },
            'orthodontics': { category: 'dental', name: '矯正歯科' },
            'cosmetic_dentistry': { category: 'dental', name: '審美歯科' },
            'oral_surgery': { category: 'dental', name: '口腔外科' },

            // その他
            'psychiatry': { category: 'others', name: '精神科' },
            'anesthesiology': { category: 'others', name: '麻酔科' },
            'rehabilitation': { category: 'others', name: 'リハビリテーション科' },
            'allergy': { category: 'others', name: 'アレルギー科' },
            'radiology': { category: 'others', name: '放射線科' },
            
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